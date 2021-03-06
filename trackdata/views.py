import time
import datetime
import pytz

from dateutil.relativedelta import relativedelta

from django.views.decorators.cache import cache_page

from django.conf import settings
from django.template import Context
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from django.db import connection
from django.db.models import Count
from django.utils import simplejson

import rcstats.utils as utils
import rcstats.rcdata.result_history_queries as result_history
from rcstats.ranking.views import get_ranked_classes_by_track
from rcstats.ranking.models import RankedClass
from rcstats.rcdata.models import SupportedTrackName, SingleRaceDetails, SingleRaceResults

@cache_page(60 * 60)
def trackdata(request):
    """
    This view will display a list of the supported race tracks. It
    is the main entry point for the track specific scenario. 
    
    This is not a raw view of all POSSIBLE tracks, just a set that
    has been manually selected by an admin.
    """
    tracklist = SupportedTrackName.objects.all()

    detailed_trackdata = []
    
    # Lookup the metadata for each of the supported tracks.
    for track in tracklist:
        temp_data = {}
        temp_data['id'] = track.id
        temp_data['trackname'] = track.trackkey.trackname
        temp_data['racecount'] = 0
        temp_data['recent_racedate'] = None
        
        # Get the number of racing currently in the system.
        racecount = SingleRaceDetails.objects.filter(trackkey=track.trackkey.id).count()
        temp_data['racecount'] = racecount
        # Get the most recent race date
        recent_racedate = SingleRaceDetails.objects.filter(trackkey=track.trackkey.id).order_by('-racedate')[:1]
        if recent_racedate:
            temp_data['recent_racedate'] = recent_racedate.get().racedate
            
        detailed_trackdata.append(temp_data)
                

    return render_to_response('trackdata.html', {'track_list':detailed_trackdata}, context_instance=RequestContext(request))

@cache_page(60 * 60)
def trackdetail(request, track_id):
    """
    This view is the initial page once a track has been selected.
    """
    supported_track = get_object_or_404(SupportedTrackName, pk=track_id)
    
    rankedclasses_tuple = get_ranked_classes_by_track(supported_track.trackkey.id)
    # Format the classes and retrieve the names to display.
    formated_rankedclasses = []
    for rankedclass_id, top_racers in rankedclasses_tuple:
        rankedclass_obj = RankedClass.objects.get(pk=rankedclass_id)
        formated_rankedclasses.append({'class': rankedclass_obj,
                                       'top3':top_racers})
    
    # This is done so we can easily display a message indicating there are not rankings.
    if (formated_rankedclasses == []):
        formated_rankedclasses = None

    # Get all of the past race dates to display in the datatable
    raw_race_dates = _get_Recent_Race_Dates(supported_track)
    
    race_dates = []
    # Need to keep in mind there may be less races than expected for special events.
    for racedate, racecount in raw_race_dates:
        # TODO - clean up the copy or find a better way to get them to click on the row
        display_string = "{0} Race Results from: {1} - Click Here".format(racecount, _display_Date_User(racedate))
        click_url = '/trackdata/' + str(supported_track.id) + '/results-by-day/' + racedate.strftime('%Y-%m-%d')
        race_dates.append([display_string, click_url])
    raceday_jsdata = simplejson.dumps(race_dates)

    ctx = Context({'trackname':supported_track.trackkey.trackname,
                   'raceday_jsdata':raceday_jsdata,
                   'formated_rankedclasses':formated_rankedclasses})
    return render_to_response('trackdatadetail.html', ctx, context_instance=RequestContext(request))

def race_result_summary_by_track_day(request, track_id, race_date):
    """
    Show race summary for all the races at the track that happened
    on the specified date.
    """
    supported_track = get_object_or_404(SupportedTrackName, pk=track_id)
    
    try:
        date = datetime.datetime.strptime(race_date, "%Y-%m-%d").date()
    except ValueError():
        raise Http404
    
    # Note - Date Format (year, month, date)
    
    # ========================================================
    # Qualifying - we just show links to detailed pages
    # ========================================================
    qual_results = result_history.qualifying_by_raceday_lookup(supported_track, date)
    
    # ========================================================
    # Main Events - we want to show a summary table of the header
    # ========================================================
    results_template_format = result_history.main_event_by_raceday_lookup(supported_track, date)

    ctx = Context({'supported_track_id':supported_track.id,
                   'trackname':supported_track.trackkey.trackname,
                   'race_date':race_date,
                   'display_date':_display_Date_User(date), 
                   'raceresults':results_template_format,
                   'qual_results':qual_results})
    
    return render_to_response('trackdata/race_result_summary_for_day.html', ctx, context_instance=RequestContext(request))
    
