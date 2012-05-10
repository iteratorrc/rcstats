'''
Created on Jan 4, 2012

@author: Anthony Honstain
'''
import unittest


# EXAMPLE of file this is designed to process: 
'''
Scoring Software by www.RCScoringPro.com                10:32:24 PM  8/13/2011

                             Bremerton R/C Raceway

Stock Buggy A Main                                            Round# 3, Race# 5

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
                  Behlen, kyle    #4      29     8:08.626     16.084           
             Honstain, Anthony    #2      28     8:00.509     16.471           
                  Fabie, Edwin    #8      27     8:04.445     16.787           
                   Craig, Mike    #1      27     8:04.702     16.387      0.257
                    Jim, Reeve    #9      27     8:15.222     17.005     10.777
                   Yates, Paul    #7      26     8:01.765     17.382           
              Haselberger, Joe    #6      26     8:10.132     16.962      8.367
               Cantrell, Jason    #5      26     8:14.373     17.139     12.608
                mcneal, pierre    #3      25     8:07.776     17.303           
                     simon,joe    #10     25     8:13.158     17.903      5.382

 ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
 3/3.804 1/2.936 7/6.013 2/3.487 4/4.118 6/5.817 10/7.72 5/4.512 8/6.310 9/6.941
 3/18.33 2/18.41 9/22.01 1/16.65 8/22.87 5/18.40 10/20.3 4/18.88 7/20.57 6/19.24
 2/17.93 3/19.76 10/23.9 1/16.25 8/22.56 6/21.97 9/22.79 4/18.41 7/22.40 5/18.80
 2/17.56 3/16.88 10/19.4 1/17.50 6/18.03 9/23.34 8/17.87 4/19.72 7/18.46 5/20.67
 3/22.22 2/17.19 10/20.0 1/16.78 8/22.16 9/21.21 7/20.11 4/18.81 6/20.60 5/18.93
 3/18.81 2/19.30 10/20.9 1/17.44 8/17.13 9/20.36 7/17.62 4/19.87 6/17.29 5/20.34
 
 3/17.20 2/20.37 10/18.1 1/20.19 8/21.23 7/18.02 6/17.81 4/16.86 5/17.81 9/19.34
 3/19.34 2/17.19 9/17.53 1/16.92 8/17.50 7/20.18 6/18.11 4/17.51 5/19.83 10/20.8
 3/17.14 2/17.08 9/18.83 1/18.36 8/20.81 7/18.55 6/17.77 4/17.04 5/18.14 10/23.8
 3/17.69 2/16.66 9/22.09 1/17.32 8/17.82 7/17.86 6/20.44 4/16.78 5/17.74 10/19.7
 3/19.72 2/16.92         1/17.16 8/18.63 7/18.13 6/17.84 4/17.55 5/21.44        
 4/20.23 2/17.75         1/16.79                         3/19.34 5/18.52        
         2/16.99         1/17.82                                                
                         1/18.00                                                
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
     27/     28/     25/     29/     26/     26/     26/     27/     27/     25/
  8:04.7  8:00.5  8:07.7  8:08.6  8:14.3  8:10.1  8:01.7  8:04.4  8:15.2  8:13.1
'''

class SingleRace(object):
    '''
    classdocs
    '''
            

    def __init__(self, filename, singleRaceLines):
        '''
        Constructor
        '''
        # The raw data rows from the text file.
        #     HAVE NOT BEEN PARSED YET
        self._raceHeaderData_RAW = []
        self._columnHeaders = ""
        self._lapRowsRaw = []
        self._trailingLapRows = []
        
        self.filename = filename
        # The refined structures.
        #________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
        #                   Behlen, kyle    #4      29     8:08.626     16.084           
        self.date = None
        self.trackName = None
        self.raceClass = None
        self.roundNumber = None
        self.raceNumber = None
        
        self.raceHeaderData = [] # List of Dictionaries
        self.lapRowsTime = [] # List of Lists
        self.lapRowsPosition = []
           
        '''     
        # Some race results have the pace for the lap included in the results
         ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
         6/37.57 5/32.86 4/31.55         3/29.97 2/29.45 1/29.18                        
         10/15.7 11/01.4 12/18.7         13/29.7 13/22.8 13/19.3                        

         6/20.12 5/22.57 4/20.81         1/19.34 3/22.50 2/22.56                        
         13/15.1 13/00.3 14/06.5         15/09.8 14/03.7 14/02.1                        

         6/19.56 5/20.44 4/21.30         1/20.43 3/20.52 2/19.76                        
         14/00.6 15/19.3 15/08.3         16/12.0 15/02.3 16/21.3                        

         6/24.54 4/21.61 3/19.91         1/19.21 2/19.79 5/28.67
         
         # We want to check if laps 3,6,9 are all empty
        EXAMPLE - print singleRaceLines
         '/37.57 5/32.86 4/31.55         3/29.97 2/29.45 1/29.18', 
         ' 10/15.7 11/01.4 12/18.7         13/29.7 13/22.8 13/19.3', 
         '',
        '''
                
        # Process the file lines into initial structures.
        lapData = False
        for line in singleRaceLines:
            
            # Process a SINGLE race
                            
            # Look for the column data
            if not lapData and (line.find('__10') != -1):
                # ___1___ ___2___ ___3___ ___4___ ___5___ 
                if not line.find('__1__'):
                    raise Exception("The column header data spilled into a new line")
                self._columnHeaders = line
                lapData = True
                
                # Check to see if pace data is mixed in - this is a strong indicator.
                index = singleRaceLines.index(line)
                if (singleRaceLines[index + 3] == '' and 
                    singleRaceLines[index + 6] == '' and 
                    singleRaceLines[index + 9] == ''):
                    
                    raise Exception("This file format not supported, cannot mix pace data in with lap times.")
                
                
            # The trailing data is redundant
            elif lapData and (line.find('-----') != -1):
                #  ------- ------- ------- ------- 
                break
            
            # Get the laps in row format
            elif lapData:
                # Warning - we dont want to blanket strip this (white space matters)
                self._lapRowsRaw.append(line.strip('\n'))
                
            # Get race header data.
            if not lapData:
                # 3/17.20 2/20.37 10/18.1 1/20.19 
                self._raceHeaderData_RAW.append(line)
            
