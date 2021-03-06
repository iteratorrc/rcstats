import pytz
import time
import datetime
import re

from dateutil.relativedelta import relativedelta

from django.template import Context
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Count
from django.db.models import Q
from django.utils import simplejson
from django.conf import settings

from rcstats.rcdata.models import RacerId, TrackName, SingleRaceDetails, SingleRaceResults
from rcstats.myresults.models import FeaturedRacer


def myresults(request):
    """
    This view is the main entry point into individual racer results scenario.
    
    It gives a listing of all tracked race names, and links to their respective
    profile pages.
    """
    racer_names = _get_racer_for_main_table()
        
    # BUG - Why cant the simplejson dump the results from the ORM, I could save another
    # loop on the data if it could serialize correctly.
    manual_format = []
    for name in racer_names:
        manual_format.append( list(name) )
    jsdata = simplejson.dumps(manual_format)
    
    featured_racers = FeaturedRacer.objects.select_related("racerid__racerpreferredname")
    
        
    return render_to_response('myresults.html', {'racer_names':jsdata,
                                                 'featured_racers': featured_racers}, context_instance=RequestContext(request))

def _get_racer_for_main_table():
    """
    Get a sorted list of racers currently being tracked. These are the raw names.
    """
    return RacerId.objects.all().order_by('racerpreferredname').values_list('racerpreferredname', 'id')


def _get_RaceTimeline_JSData(racer_obj):
    '''
    Get the data for the timeline of all race results for the racer. This
    data will be converted to JSON and formated for use in the FLOT graph.
        This will have special formating for the time (FLOT requires this),
        so the axis is correct.    
    '''
    # This is every race result for this racer.
    race_results = SingleRaceResults.objects.filter(racerid=racer_obj.id)
    '''
    IMPORTANT FOR FLOT GRAPHS
    
    The timestamps must be specified as Javascript timestamps, as
      milliseconds since January 1, 1970 00:00. This is like Unix
      timestamps, but in milliseconds instead of seconds (remember to
      multiply with 1000!)
    '''
    
    graphdata = []
    # Example graphdata
    #     [[1330727163000.0, 1], [1330727881000.0, 7], [1313339287000.0, 5], ... ]
    for result in race_results:
        race_detail = SingleRaceDetails.objects.get(pk=result.raceid.id)
        # Convert to milliseconds
        formatedtime = time.mktime(race_detail.racedate.timetuple()) * 1000
        graphdata.append([formatedtime, result.finalpos])
    
    #print 'graphdata', graphdata
    mylist = [{'label':racer_obj.racerpreferredname, 'data':graphdata}]
    jsdata = simplejson.dumps(mylist)
    
    return jsdata


def _get_Group_Race_Classes(racer_obj):
    '''
    Identify and group the race classes for the racer_obj
    
    WARNING - This only tracks main events. The racedata must contain the 
    token: "main"
    ''' 
        
    # Warning - requires the racedata to contain the token 'main'
    racedetails_allmains = SingleRaceDetails.objects.filter(singleraceresults__racerid=racer_obj.id, 
                                                            mainevent__gte=1)\
                                                            .values('racedata')\
                                                            .annotate(dcount=Count('racedata'))
    
    cleaned_classnames = _get_Cleaned_Class_Names(racedetails_allmains)
    
    # Now I have the unique class names and their count, I need to
    # display this information to the user.
    class_frequency = cleaned_classnames.items()
    class_frequency.sort(key=lambda tup:tup[1], reverse=True) # Example of class_frequency [(u'STOCK BUGGY', 105), (u'STOCK TRUCK', 62),
    
    # This is special formating for the FLOT graph.
    pie_chart_data = []
    for single_class_freq in class_frequency:
        pie_chart_data.append({'label':single_class_freq[0] + ": " + str(single_class_freq[1]), 
                               'data':single_class_freq[1]})
    
    # This is an example of what I need for the pie chart.
    #  [ { label: "This",  data: 44 }, ...
    classfreq_jsdata = simplejson.dumps(pie_chart_data)
    
    return cleaned_classnames, classfreq_jsdata


