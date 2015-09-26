#!/usr/bin/env python
"""
This script will take a lat-long pair (e.g., "-80.123, 45.678") in the final column, and determine if any other lines are at that exactly named pair. If so, it scatters them around in a circle.

So if other points are adjacent or identical but differently named (-80.123 vs. -80.1230), this won't help much. It works for what it is, and it's not meant to do more.

Scattering distance right now is hard-coded (see "meters=100" around line 85).

This may use a lot of memory on large datasets, so you might want it to work off a database. I didn't.
"""

from __future__ import print_function
import argparse
import csv
import sys

from geopy.distance import VincentyDistance

masterdict = {}
flagonsolo = 987654321

# verbose = 1				## Comment this line out if you don't want feedback.


def set_spot(latlong):
    if latlong in masterdict.keys():
        masterdict[latlong][0] += 1
    else:
        masterdict[latlong] = [1,-1]

# So if we have a value, we know this spot already and we should add to the count.
# If we don't have a value, we need to create one, set to the 1.

def get_spot(latlong, value):
    value = masterdict[latlong][1]
    if value == flagonsolo:
        pass
    else:
        masterdict[latlong][1] = value + 1
    return (latlong, value)
# Let's peel the latest index count off, and increment by 1, unless this is the only spot at the location.


def main(verbose=0):
    inputfilename = args.filename
    outputfilename = inputfilename[:inputfilename.rfind(".")] + "-jitter" + inputfilename[inputfilename.rfind("."):]
    with open(inputfilename, 'r') as inputfilehandle:
        rows = csv.reader(inputfilehandle)
        headers = next(rows)
        for row in rows:
            latlong = row[-1]
        # We're only grabbing latlong from last field
            set_spot(latlong)
        # masterdict should now have all latlongs, and their counts
        # and inputfilehandle should now be closed.
        # Let's now set up our spot dictionary:

    for key in masterdict:
        if masterdict[key][0] == 1:
            masterdict[key][1] = flagonsolo
        else:
            masterdict[key][1] = 0

## We should be ready to start processing. Our masterdict holds a list keyed to each unique latlong in our
## source CSV. [0] holds how many values are at that index. [1] holds an index to which one of those things
## we're processing, so we know where to jigger it.
## flagonsolo gives us a value that says, "Only one point at this latlong. Don't mess with it."

    with open(outputfilename, 'w') as outputfile:
        put = csv.writer(outputfile)
        with open(inputfilename, 'r') as inputfilehandle:
            rows = csv.reader(inputfilehandle)
            headers = next(rows)
            headers.append("RowsHere")
            headers.append("latlongspaced")
            put.writerow(headers)
            for row in rows:
                latlong = row[-1]
                value = -700
#				get_spot(latlong, value)
                Bud, Schlitz = get_spot(latlong, value)

#				print "Tequila" + str(value)
#				print "Schlitz " + str(Schlitz)
                value = Schlitz
                if value == flagonsolo:
                    latlongspaced = latlong
                    areacount = 1
                    bearing = "N/A"
                else:
                    areacount = masterdict[latlong][0]
                    bearing = (value * 360 / areacount)
                    destination = VincentyDistance(meters=100).destination(latlong, bearing)
                    latlongspaced = str(destination.latitude) + ", " + str(destination.longitude)
                if verbose == 1:
                    print("Latlong:" + "\t" + latlong + "\t" + "Area count:" + "\t" + str(areacount) + "\t" + "Index count:" + "\t" + str(value) + "\t" + "Spaced:" + "\t" + latlongspaced + "\t" + "Bearing " + "\t" + str(bearing))
                row.append(str(areacount))
                row.append(latlongspaced)
                put.writerow(row)
    if verbose == 1:
        linecount = 0
        for key in masterdict:
            linecount = linecount + masterdict[key][0]
        print("Processed " + str(linecount) + " rows at " + str(len(masterdict)) + " locations.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Lat-longs to scatter")
    parser.add_argument('filename', metavar='filename', help='CSV file containing Lat-longs to scatter')
    parser.add_argument("-v", help="turn on verbose output", action="store_true")
    args = parser.parse_args()
    if args.filename.lower().endswith('.csv'):
        if args.v:
            main(verbose=1)
        else:
            main()
    else:
        print("File must be of type CSV and end with .csv extension")