#        if verbose:
#            print "self._raceHeaderData_RAW"
#            print "-"*20
#            for line in self._raceHeaderData_RAW:
#                print line.strip('\n')
#            
#            print "self._columnHeaders"
#            print "-"*20
#            print self._columnHeaders
#            
#            print "self._lapRowsRaw"
#            print "-"*20
#            print self._lapRowsRaw


        # ===================================================
        # Process the _lapRowsRaw data
        # ===================================================
        
        #print self._columnHeaders.split()
        for index in range(len(self._columnHeaders.split())):
            self.lapRowsTime.append([])
            self.lapRowsPosition.append([])    
        
        lapWidth = self._columnHeaders[1:].find(' ') - 1
            
        # INFO - at this stage, we are going to keep empty laps here, it is
        # usefull information for the user.
        for row in self._lapRowsRaw:
            # Need to parse the row
            # Example:3/3.804 1/2.936 7/6.013 2/3.487 4/4.118 6/5.817 10/7.72 5/4.512 8/6.310 9/6.941
                        
            # Split is not going to work because it trims: racerSplit = row.split()
            
            # how big a single lap (in characters)
            i = 1
            racerIndex = 0
            while i < len(row):                  
                # Print line debugging
                #print "Row:'" + row + "'"
                #print "raceIndex:" + str(racerIndex) + " lapWidth:" + str(lapWidth)
                #print "i:", i, "'" + row[i:i+lapWidth + 1] + "'" 
                #print "lapRwosPos:" + str(self.lapRowsPosition)
                #print self._columnHeaders

                pos, lap = self.ParseLap(row[i:i+lapWidth + 1])
                self.lapRowsPosition[racerIndex].append(pos)
                self.lapRowsTime[racerIndex].append(lap)
                #self.lapRowsTime[racerIndex].append(row[i:i+lapWidth + 1])
                i += lapWidth + 2 # +2 to skip the ' ' space.
                racerIndex += 1
            
                
        # Can print the first few racers results.   
        #print self.lapRowsTime[3]
        #print self.lapRowsPosition[3]
        
        
        # ====================================================
        # Process the header data - Example
        # ====================================================
        """        
        Scoring Software by www.RCScoringPro.com                10:32:24 PM  8/13/2011
        
                                     Bremerton R/C Raceway
        
        Stock Buggy A Main                                            Round# 3, Race# 5
        
        ________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
                          Behlen, kyle    #4      29     8:08.626     16.084           
                     Honstain, Anthony    #2      28     8:00.509     16.471           
                          Fabie, Edwin    #8      27     8:04.445     16.787           
                           Craig, Mike    #1      27     8:04.702     16.387      0.257
                            Jim, Reeve    #9      27     8:15.222     17.005     10.777
                           Yates, Paul    #7      26     8:01.765     17.382           
                      Haselberger, Joe    #6      26     8:10.132     16.962      8.367
                       Cantrell, Jason    #5      26     8:14.373     17.139     12.608
                        mcneal, pierre    #3      25     8:07.776     17.303           
                             simon,joe    #10     25     8:13.158     17.903      5.382
        """

        # Get the date and time
        self.date = self.ParseDate(self._raceHeaderData_RAW[0])
        
        self.trackName = self._raceHeaderData_RAW[2].strip()
        
        self.raceClass, self.roundNumber, self.raceNumber = self.ParseClassRndData(self._raceHeaderData_RAW[4])
        
        individualResult = self._raceHeaderData_RAW[7:]
        finalRacePosition = 0;
        
        #print "individualResult" + individualResult.__str__()
        for line in individualResult[:-1]:
            finalRacePosition += 1
            driver = line[:line.find("#")].strip()
            
            # Cut off the racer names to simplify things.
            racedata = line[line.find("#"):]
            lineList = racedata.split()
                                
            #print "lineList:" , lineList
            carRaw = lineList[0]
            if (carRaw[0] != '#'):
                raise Exception("Incorrect format for header data, execting a '#' in the car number, line: " + line)
            car = int(carRaw[1:])
            
            laps = int(lineList[1])
            
            # WARNING - it is possible to have a fast lap, but NO racetime.
            racetime = lineList[2]
            
            fastlap = ""
            behind = ""
            # Not everyone had a 'behind' or a 'fastlap' field.
            if (len(lineList) > 3):
                fastlap = lineList[3]
            if len(lineList) == 5:
                behind = lineList[4]

            if (racetime.find(':') >= 0):
                self.raceHeaderData.append({"Driver":driver, 
                                             "Car#":car, 
                                             "Laps":laps, 
                                             "RaceTime":racetime, 
                                             "Fast Lap":fastlap, 
                                             "Behind":behind,
                                             "Final Position":finalRacePosition})
            else:
                self.raceHeaderData.append({"Driver":driver, 
                                         "Car#":car, 
                                         "Laps":laps, 
                                         "RaceTime":'', 
                                         "Fast Lap":racetime, 
                                         "Behind":behind,
                                         "Final Position":finalRacePosition})

        #self.class
        #self.roundNumber
        #self.raceNumber
        #self.raceHeaderData 

        # *******************************************************
        # Logging code - need to implement logging in this module.
        # *******************************************************
        '''
        if verbose:
            print "self.date: " + str(self.date)
            print "self.trackName: " + str(self.trackName)
            print "self.raceClass: " + str(self.raceClass)
            print "self.roundNumber: " + str(self.roundNumber)
            print "self.raceNumber: " + str(self.raceNumber)
            
            print "self.raceHeaderData"
            print "-"*20
            for line in self.raceHeaderData:
                print line
            
            print "self.lapRowsTime"
            print "-"*20
            for line in self.lapRowsTime:
                print line
                            
            print "self.lapRowsPosition"
            print "-"*20
            for line in  self.lapRowsPosition:
                print line
         '''
   
    def ParseDate(self, rawDateLine):
        #Scoring Software by www.RCScoringPro.com                10:32:24 PM  8/13/2011
        trimmedDate = rawDateLine[41:].strip()
        #print "trim" + trimmedDate
        # TODO - get this in the correct format for the DB.   
        return trimmedDate
            
    def ParseClassRndData(self, rawClassData):
        #Stock Buggy A Main                                            Round# 3, Race# 5
        #print "RawClassData:" + rawClassData
        roundIndex = rawClassData.find("Round#")    
        raceClass = rawClassData[:roundIndex].strip()
        round = rawClassData[roundIndex:].split(',')[0].split()[1]
        race = rawClassData[roundIndex:].split(',')[1].split()[1]