@cache_page(60 * 60)
def trackdetail_data(request, track_id, time_frame='alltime'):
    """
    the purpose of trackdetail_data is to provide summary race data about
    the track for varying periods of time. 
    
    PERFORMANCE CONCERN
        For stats that calculated Per Racer, only a set number of results
        are returned (we dont want to do every single person). 
    
    Current stats - Filtered by date, sorted by the ct ount
        Total number of wins for the top racers
        Total number of laps for the top racers
    """
    
    # Need to verify track is still supported.
    supported_track = get_object_or_404(SupportedTrackName, pk=track_id)
    
    if (time_frame not in ('alltime', 'month', '6months')):
        raise Http404
    
    DISPLAY_RESULT_LIMIT = 100
    
    #
    # This is where we set the time period to filter by.
    #    If the filter is "All Time" there is no need to filter.
    #
    # WARNING - I am manually inserting the sql_time_filter into the raw
    # query because it does NOT come from the user. If this is changed
    # the method of executing the queries should be updated.
    #
    sql_time_filter = ''
    filterdatestr = 'All Time'
    
    if (time_frame == 'month'):
        filterdate = datetime.datetime.now() + relativedelta(months=-1)
        filterdatestr = time.strftime('%a, %d %b %Y', filterdate.timetuple())
        dbdate = time.strftime('%Y-%m-%d %H:%M:%S-01', filterdate.timetuple())
        sql_time_filter = "AND rdetails.racedate > '" + dbdate + "'"
    elif (time_frame == '6months'):
        filterdate = datetime.datetime.now() + relativedelta(months=-6)
        filterdatestr = time.strftime('%a, %d %b %Y', filterdate.timetuple())
        dbdate = time.strftime('%Y-%m-%d %H:%M:%S-01', filterdate.timetuple())
        sql_time_filter = "AND rdetails.racedate > '" + dbdate + "'"
        
    
    # Get the total number of wins.
    topwins = _get_Total_Wins(supported_track.trackkey.id, sql_time_filter, DISPLAY_RESULT_LIMIT)

    # Get the total number of laps
    toplaps = _get_Total_Lap(supported_track.trackkey.id, sql_time_filter, DISPLAY_RESULT_LIMIT)
        
    topwins_jsdata = simplejson.dumps(topwins)
    toplaps_jsdata = simplejson.dumps(toplaps)
      
    ctx = Context({'filterdate':filterdatestr,
                   'tabid':time_frame, # For this to work with tabs, I need unique id's for each datatable
                   'topwins':topwins_jsdata, 
                   'toplaps':toplaps_jsdata})
    return render_to_response('trackdatadetail_data.html', ctx, context_instance=RequestContext(request))
        
        
def _get_Total_Wins(track_key_id, sql_time_filter, row_limit):
    #
    # This query does all the work to find the total number of race wins
    #
    
    sqlquery = '''SELECT SUM(racedata.finalpos), racedata.racerpreferredname  FROM
      (
      SELECT rresults.raceid_id, rid.racerpreferredname, rresults.finalpos FROM
        rcdata_racerid as rid,
        rcdata_singleraceresults as rresults
        WHERE rresults.racerid_id = rid.id AND
            rresults.finalpos = 1    
      ) as racedata,
    rcdata_singleracedetails as rdetails
    WHERE rdetails.id = racedata.raceid_id AND
      rdetails.trackkey_id = %(trackkey)s
      ''' + sql_time_filter + '''
    /* This is were we would filter out by track id and racelength */
    GROUP BY racedata.racerpreferredname
    ORDER BY SUM(racedata.finalpos) desc
    LIMIT ''' + str(row_limit) + ''';'''
    
    cursor = connection.cursor()   
    cursor.execute(sqlquery, {'trackkey':track_key_id})
    topwins = cursor.fetchall()

    return topwins
        

def _get_Total_Lap(track_key_id, sql_time_filter, row_limit):
    #
    # This query does the work to find the total number of laps races.
    #
    querytoplaps = '''SELECT SUM(racedata.lapcount), racedata.racerpreferredname  FROM
      (
      SELECT rresults.raceid_id, rid.racerpreferredname, rresults.lapcount FROM
        rcdata_racerid as rid,
        rcdata_singleraceresults as rresults
        WHERE rresults.racerid_id = rid.id
      ) as racedata,
    rcdata_singleracedetails as rdetails
    WHERE rdetails.id = racedata.raceid_id AND
      rdetails.trackkey_id = %(trackkey)s
      ''' + sql_time_filter + '''
    /* This is were we would filter out by track id and racelength */
    GROUP BY racedata.racerpreferredname
    ORDER BY SUM(racedata.lapcount) desc
    LIMIT ''' + str(row_limit) + ''';'''
       
    cursor = connection.cursor()
    cursor.execute(querytoplaps, {'trackkey':track_key_id})
    toplaps = cursor.fetchall()
    
    return toplaps


