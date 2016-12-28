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

try:
    geocachepath = creds.setup['geocachepath']
except KeyError:
    print("You need to figure a setup['geocachepath'] within creds.py to meet the new file format.")
    print("Check the sample on Github.com/PalmBeachPost/postgeo to figure out how to update your version.")
    sys.exit()

geolocator = GoogleV3(api_key=GoogleAPIkey, timeout=10)
global timedelay
timedelay = 1


def timedisplay(timediff):
    m, s = divmod(timediff, 60)
    h, m = divmod(m, 60)
    return("%d:%02d:%02d" % (h, m, s))


def main(geocacheflag):
    # Start building caching as we go along.
    # Format: Full address as key, value as a tuple of lat, long, accuracy, lat-long
    geocache = {"1600 Pennsylvania Ave. NW, Washington, D.C. 20500":
                ("-77.036482", "38.897667", "Rooftop", "-77.036482, 38.897667")}
    inputfilename = args.filename
    buffersize = 1
    totalrows = 0
    rowsprocessed = 0
    lastpercentageprocessed = 0
    starttime = time.clock()

    outputfilename = inputfilename[:inputfilename.rfind(".")] + "-geo" + inputfilename[inputfilename.rfind("."):]

    if os.path.isfile(outputfilename):
        message = "File {} exists, proceeding will overwrite(y or n)? "
        proceed_prompt = get_input(message.format(outputfilename))
        if proceed_prompt.lower() == 'y':
            pass
        else:
            print('Aborting . . .')
            exit()

# Read from geocache.csv file, if selected as option at command line.
    if geocacheflag == 1:
        if not os.path.isfile(geocachepath):
            print("Using " + geocachepath + " file to speed up results.")
            with open(geocachepath, 'wb') as cachefilehandle:
                        # with open(geocachepath, 'wb', buffersize) as cachefilehandle:
                cacheput = csv.writer(cachefilehandle)
                geocacheheader = ['fulladdy', 'lat', 'long', 'accuracy', 'latlong']
                cacheput.writerow(geocacheheader)
                for fulladdy in geocache:
                    mylat, mylong, myaccuracy, mylatlong = geocache[fulladdy]
                    myrow = [fulladdy, mylat, mylong, myaccuracy, mylatlong]
                    cacheput.writerow(myrow)

        else:       # If we have that geocachepath file
            print("Using " + geocachepath + " file to speed up results.")
            with open(geocachepath, 'rU') as cachefilehandle:
                rows = csv.reader(cachefilehandle)
                rows.next()        # Skip header row
                for row in rows:
                    if len(row) > 4:        # If we have a blank row, skip it.
                        if row[0] not in geocache:          # check for repeats of fulladdy as key
                            geocache[row[0]] = (row[1], row[2], row[3], row[4])
                        # Geocache should be fully set up now.
# Cache file should now be closed. Let's open it again to append to it.
        cachefilehandle = open(geocachepath, "ab")       # Open to append
        cacheput = csv.writer(cachefilehandle)
#
# Note we still have the file handle open for our cache. This is a good thing, but we do need to remember to write and close.
#

# Next, we open the source data CSV entirely to get a row count, then close it.
    with open(inputfilename, 'rU') as inputfilehandle:
            rows = csv.reader(inputfilehandle)
            for row in rows:
                totalrows += 1
            print(str(totalrows) + " rows to be processed.")

    with open(outputfilename, 'wb', buffersize) as outputfile:
        put = csv.writer(outputfile)
        with open(inputfilename, 'rU') as inputfilehandle:
            rows = csv.reader(inputfilehandle)
            headers = next(rows)
            headers.append("lat")
            headers.append("long")
            headers.append("accuracy")
            headers.append("latlong")
            put.writerow(headers)
            # print headers
            for row in rows:
                # print(row)
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

                    outputfile.flush()  # Force writes after each line. Should be no performance hit because geocoding is so slow.

                else:
                    if len(fulladdy) > 0:
                        location = geolocator.geocode(fulladdy.replace("'", ""))
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
                                endtime = time.clock()
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
                            if geocacheflag == 1:
                                cacheput.writerow([fulladdy, mylat, mylong, myaccuracy, mylatlong])
                                cachefilehandle.flush()
                                # os.fsync()  HEY!

                            time.sleep(timedelay)       # Necessary to avoid getting shut out

                        except AttributeError:
                            if len(fulladdy) > 0:
                                print("Dropping row: Something went wrong on " + fulladdy)
                                time.sleep(timedelay)
                                rowsprocessed += 1
                            else:
                                print("Dropping row: No address listed in this row: " + str(row))
                                rowsprocessed += 1
                        except GeocoderTimedOut:
                            print("Geocoder service timed out on this row: " + str(row))
                            print("You should probably re-run this on the next pass.")
                            time.sleep(timedelay)
                            rowsprocessed += 1
                    else:           # If fulladdy was blank
                            print("Dropping row: No address listed in this row: " + str(row))
                            rowsprocessed += 1

    if geocacheflag == 1:
        cachefilehandle.flush()
        cachefilehandle.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="postgeo.py is a command-line geocoder tool.")
    parser.add_argument('filename', metavar='filename', help='CSV file containing addresses to be geocoded')
    parser.add_argument('-c', help='Use geocache.csv file to speed up coding and recoding. Now the default.', action="store_true")
    parser.add_argument('-n', help='Do NOT use geocache file Use geocache.csv file to speed up geocoding and recoding.', action="store_true")
    parser.add_argument('-t', type=float, nargs=1, default=1, action="store", help='Enter a delay between queries measured in seconds, such as 1 or 0.5.')
    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(1)
    get_input = input

    if sys.version_info[:2] <= (2, 7):
        get_input = raw_input
        
    timedelay = args.t[0]
        
    if args.n:
        geocacheflag = 0
    else:
        geocacheflag = 1
    
    if args.c:      # If we get both options
        geocacheflag = 1
    if geocacheflag == 1:
        print("Speeding up results with cached file " + geocachepath)
        
    if args.filename.lower().endswith('.csv'):
        if os.path.isfile(args.filename):
            print("Beginning to process " + args.filename)
            main(geocacheflag)
        else:
            print("File " + args.filename + " not found.")

    else:
        print("File must be of type CSV and end with .csv extension")