#        print raceClass, round, race
        return (raceClass, round, race)
            
    def ParseLap(self, rawLap):
        # rawLap will have the form of 3/3.804
        if rawLap.find('/') == -1:
            return ("", "")
        
        splitLap = rawLap.split('/')
        return (splitLap[0], splitLap[1])
    
    
    
singleRaceSimple = '''Scoring Software by www.RCScoringPro.com                8:09:03 PM  01/14/2012

                               TACOMA R/C RACEWAY

MODIFIED BUGGY B Main                                         Round# 3, Race# 16

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
Matesa, Ryan            #2         28         8:10.270         16.939                  
DIBRINO, ANDY            #3         28         8:13.744         16.748             3.474
JOWERS, ROBERT            #4         27         8:01.288         16.874                  
HONSTAIN, ANTHONY            #8         27         8:11.316         17.290            10.028
GOULD, CHRIS            #1         27         8:11.756         16.900            10.468
CHERRY, GEORGE            #5         27         8:17.078         17.426            15.790
TRAVIS SCHREVEN            #7         26         8:01.935         16.613                  
RASHEED, DEREK            #6         26         8:02.970         17.008             1.035
ROGER SEIM            #10        26         8:04.489         17.121             2.554
TOM WAGGONER            #9         26         8:07.943         17.063             6.008

 ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
 10/24.5 1/20.58 3/22.32 6/23.85 4/23.14 5/23.45 2/21.97 8/24.19 9/24.35 7/23.92
 8/18.04 1/17.09 5/19.28 9/19.79 3/17.67 4/17.72 2/17.83 7/18.19 10/20.0 6/18.13
 8/17.53 1/16.93 4/17.02 9/17.43 3/17.66 5/17.98 2/17.22 7/17.34 10/19.4 6/17.26
 5/17.34 1/17.11 3/17.65 7/17.67 9/22.07 8/20.90 2/18.20 4/17.56 10/20.8 6/19.10
 4/17.13 1/17.25 3/17.96 6/17.16 9/17.42 8/17.60 2/18.27 5/17.74 10/17.3 7/18.50
 4/17.30 1/17.25 3/17.26 6/17.65 9/19.12 8/18.86 2/17.14 5/17.76 10/17.5 7/17.19
 4/17.21 1/16.99 3/17.17 6/17.42 9/17.63 8/17.75 2/17.92 5/17.59 10/17.5 7/19.47
 2/17.42 1/17.44 5/20.61 3/17.32 9/17.48 8/17.46 4/20.34 6/19.75 10/17.3 7/17.26
 2/17.14 1/17.33 4/17.39 3/17.60 9/18.96 8/19.20 7/21.09 5/17.41 10/18.5 6/17.34
 2/17.18 1/17.56 4/16.74 3/17.38 9/21.50 10/22.4 6/18.16 5/19.21 8/18.10 7/22.36
 2/17.47 1/17.31 4/17.49 3/16.88 9/18.12 10/17.8 7/20.85 5/17.53 8/18.10 6/17.75
 2/17.01 1/17.35 4/16.87 3/17.26 9/19.50 8/18.13 10/23.2 5/17.72 6/18.36 7/19.70
 2/17.21 1/18.07 4/17.10 3/16.97 8/17.55 10/23.3 9/17.77 5/18.00 6/17.10 7/18.20
 2/19.16 1/17.31 3/17.16 4/18.11 6/17.63 10/17.9 9/18.11 5/17.59 7/21.18 8/21.60
 2/17.03 1/18.23 3/17.14 4/17.30 6/17.76 10/19.0 9/20.36 5/17.54 7/17.56 8/17.80
 4/19.43 1/17.40 2/18.27 3/18.04 6/17.53 10/18.9 9/17.70 5/17.77 8/20.34 7/17.22
 4/17.24 1/17.32 2/16.86 3/17.12 6/18.08 10/17.1 9/17.03 5/19.33 8/17.13 7/17.19
 4/17.43 1/17.15 2/17.15 3/17.52 6/17.88 10/17.0 9/17.36 5/17.65 8/17.06 7/17.65
 4/17.31 1/17.31 2/17.41 3/17.12 6/17.57 10/17.6 9/17.01 5/17.29 8/17.56 7/17.12
 4/16.90 1/17.47 2/17.02 3/16.87 6/17.80 10/17.2 8/17.54 5/18.06 9/20.40 7/17.58
 4/17.33 1/17.31 2/17.14 3/17.08 6/17.52 10/17.0 8/17.27 5/18.06 9/17.62 7/18.30
 4/17.17 1/17.42 2/17.15 3/17.82 6/18.35 9/18.27 8/18.52 5/18.12 10/24.2 7/17.48
 4/24.36 1/18.37 2/17.37 3/20.07 6/17.81 9/17.20 8/16.61 5/17.55 10/17.4 7/17.91
 5/21.31 1/17.47 2/17.36 3/17.00 6/17.60 9/17.25 8/17.07 4/17.61 10/17.9 7/17.49
 5/17.24 1/17.34 2/17.20 3/17.26 6/17.88 8/17.78 7/17.89 4/17.69 10/17.2 9/23.20
 4/17.02 1/17.36 2/17.32 3/17.40 6/17.65 8/17.54 7/19.32 5/17.86 10/17.3 9/17.66
 5/20.17 1/17.27 2/16.93 3/18.05 6/18.07                 4/19.08                
         1/17.14 2/17.27                                                        
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
     27/     28/     28/     27/     27/     26/     26/     27/     26/     26/
  8:11.7  8:10.2  8:13.7  8:01.2  8:17.0  8:02.9  8:01.9  8:11.3  8:07.9  8:04.4
'''