def generalstats(request, racer_id):
    """
    This view displays the current stats for an individual racer. 
    
    WARNING - this is currently a wall of code as I am prototyping 
    out the features that we want to display. Portions have already
    been refactored or pushed into a different view, but additional
    cleanup is needed.
    """
    racer_obj = get_object_or_404(RacerId, pk=racer_id)
    
    # Get the data for the flot graph of race history over time. 
    timeline_jsdata = _get_RaceTimeline_JSData(racer_obj)
            
    # Get the data for the flot pie graph of the classes races.
    cleaned_classnames, classfreq_jsdata = _get_Group_Race_Classes(racer_obj)

    # ===========================================================
    # Find last 5 races for each class and track.
    # ===========================================================
    '''
    There are a couple of issues to work through here.
        TO START WITH - find the tracks and classes. Then once I have filtered by
        that, I will show the last 5 races (how ever old they are).
        
    1. Find the tracks they have raced at.
    2. Find the classes they have raced in at each track.
    3. Present the last 5 races based on 1 and 2.
        GOING TO USE 'main' in the title for now, since double and trip mains do happen.
        
    [
        {
         "js_id": <>
         "trackname": <>,
         "classes: [
                    {"js_id":<>
                     "classname": <>,
                     "individual_racedata": [
                                             {'date':<>, 'id':<>, "js_id":<>}, 
                                             ...
                                            ]
                    }
                    ... Multiple classes
                   ]
         }
         ... Multiple tracks 
    ]
    
    This can be used then to construct the display for the user, with another page
    handling the lookup and display of race results for that day.
    Each racedate button displayed to the user, will show them the last race.
       
    '''
    
    # Example [{'classes': 
    #            [{'classname': u'Stock Short Course', 'individual_racedata': [60, 3334, 1005, 1001, 1766]}, 
    #             {'classname': u'Mod Short Course', 'individual_racedata': [2139, 2468, 1443, 3336, 1026]}, 
    #             {'classname': u'Stock Buggy', 'individual_racedata': [2470, 1444, 59, 3333, 1023]}], 
    #           'trackname': u'Bremerton R/C Raceway'}]
    recent_race_data = []
        
        
    # I am going to remove this functionality, since I think most people just want to see the last results.
    # Right now it is common to go to a profile, and find they have no results because of this.
    '''
    # Get the date from 2 months ago.
    filterdate = datetime.datetime.now() + relativedelta(months=-2)
    filterdatestr = time.strftime('%a, %d %b %Y', filterdate.timetuple())
    dbdate = time.strftime('%Y-%m-%d', filterdate.timetuple())
    #sql_time_filter = "AND rdetails.racedate > '" + dbdate + "'"
    
    racetracks = SingleRaceDetails.objects.filter(racedate__gte=dbdate,
                                                  singleraceresults__racerid=racer_obj.id).values('trackkey').annotate()
    '''
    racetracks = SingleRaceDetails.objects.filter(singleraceresults__racerid=racer_obj.id).values('trackkey').annotate()
    
    js_id_track = 0
                                                  
    for track in racetracks:
        #print 'track', track        
        trackname = TrackName.objects.get(pk=track['trackkey'])
        
        recent_race_data.append({'trackname': trackname.trackname, 'classes': [], 'js_id':js_id_track})
        js_id_track += 1

        '''
        # We need the class names as they will be present to the user.
        test = SingleRaceDetails.objects.filter(trackkey=track['trackkey'], # track
                                                racedate__gte=dbdate, # date
                                                singleraceresults__racerid=racer_obj.id, # racer
                                                racedata__icontains = "main" # class name
                                                ).values('racedata').annotate(dcount=Count('racedata')).order_by('-dcount')
        '''
        test = SingleRaceDetails.objects.filter(trackkey=track['trackkey'], # track
                                                singleraceresults__racerid=racer_obj.id, # racer
                                                mainevent__gte = 1
                                                ).values('racedata').annotate(dcount=Count('racedata')).order_by('-dcount')
        
        cleaned_classnames = _get_Cleaned_Class_Names(test)
        
        # NOTE - For the time being I am not going to worry about providing a recent
        # summary of race history. 
        '''
        # Now I have the unique class names and their count, I need to 
        # display this information to the user.           
        class_frequency = cleaned_classnames.items()
        class_frequency.sort(key = lambda tup: tup[1], reverse = True)
        # Example of class_frequency [(u'STOCK BUGGY', 105), (u'STOCK TRUCK', 62), 
        '''
        js_id_class = 0

        for unique_class in cleaned_classnames.keys():
            #print 'unique class', unique_class
                       
            class_dict = {'classname':unique_class, 'individual_racedata':[], 'js_id':js_id_class}
            js_id_class += 1
            
            # Now I have a track, and a class name.
            # I want the last 5 races.
            racedetails = SingleRaceDetails.objects.filter(Q(mainevent__gte=1) & Q(racedata__icontains=unique_class),
                                                           trackkey=track['trackkey'],
                                                           singleraceresults__racerid=racer_obj.id                                                           
                                                           ).order_by('-racedate')[:5] 
            
            js_id_race = 0
            
            for race in racedetails:
                tmz = pytz.timezone(settings.TIME_ZONE)
                converted_date = race.racedate.astimezone(tmz).date() 
                race_dict = {'id':race.id, 'date':_display_Date_User(converted_date), 'js_id':js_id_race}
                js_id_race += 1
                
                class_dict['individual_racedata'].append(race_dict)
                # Now that I have the races, I need to pick the groups, and what to display.
                #print 'racedetails', race.id, 'racedata', race.racedata, 'date', race.racedate
       
            
            recent_race_data[-1]['classes'].append(class_dict)
    
    ctx = Context({'racerid':racer_obj.id,
                   'racername':racer_obj.racerpreferredname, 
                   'classfreq_jsdata':classfreq_jsdata,
                   'racehistory_jsdata':timeline_jsdata, 
                   'recent_race_data':recent_race_data})
    
    return render_to_response('generalstats.html', ctx, context_instance=RequestContext(request))


