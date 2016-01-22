#!/usr/bin/env python
"""
This thing assumes you're throwing it at a CSV that ends in .csv or .CSV or similar.
Your full address field -- "1600 Pennsylvania Ave. NW, Washington, D.C., USA" -- MUST be the final column.
"""

from __future__ import print_function
import argparse
import sys
import csv
import os
import time

from geopy.geocoders import GoogleV3
from geopy.exc import GeocoderTimedOut

import creds

try:
    GoogleAPIkey = creds.setup['GoogleAPIkey']
except KeyError:
    print("You need to configure your Google geocoding API key in creds.py. Instructions are there.")
    print("It's not as scary as it sounds, if you've never done this before.")
    sys.exit()
if GoogleAPIkey == "GetYourKeyUsingTheDirectionsAbove":
    print("You need to configure your Google geocoding API key in creds.py. Instructions are there.")
    print("It's not as scary as it sounds, if you've never done this before.")
    sys.exit()
    
    
geocachepath = creds.setup['geocachepath']
    
geolocator = GoogleV3(api_key=GoogleAPIkey, timeout=10)

def timedisplay(timediff):
    m, s = divmod(timediff, 60)
    h, m = divmod(m, 60)
    return("%d:%02d:%02d" % (h, m, s))

def main(geocacheflag):
    ## Start building caching as we go along.
    ## Format: Full address as key, value as a tuple of lat, long, accuracy, lat-long
    geocache = { "1600 Pennsylvania Ave. NW, Washington, D.C. 20500":
        ("-77.036482", "38.897667", "Rooftop", "-77.036482, 38.897667") }
    inputfilename = args.filename
    buffersize = 1
    totalrows=0
    rowsprocessed=0
    lastpercentageprocessed=0
    starttime=time.clock()

    outputfilename = inputfilename[:inputfilename.rfind(".")] + "-geo" + inputfilename[inputfilename.rfind("."):]

    if os.path.isfile(outputfilename):
        message = "File {} exists, proceeding will overwrite(y or n)? "
        proceed_prompt = get_input(message.format(outputfilename))
        if proceed_prompt.lower() == 'y':
            pass
        else:
            print('Aborting . . .')
            exit()

## Read from geocache.csv file, if selected as option at command line.            
    if geocacheflag == 1:
        if os.path.isfile(geocachepath):
            print("Using " + geocachepath + " file to speed up results.")
            with open('geocache.csv', 'rU') as cachefilehandle:
                rows = csv.reader(cachefilehandle)
                rows.next()        # Skip header row
                for row in rows:
                    if row[0] not in geocache:          # check for repeats of fulladdy as key
                        geocache[row[0]] = (row[1], row[2], row[3], row[4])
                        # Geocache should be fully set up now.

            
## Next, we open the source data CSV entirely to get a row count, then close it.
    with open(inputfilename, 'rU') as inputfilehandle:
            rows = csv.reader(inputfilehandle)
            for row in rows:
                totalrows += 1
            print(str(totalrows) + " rows to be processed.")

    with open(outputfilename, 'wb', buffersize) as outputfile:
#        put = csv.writer(outputfile, lineterminator='\n')
        put = csv.writer(outputfile)
        with open(inputfilename, 'rU') as inputfilehandle:
            rows = csv.reader(inputfilehandle)
            headers = next(rows)
            headers.append("lat")
            headers.append("long")
            headers.append("accuracy")
            headers.append("latlong")
            put.writerow(headers)
#            print headers
            for row in rows:
#                print(row)
                fulladdy = row[-1]      # Last column of the file
                if fulladdy in geocache:
                    print("\tFound in cache: " + fulladdy)
                    mylat, mylong, myaccuracy, mylatlong = geocache[fulladdy]
                    row.append(mylat)
                    row.append(mylong)
                    row.append(myaccuracy)
                    row.append(mylatlong)
                    put.writerow(row)
                    rowsprocessed += 1
                    
                    outputfile.flush()
##                    os.fsync()        # Disabled. Error after ~20 successes: fsync() takes exactly one argument (0 given)  
                                        # Force writes after each line. Should be no performance hit because geocoding
                                        # is so slow.
                else:
                    location = geolocator.geocode(fulladdy)
                    try:
                        mylatlong = str(location.latitude) + ", " + str(location.longitude)
                        mylat = str(location.latitude)
                        mylong = str(location.longitude)
                        myaccuracy = location.raw["geometry"]["location_type"]
                        row.append(mylat)
                        row.append(mylong)
                        row.append(myaccuracy)
                        row.append(mylatlong)
                        geocache[fulladdy] = (mylat, mylong, myaccuracy, mylatlong)
                        rowsprocessed += 1
                        percentageprocessed = int(100*rowsprocessed/totalrows)
                        if percentageprocessed > lastpercentageprocessed:
                            lastpercentageprocessed = percentageprocessed
                            endtime=time.clock()
                            timediff = (endtime-starttime)
                            print(str(percentageprocessed) + "% processed in " + timedisplay(timediff) + ". ETA: " + timedisplay((timediff/rowsprocessed)*(totalrows-rowsprocessed)) + ".")
                            
                        put.writerow(row)
                        outputfile.flush()
                        print("Found: " + fulladdy)
                        lastfulladdy = fulladdy
                        lastlat = mylat
                        lastlong = mylong
                        lastaccuracy = myaccuracy
                        lastlatlong = mylatlong
                        time.sleep(1)       # Necessary to avoid getting shut out
                    except AttributeError:
                        if len(fulladdy)>0:
                            print("Dropping row: Something went wrong on " + fulladdy)
                            rowsprocessed += 1
                        else:
                            print("Dropping row: No address listed in this row: " + str(row))
                            rowsprocessed += 1
                    except GeocoderTimedOut:
                        print("Geocoder service timed out on this row: " + str(row))
                        rowsprocessed += 1

## Done geocoding now. Let's write geocache.csv if -c flag was selected.
    if geocacheflag == 1:
        with open(geocachepath, 'wb', buffersize) as cachefilehandle:
            put = csv.writer(cachefilehandle)
            geocacheheader = ['fulladdy', 'lat', 'long', 'accuracy', 'latlong']
            put.writerow(geocacheheader)
            for fulladdy in geocache:
                mylat, mylong, myaccuracy, mylatlong = geocache[fulladdy]
                myrow = [ fulladdy, mylat, mylong, myaccuracy, mylatlong ]
                put.writerow(myrow)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Address file to geocode")
    parser.add_argument('filename', metavar='filename', help='CSV file containing addresses to be geocoded')
    parser.add_argument('-c', help='Use geocache.csv file to speed up coding and recoding.', action="store_true")
    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(1)
    get_input = input

    if sys.version_info[:2] <= (2, 7):
        get_input = raw_input

    if args.c:
        geocacheflag=1
    else:
        geocacheflag=0
        
    if args.filename.lower().endswith('.csv'):
        if os.path.isfile(args.filename):
            print("Beginning to process " + args.filename)
            main(geocacheflag)
        else:
            print("File " + args.filename + " not found.")

    else:
        print("File must be of type CSV and end with .csv extension")