class TestSingleRaceSimple(unittest.TestCase):

    def setUp(self):        
        self.SingleRace = SingleRace("test_filename", singleRaceSimple.split('\n'))

    def test_racerOne(self):
        # Note - this test verifies racer one, it expects empty laps at the end
        # (since he did not complete the same number of laps as the leader). 
        expectedLaps = ["24.5", "18.04", "17.53", "17.34", "17.13", "17.30", "17.21", "17.42", "17.14", "17.18", "17.47", "17.01", "17.21", "19.16", "17.03", "19.43", "17.24", "17.43", "17.31", "16.90", "17.33", "17.17", "24.36", "21.31", "17.24", "17.02", "20.17", ""]
        
        self.assertEqual(expectedLaps, self.SingleRace.lapRowsTime[0])

    def test_racerTwo(self):
        expectedLaps = ["20.58", "17.09", "16.93", "17.11", "17.25", "17.25", "16.99", "17.44", "17.33", "17.56", "17.31", "17.35", "18.07", "17.31", "18.23", "17.40", "17.32", "17.15", "17.31", "17.47", "17.31", "17.42", "18.37", "17.47", "17.34", "17.36", "17.27", "17.14"]

        self.assertEqual(expectedLaps, self.SingleRace.lapRowsTime[1])
#
    def test_racerTen(self):
        expectedLaps = ["23.92", "18.13", "17.26", "19.10", "18.50", "17.19", "19.47", "17.26", "17.34", "22.36", "17.75", "19.70", "18.20", "21.60", "17.80", "17.22", "17.19", "17.65", "17.12", "17.58", "18.30", "17.48", "17.91", "17.49", "23.20", "17.66", "", ""]

        self.assertEqual(expectedLaps, self.SingleRace.lapRowsTime[9])
        
    def test_headerData(self):
        self.assertEqual("TACOMA R/C RACEWAY", self.SingleRace.trackName)
        #self.assertEqual("8:09:03 PM  01/14/2012", self.SingleRace.date)
        self.assertEqual("MODIFIED BUGGY B Main", self.SingleRace.raceClass)
        self.assertEqual("3", self.SingleRace.roundNumber)
        self.assertEqual("16", self.SingleRace.raceNumber)
        
        self.assertEqual(self.SingleRace.raceHeaderData[-1], 
                         {"Driver":"TOM WAGGONER", 
                          "Car#":9, 
                          "Laps":26, 
                          "RaceTime":"8:07.943", 
                          "Fast Lap":"17.063", 
                          "Behind":"6.008",
                          "Final Position":10})