def _get_Cleaned_Class_Names(raw_racedata_list):
    """
    Takes a list of (dictionaries) racedata and their counts, and finds 
    distinct classes from the potentially dirtied names in the race details
        Example of extraction:
            "mod buggy A2 main":2  -> "mod buggy": 2
            "mod buggy A main":5  -> "mod buggy": 7
            
    """
    
    # A dictionary of class names {u'MODIFIED SHORT COURSE': 4, u'STOCK BUGGY': 105,
    unique_classes = {}
    
    # I am going to go through the list and remove 'duplicates'
    # Example of the data befor I work with it:
    #    [{'dcount': 86, 'racedata': u'STOCK BUGGY A Main'},
    #    {'dcount': 56, 'racedata': u'STOCK TRUCK A Main'},
    #    {'dcount': 51, 'racedata': u'13.5 STOCK SHORT COURSE A Main'}]
        
    for race_dict in raw_racedata_list:     
        
        # WARNING
        # After migration - this code will be pointless, we can just use racedata.
        # WARNING
               
        # I no longer care about the 'A','B', '1', 'main' etc. I am going to strip
        # and trim the strings as I add them to a new master table.            
        pattern = re.compile("[A-Z][1-9]? main", re.IGNORECASE)        
        match = pattern.search(race_dict['racedata'])
        if match:
            start_index = match.start(0)        
            # We want to trim off the 'A main' part of the string and clean it up.
            processed_classname = race_dict['racedata'][:start_index].strip('+- ')
        else:
            # EXPECTED PATH AFTER MIGRATION
            processed_classname = race_dict['racedata']
        unique_classes[processed_classname] = unique_classes.get(processed_classname, 0) + race_dict['dcount']

    return unique_classes


def _display_Date_User(datetime_object):
    """
    Take the datetime object and generate the string to display to users.
    """
    return datetime_object.strftime('%a, %d %b %Y')
