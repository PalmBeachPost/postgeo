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

GoogleAPIkey = creds.access['GoogleAPIkey']

geolocator = GoogleV3(api_key=GoogleAPIkey, timeout=10)

# Let's set up a buffer, in case we're running with a sorted list that has overlapping points.


def main():
    lastfulladdy = "1600 Pennsylvania Ave. NW, Washington, D.C. 20500"
    lastlat = "-77.036482"
    lastlong = "38.897667"
    lastaccuracy = "Rooftop"
    lastlatlong = "-77.036482, 38.897667"
    inputfilename = args.filename
    buffersize = 1

    outputfilename = inputfilename[:inputfilename.rfind(".")] + "-geo" + inputfilename[inputfilename.rfind("."):]

    if os.path.isfile(outputfilename):
        message = "File {} exists, proceeding will overwrite(y or n)? "
        proceed_prompt = get_input(message.format(outputfilename))
        if proceed_prompt.lower() == 'y':
            pass
        else:
            print('Aborting . . .')
            exit()

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
                fulladdy = row[-1]
                if fulladdy == lastfulladdy:
                    print("Repeated address found for " + fulladdy)
                    row.append(lastlat)
                    row.append(lastlong)
                    row.append(lastaccuracy)
                    row.append(lastlatlong)
                    put.writerow(row)
                    outputfile.flush()
                    os.fsync()          # Force writes after each line. Should be no performance hit because geocoding
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
                        put.writerow(row)
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
                        else:
                            print("Dropping row: No address listed in this row: " + str(row))
                    except GeocoderTimedOut:
                        print("Geocoder service timed out on this row: " + str(row))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Address file to geocode")
    parser.add_argument('filename', metavar='filename', help='CSV file containing addresses to be geocoded')
    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(1)
    get_input = input

    if sys.version_info[:2] <= (2, 7):
        get_input = raw_input

    if args.filename.lower().endswith('.csv'):
        print(args.filename)
        main()
    else:
        print("File must be of type CSV and end with .csv extension")