class TestSingleRaceSimpleTextFile(unittest.TestCase):

    def setUp(self):   
        self.filename = "TestFile_SingleRaceSimple.txt"
        with open(self.filename) as f: 
            content = f.readlines()     
        self.SingleRace = SingleRace(self.filename, content)

    def test_filename(self):
        self.assertEqual(self.filename, self.SingleRace.filename)

    def test_racerOne(self):
        # Note - this test verifies racer one, it expects empty laps at the end
        # (since he did not complete the same number of laps as the leader). 
        expectedLaps = ["24.5", "18.04", "17.53", "17.34", "17.13", "17.30", "17.21", "17.42", "17.14", "17.18", "17.47", "17.01", "17.21", "19.16", "17.03", "19.43", "17.24", "17.43", "17.31", "16.90", "17.33", "17.17", "24.36", "21.31", "17.24", "17.02", "20.17", ""]
        
        self.assertEqual(expectedLaps, self.SingleRace.lapRowsTime[0])

    def test_racerTwo(self):
        expectedLaps = ["20.58", "17.09", "16.93", "17.11", "17.25", "17.25", "16.99", "17.44", "17.33", "17.56", "17.31", "17.35", "18.07", "17.31", "18.23", "17.40", "17.32", "17.15", "17.31", "17.47", "17.31", "17.42", "18.37", "17.47", "17.34", "17.36", "17.27", "17.14"]

        self.assertEqual(expectedLaps, self.SingleRace.lapRowsTime[1])

    def test_racerTen(self):
        expectedLaps = ["23.92", "18.13", "17.26", "19.10", "18.50", "17.19", "19.47", "17.26", "17.34", "22.36", "17.75", "19.70", "18.20", "21.60", "17.80", "17.22", "17.19", "17.65", "17.12", "17.58", "18.30", "17.48", "17.91", "17.49", "23.20", "17.66", "", ""]

        self.assertEqual(expectedLaps, self.SingleRace.lapRowsTime[9])
        
    def test_headerData(self):
        self.assertEqual("TACOMA R/C RACEWAY", self.SingleRace.trackName)
        #self.assertEqual("8:09:03 PM  01/14/2012", self.SingleRace.date)
        self.assertEqual("MODIFIED BUGGY B Main", self.SingleRace.raceClass)
        self.assertEqual("3", self.SingleRace.roundNumber)
        self.assertEqual("16", self.SingleRace.raceNumber)
        
        self.assertEqual(self.SingleRace.raceHeaderData[-1], 
                         {"Driver":"TOM WAGGONER", 
                          "Car#":9, 
                          "Laps":26, 
                          "RaceTime":"8:07.943", 
                          "Fast Lap":"17.063", 
                          "Behind":"6.008",
                          "Final Position":10})
        

singleRaceModified ='''Scoring Software by www.RCScoringPro.com                10:36:55 PM  01/14/2012

                               TACOMA R/C RACEWAY

4WD MODIFIED A2 Main                                          Round# 3, Race# 30

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
SCHOETLER, MICHAEL            #1         22         6:04.123         15.794                  
SMITH, LUKE            #2         22         6:06.384         15.759             2.261
Barnes, Marty            #3         22         6:06.896         16.095             2.773
BRIAN MUNN            #6         22         6:30.514         16.241            26.391
WALENTIA, JOHN            #5         21         6:07.583         15.908                  
AUSTIN SEIM            #7         21         6:10.454         16.248             2.871
HONSTAIN, ANTHONY            #8         21         6:13.906         16.425             6.323
DIBRINO, ANDY            #4         16         4:27.016         16.087                  
MATESA, TANNER            #9          4         1:20.392         17.097                  

 ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
 9/35.00 8/34.64 1/19.87 2/20.26 6/25.95 5/25.66 3/24.05 7/26.66 4/25.46        
 8/15.85 9/16.58 1/16.67 2/17.01 5/17.55 4/17.29 3/17.22 6/17.41 7/20.34        
                 1/16.25 2/16.73 5/16.25 4/16.43 3/17.05 6/16.59 7/17.48        
 1/15.79 2/16.27 3/16.48 4/16.16 7/17.28 6/17.24 5/16.83 8/17.42 9/17.09        
 1/15.90 2/15.89 3/16.36 4/16.08 7/16.21 6/16.44 5/17.09 8/17.11                
 1/16.06 2/15.75 3/16.33 4/16.59 8/19.65 5/16.44 6/17.78 7/17.10                
 1/15.85 2/16.34 3/16.59 4/16.68 8/19.06 5/16.69 6/16.93 7/16.42                
 1/15.86 2/16.13 3/16.20 4/16.48 8/16.08 5/16.53 6/16.73 7/16.49                
 1/16.16 2/15.87 3/16.11 4/16.19 8/16.84 5/16.51 6/16.95 7/16.89                
 1/17.00 2/16.49 3/16.22 4/16.08 8/16.10 5/16.35 6/16.78 7/16.76                
 1/15.82 2/18.69 3/16.41 4/16.32 8/16.17 5/16.55 6/16.61 7/17.81                
 1/16.32 2/16.08 3/16.10 4/16.75 8/16.84 5/17.12 6/16.85 7/17.20                
 1/16.23 2/15.96 3/16.32 4/16.31 7/18.92 5/16.62 6/16.49 8/19.52                
 1/17.29 2/17.14 3/16.57 4/16.60 7/16.66 5/16.24 6/19.76 8/17.98                
 1/18.50 2/16.23 3/16.62 4/16.60 7/16.13 5/16.74 6/17.72 8/16.99                
 1/16.30 2/16.34 3/16.17 4/16.11 7/16.99 5/16.92 6/16.84 8/17.78                
 1/16.60 2/16.65 3/16.97         6/18.70 4/16.89 5/18.24 7/16.73                
 2/18.49 3/19.97 1/16.51         5/16.46 4/16.77 6/18.71 7/16.70                
 2/16.06 3/15.95 1/16.09         5/16.38 4/17.32 6/16.24 7/17.04                
 1/16.56 3/16.33 2/17.91         5/15.90 4/16.34 6/18.22 7/16.96                
 1/15.98 3/16.29 2/16.61         5/17.36 4/16.82 6/17.26 7/20.27                
 1/16.39 2/16.69 3/17.43                 4/30.51                                
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
     22/     22/     22/     16/     21/     22/     21/     21/      4/        
  6:04.1  6:06.3  6:06.8  4:27.0  6:07.5  6:30.5  6:10.4  6:13.9  1:20.3        
'''
        