def recentresultshistory(request, track_id):
    """
    Main page to organize and display the recent race results from the track.
    
    The race date is processed using the format '%Y-%m-%d'    
    """    
    NUMBER_OF_RESULTS_FOR_HISTORY = 5
    
    supported_track = get_object_or_404(SupportedTrackName, pk=track_id)

    raw_race_dates = _get_Recent_Race_Dates(supported_track, number_races=NUMBER_OF_RESULTS_FOR_HISTORY)
    
    race_dates = []
    # Need to keep in mind there may be less races than expected for special events.
    for index in range(min(len(raw_race_dates), NUMBER_OF_RESULTS_FOR_HISTORY)):
        race_dates.append({'id':"button_" + str(index), 
                           'display_date': _display_Date_User(raw_race_dates[index][0]),
                           'date': raw_race_dates[index][0].strftime('%Y-%m-%d'), # This is for url.
                           })
                          
    ctx = Context({'supportedtrack':supported_track, 'race_dates':race_dates})
                                                             
    return render_to_response('recentresultshistory.html', ctx, context_instance=RequestContext(request))    


def recentresultshistory_data(request, track_id, race_date):
    """
    Will use the recentresultshistory_data.html template to display all
    of the MAIN event races at the specified track_id on the given race_date.
    
    Qualifying races are only provided a link to the details page.
    """
    supported_track = get_object_or_404(SupportedTrackName, pk=track_id)

    try:
        date = datetime.datetime.strptime(race_date, "%Y-%m-%d").date()
    except ValueError():
        raise Http404
    
    # Note - Date Format (year, month, date)
    
    # ========================================================
    # Qualifying - we just show links to detailed pages
    # ========================================================
    qual_results = result_history.qualifying_by_raceday_lookup(supported_track, date)
    
    # ========================================================
    # Main Events - we want to show a summary table of the header
    # ========================================================
    results_template_format = result_history.main_event_by_raceday_lookup(supported_track, date)

    ctx = Context({'supported_track_id':supported_track.id,
                   'race_date':race_date,
                   'display_date':_display_Date_User(date), 
                   'raceresults':results_template_format,
                   'qual_results':qual_results})
    
    return render_to_response('trackdata/recentresultshistory_data.html', ctx, context_instance=RequestContext(request))


def recentresultshistory_share(request, track_id, race_date):
    """
    Will use the recentresultshistory_data.html template to display all
    of the MAIN event races at the specified track_id on the given race_date.
    
    Qualifying races are only provided a link to the details page.
    """
    supported_track = get_object_or_404(SupportedTrackName, pk=track_id)

    try:
        date = datetime.datetime.strptime(race_date, "%Y-%m-%d").date()
    except ValueError():
        raise Http404
    
    # Note - Date Format (year, month, date)
    details = SingleRaceDetails.objects.filter(racedate__range=(date, date + relativedelta(days=+1)),
                                                    trackkey=supported_track.trackkey).order_by('racedate')
    
    race_details = []
    for qual in details:
        classname_summary = utils.format_main_event_for_user(qual) + \
            " - Round:" + str(qual.roundnumber) + \
            " Race:" + str(qual.racenumber)
        
        race_details.append({'racedetail_id':qual.id,
                             'racedata_summary':classname_summary})
    
    ctx = Context({'trackname':supported_track.trackkey, 
                   'display_date':_display_Date_User(date),
                   'race_details':race_details})
    
    return render_to_response('recentresultshistory_share.html', ctx, context_instance=RequestContext(request))


def _get_Recent_Race_Dates(supported_track, number_races=None):
    """
    Retrieve a list of python datetime objects for the most recent races.    
    """       
    # This is a quick re-write to take advantage for the time zone conversion.
    queryset = SingleRaceDetails.objects.filter(trackkey__exact=supported_track.trackkey.id).values('racedate').order_by('-racedate')
    return _get_recent_race_dates_from_queryset(queryset, number_races)

def _get_recent_race_dates_from_queryset(queryset, number_races):
    """
    Given a queryset contains SingleRaceDetails, group the races by the day (collapse multiple races on the
    same day down to a single date) and get a count for the day.

    WARNING - the queryset must be sorted by racedate.
    """
    tmz = pytz.timezone(settings.TIME_ZONE)    
    unique_dates = []
    for date in queryset:
        if number_races and (len(unique_dates) >= number_races):
            # We want to stop when we have enough races.
            break
                
        converted_date = date['racedate'].astimezone(tmz).date()        
        if (not unique_dates) or converted_date != unique_dates[-1][0]:
            unique_dates.append([converted_date, 1])
        else:
            unique_dates[-1][1] += 1
        
    #print 'UNIQUE_DATES', unique_dates
    # [datetime.date(2012, 8, 7), datetime.date(2012, 8, 3), datetime.date(2012, 7, 31),
    return unique_dates

def _display_Date_User(datetime_object):
    """
    Take the datetime object and generate the string to display to users.
    """
    return datetime_object.strftime('%a, %d %b %Y')