class TestSingleRaceModified(unittest.TestCase):

    def setUp(self):        
        self.SingleRace = SingleRace("testfilename", singleRaceModified.split('\n'))

    def test_racerOne(self):
        # Note - this test verifies racer one, it expects empty laps at the end
        # (since he did not complete the same number of laps as the leader). 
        expectedLaps = ["35.00", "15.85", "", "15.79", "15.90", "16.06", "15.85", "15.86", "16.16", "17.00", "15.82", "16.32", "16.23", "17.29", "18.50", "16.30", "16.60", "18.49", "16.06", "16.56", "15.98", "16.39"]
                        
        self.assertEqual(expectedLaps, self.SingleRace.lapRowsTime[0])

    def test_racerFour(self):
        expectedLaps = ["20.26", "17.01", "16.73", "16.16", "16.08", "16.59", "16.68", "16.48", "16.19", "16.08", "16.32", "16.75", "16.31", "16.60", "16.60", "16.11", "", "", "", "", "", ""]
        self.assertEqual(expectedLaps, self.SingleRace.lapRowsTime[3])

    def test_racerTen(self):
        expectedLaps = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
        self.assertEqual(len(expectedLaps), len(self.SingleRace.lapRowsTime[9]))
        self.assertEqual(expectedLaps, self.SingleRace.lapRowsTime[9])
        
    def test_headerData(self):
        self.assertEqual("TACOMA R/C RACEWAY", self.SingleRace.trackName)
        #self.assertEqual("8:09:03 PM  01/14/2012", self.SingleRace.date)
        self.assertEqual("4WD MODIFIED A2 Main", self.SingleRace.raceClass)
        self.assertEqual("3", self.SingleRace.roundNumber)
        self.assertEqual("30", self.SingleRace.raceNumber)
        
        self.assertEqual(self.SingleRace.raceHeaderData[-1], 
                         {"Driver":"MATESA, TANNER", 
                          "Car#":9, 
                          "Laps":4, 
                          "RaceTime":"1:20.392", 
                          "Fast Lap":"17.097", 
                          "Behind":"",
                          "Final Position":9})
        
        
singleRaceEarlyDrop = '''Scoring Software by www.RCScoringPro.com                8:29:37 PM  01/14/2012

                               TACOMA R/C RACEWAY

MODIFIED SHORT COURSE B Main                                  Round# 3, Race# 18

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
JONES, GREG			#2 		16		 5:33.539		 19.147		          
LEONARD, DMITRI			#4 		15		 5:24.548		 19.540		          
KILE, CORRY			#3 		14		 5:03.416		 19.153		          
MIKE CRAIG			#1 		 0		    0.000		       		          

 ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
         1/24.85 3/27.50 2/26.13                                                
         1/20.00 3/20.19 2/21.22                                                
         1/20.41 2/21.93 3/22.72                                                
         1/19.97 3/24.01 2/21.98                                                
         1/20.28 3/20.81 2/20.87                                                
         1/20.27 3/19.15 2/20.24                                                
         1/20.29 3/21.15 2/19.61                                                
         1/20.27 2/21.07 3/25.53                                                
         1/20.00 2/21.00 3/20.11                                                
         1/19.14 2/22.12 3/20.78                                                
         1/20.27 3/20.87 2/19.54                                                
         1/19.92 3/20.39 2/21.28                                                
         1/23.70 3/23.00 2/21.27                                                
         1/20.33 3/20.16 2/20.78                                                
         1/21.26         2/22.43                                                
         1/22.50                                                                
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
      0/     16/     14/     15/                                                
     0.0  5:33.5  5:03.4  5:24.5                                                

'''

class TestSingleRaceRacerDropped(unittest.TestCase):
 
    def setUp(self):        
        self.SingleRace = SingleRace("t1", singleRaceEarlyDrop.split('\n'))

    def test_racerOne(self):
        expectedLaps = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
        self.assertEqual(expectedLaps, self.SingleRace.lapRowsTime[0])

    def test_racerTwo(self):
        expectedLaps = ["24.85", "20.00", "20.41", "19.97", "20.28", "20.27", "20.29", "20.27", "20.00", "19.14", "20.27", "19.92", "23.70", "20.33", "21.26", "22.50"]
        self.assertEqual(expectedLaps, self.SingleRace.lapRowsTime[1])

singleRaceWithBrokeRacer = '''Scoring Software by www.RCScoringPro.com                9:10:24 PM  01/14/2012

                               TACOMA R/C RACEWAY

4WD MODIFIED A1 Main                                          Round# 3, Race# 22

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
SCHOETLER, MICHAEL            #1         23         6:15.854         15.552                  
SMITH, LUKE            #2         22         6:02.864         15.808                  
Barnes, Marty            #3         22         6:07.925         15.906             5.061
WALENTIA, JOHN            #5         22         6:11.373         16.058             8.509
DIBRINO, ANDY            #4         21         6:00.911         15.940                  
BRIAN MUNN            #6         21         6:05.274         16.200             4.363
HONSTAIN, ANTHONY            #8         20         6:03.032         16.662                  
MATESA, TANNER            #9         20         6:12.549         16.794             9.517
AUSTIN SEIM            #7         19         6:00.231         16.821                  
Gilley, Tres            #10         1           21.675                                 

 ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
         1/19.29 2/19.75 3/20.48 5/24.82 6/26.83 8/27.84 9/28.00 7/27.23 4/21.67
 1/34.59 2/16.38 3/16.58 4/16.56 5/17.24 6/17.17 9/22.09 8/19.50 7/18.80        
 3/20.47 1/16.36 2/17.13 4/18.92 5/16.96 6/16.54 9/17.50 7/17.30 8/21.02        
 3/16.10 1/15.95 2/16.21 4/16.16 5/16.60 6/16.92 9/20.37 7/16.83 8/18.06        
 3/16.23 1/16.11 2/16.46 4/16.51 5/16.29 6/16.83 9/18.54 7/16.66 8/18.99        
 3/15.55 1/15.80 2/15.90 4/16.75 5/16.69 6/17.77 9/18.69 7/16.92 8/17.18        
 3/15.82 1/16.19 2/16.32 4/16.21 5/16.54 6/17.10 9/18.83 7/17.66 8/19.18        
 2/16.22 1/15.99 3/17.15 5/21.69 4/16.45 6/17.29 9/17.39 7/17.37 8/18.34        
 2/15.68 1/16.01 3/16.24 5/16.06 4/16.39 6/16.68 9/17.73 7/18.47 8/18.11        
 2/15.73 1/17.36 3/16.38 5/16.22 4/16.33 6/16.63 9/20.26 7/19.29 8/17.18        
 2/15.90 1/15.86 3/16.59 5/16.32 4/16.32 6/16.37 9/17.91 7/17.53 8/17.43        
 2/16.05 1/16.57 3/16.32 5/15.94 4/16.23 6/16.33 9/17.59 7/16.74 8/19.66        
 2/16.03 1/16.04 3/16.51 5/19.00 4/16.39 6/16.20 9/17.98 7/16.73 8/17.58        
 2/15.99 1/15.80 3/16.10 5/16.51 4/16.24 6/17.00 9/17.98 7/16.81 8/18.84        
 2/15.95 1/16.21 3/16.42 5/17.65 4/16.86 6/17.63 9/17.79 7/17.33 8/17.05        
 2/15.79 1/15.99 3/16.68 5/17.70 4/16.06 6/17.61 9/18.40 7/17.71 8/17.88        
 1/17.01 2/18.32 3/16.56 5/17.23 4/16.37 6/16.66 9/17.62 7/17.14 8/16.79        
 1/15.79 2/16.78 3/16.09 5/16.29 4/16.51 6/17.15 9/18.83 7/16.99 8/17.77        
 1/16.05 2/16.18 3/17.97 5/16.28 4/17.32 6/16.63 9/16.82 7/16.92 8/17.27        
 1/16.03 2/17.22 3/17.44 5/16.14 4/16.21 6/17.16         7/21.04 8/18.10        
 1/15.80 2/16.20 3/16.05 5/16.22 4/16.38 6/16.69                                
 1/15.73 2/16.16 3/16.97         4/16.05                                        
 1/17.27                                                                        
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
     23/     22/     22/     21/     22/     21/     19/     20/     20/      1/
  6:15.8  6:02.8  6:07.9  6:00.9  6:11.3  6:05.2  6:00.2  6:03.0  6:12.5    21.6
'''

class TestSingleRaceBrokeRacer(unittest.TestCase):

    def setUp(self):        
        self.SingleRace = SingleRace("testfilename", singleRaceWithBrokeRacer.split('\n'))
        
    def test_headerData(self):
        self.assertEqual("TACOMA R/C RACEWAY", self.SingleRace.trackName)
        #self.assertEqual("8:09:03 PM  01/14/2012", self.SingleRace.date)
        self.assertEqual("4WD MODIFIED A1 Main", self.SingleRace.raceClass)
        self.assertEqual("3", self.SingleRace.roundNumber)
        self.assertEqual("22", self.SingleRace.raceNumber)
        
        # Gilley, Tres            #10         1           21.675                      
        self.assertEqual(self.SingleRace.raceHeaderData[9], 
                         {"Driver":"Gilley, Tres", 
                          "Car#":10, 
                          "Laps":1, 
                          "RaceTime":"", 
                          "Fast Lap":"21.675", 
                          "Behind":"",
                          "Final Position":10})
        # SCHOETLER, MICHAEL            #1         23         6:15.854         15.552      
        self.assertEqual(self.SingleRace.raceHeaderData[0], 
                         {"Driver":"SCHOETLER, MICHAEL", 
                          "Car#":1, 
                          "Laps":23, 
                          "RaceTime":"6:15.854", 
                          "Fast Lap":"15.552", 
                          "Behind":"",
                          "Final Position":1})
        
        
singleRaceWithPaceData = '''Scoring Software by www.RCScoringPro.com                10:05:41 PM  03/18/2011

                               TACOMA R/C RACEWAY

STOCK BUGGY B Main                                            Round# 3, Race# 1

________________________Driver___Car#____Laps____RaceTime____Fast Lap___Behind_
FRANK, JON            #5         18         6:09.135         19.183                  
JOHNSON, JJ            #6         18         6:16.021         19.456             6.886
CADDELL, ANDREW            #3         17         6:05.638         19.211                  
JOHNSON, JAMES            #7         16         5:40.504         18.829                  
MARGESON, EVAN            #1         16         6:06.879         19.568            26.375
BUTLER, BRANDON            #2         15         6:12.022         19.415                  

 ___1___ ___2___ ___3___ ___4___ ___5___ ___6___ ___7___ ___8___ ___9___ ___10__
 6/37.57 5/32.86 4/31.55         3/29.97 2/29.45 1/29.18                        
 10/15.7 11/01.4 12/18.7         13/29.7 13/22.8 13/19.3                        

 6/20.12 5/22.57 4/20.81         1/19.34 3/22.50 2/22.56                        
 13/15.1 13/00.3 14/06.5         15/09.8 14/03.7 14/02.1                        

 6/19.56 5/20.44 4/21.30         1/20.43 3/20.52 2/19.76                        
 14/00.6 15/19.3 15/08.3         16/12.0 15/02.3 16/21.3                        

 6/24.54 4/21.61 3/19.91         1/19.21 2/19.79 5/28.67                        
 15/21.8 15/05.6 16/14.3         17/18.1 16/09.0 15/15.7                        

 5/20.36 6/27.97 3/20.23         1/19.82 2/19.94 4/20.20                        
 15/06.5 15/16.4 16/04.2         17/09.8 17/21.5 15/01.1                        

 5/19.68 6/20.04 3/19.64         1/20.17 2/19.45 4/18.82                        
 16/18.3 15/03.7 17/18.1         17/05.4 17/13.0 16/11.2                        

 6/23.51 5/19.41 3/19.21         1/20.24 2/20.38 4/19.17                        
 16/18.0 16/16.9 17/10.7         17/02.3 17/09.2 16/02.0                        

 5/23.20 6/26.41 3/19.66         1/19.59 2/19.87 4/19.09                        
 16/17.1 16/22.6 17/06.2         18/19.8 17/05.3 17/17.1                        

 5/20.18 6/23.97 2/20.40         1/23.43 3/22.77 4/21.67                        
 16/11.1 16/22.7 17/04.0         17/03.1 17/07.7 17/16.2                        

 5/22.65 6/24.61 2/20.63         1/20.93 3/19.65 4/18.97                        
 16/10.3 16/23.8 17/02.7         17/02.4 17/04.4 17/10.8                        

 5/24.19 6/28.28 2/19.58         1/19.18 3/19.45 4/19.32                        
 16/11.8 15/05.7 17/00.0         18/20.2 17/01.3 17/06.9                        

 5/21.53 6/26.16 2/20.39         1/19.26 3/20.09 4/19.92                        
 16/09.5 15/07.9 18/20.0         18/17.4 18/20.8 17/04.6                        

 5/21.30 6/28.63 4/24.88         1/19.86 2/21.92 3/20.53                        
 16/07.3 15/12.7 17/03.8         18/15.9 17/00.7 17/03.4                        

 5/26.81 6/23.90 4/19.73         1/19.38 2/19.90 3/19.87                        
 16/11.7 15/11.6 17/01.8         18/13.9 18/20.2 17/01.6                        

 5/21.04 6/25.10 4/26.10         1/19.67 2/19.63 3/19.90                        
 16/09.4 15/12.0 17/07.3         18/12.6 18/18.4 17/00.0                        

 5/20.55         4/21.47         1/19.48 2/19.74 3/22.81                        
 16/06.8         17/07.1         18/11.2 18/17.0 17/01.7                        

                 3/20.07         1/19.59 2/21.16                                
                 17/05.6         18/10.1 18/17.2                                

                                 1/19.51 2/19.73                                
                                 18/09.1 18/16.0                                
 ------- ------- ------- ------- ------- ------- ------- ------- ------- -------
     16/     15/     17/             18/     18/     16/                        
  6:06.8  6:12.0  6:05.6          6:09.1  6:16.0  5:40.5      
'''
        
class TestSingleRaceWithPaceData(unittest.TestCase):
 
    #def setUp(self):        
        #self.assertRaises(Exception, SingleRace, "t1", singleRaceWithPaceData.split('\n'))
        #self.SingleRace = SingleRace("t1", singleRaceEarlyDrop.split('\n'))
        
    def test_notSupported(self):
        self.assertRaises(Exception, SingleRace, "t1", singleRaceWithPaceData.split('\n'))    
        #expectedLaps = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
        #self.assertEqual(expectedLaps, self.SingleRace.lapRowsTime[0])


if __name__ == '__main__':
    unittest.main()
    
    
    
