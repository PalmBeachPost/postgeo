#!/usr/bin/env python
"""
This script will take a lat-long pair (e.g., "-80.123, 45.678") in the final column, and determine if any
other lines are at that exactly named pair. If so, it scatters them around in a circle.

So if other points are adjacent or identical but differently named (-80.123 vs. -80.1230), this won't help
much. It works for what it is, and it's not meant to do more.

Scattering distance can be specified on the command-line using the -m flag).

This may use a lot of memory on large datasets, so you might want it to work off a database. I didn't.
"""

from __future__ import print_function
import argparse
import csv
import os
import sys

from geopy.distance import VincentyDistance

masterdict = {}
flagonsolo = 987654321

output_string = "Latlong: {:20} Area count: {} Index count: {:>9} Spaced: {:>} Bearing {}"
processed_string = "Processed {} rows at {} locations."


def set_spot(latlong):
    if latlong in masterdict.keys():
        masterdict[latlong][0] += 1
    else:
        masterdict[latlong] = [1, -1]

# So if we have a value, we know this spot already and we should add to the count.
# If we don't have a value, we need to create one, set to the 1.


def get_spot(latlong):
    indexvalue = masterdict[latlong][1]
    if indexvalue == flagonsolo:
        pass
    else:
        masterdict[latlong][1] = indexvalue + 1
    return (indexvalue)
# Let's peel the latest index count off, and increment by 1, unless this is the only spot at the location.


def main(spacing, verbose=0):
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

# We should be ready to start processing. Our masterdict holds a list keyed to each unique latlong in our
# source CSV. [0] holds how many values are at that index. [1] holds an index to which one of those things
# we're processing, so we know where to jigger it.
# flagonsolo gives us a value that says, "Only one point at this latlong. Don't mess with it."

    if os.path.isfile(outputfilename):
        message = "File {} exists, proceeding will overwrite(y or n)? "
        proceed_prompt = get_input(message.format(outputfilename))
        if proceed_prompt.lower() == 'y':
            pass
        else:
            print('Aborting . . .')
            exit()

    with open(outputfilename, 'w') as outputfile:
        put = csv.writer(outputfile, lineterminator='\n')
        with open(inputfilename, 'r') as inputfilehandle:
            rows = csv.reader(inputfilehandle)
            headers = next(rows)
            headers.append("RowsHere")
            headers.append("latlongspaced")
            put.writerow(headers)
            for row in rows:
                latlong = row[-1]
                indexvalue = get_spot(latlong)
                if indexvalue == flagonsolo:
                    latlongspaced = latlong
                    areacount = 1
                    bearing = -1
                else:
                    areacount = masterdict[latlong][0]
                    bearing = (indexvalue * 360 / areacount)
                    destination = VincentyDistance(meters=spacing).destination(latlong, bearing)
                    latlongspaced = str(destination.latitude) + ", " + str(destination.longitude)
                if verbose == 1:
                    print(output_string.format(latlong, areacount, indexvalue, latlongspaced, bearing))
                row.append(str(areacount))
                row.append(latlongspaced)
                put.writerow(row)
    if verbose == 1:
        linecount = 0
        for key in masterdict:
            linecount = linecount + masterdict[key][0]
        print(processed_string.format(linecount, len(masterdict)))

if __name__ == '__main__':
    # TODO: add flag for meters for spacing.
    parser = argparse.ArgumentParser(description="Lat-longs to scatter")
    parser.add_argument('filename', metavar='filename', help='CSV file containing Lat-longs to scatter')
    parser.add_argument("-v", help="turn on verbose output", action="store_true")
    parser.add_argument("-m", help="set distance in meters for spacing", default=100, type=int)
    args = parser.parse_args()
    get_input = input
    if sys.version_info[:2] <= (2, 7):
        get_input = raw_input
    if args.filename.lower().endswith('.csv'):
        if args.v:
            main(verbose=1, spacing=args.m)
        else:
            main(spacing=args.m)
    else:
        print("File must be of type CSV and end with .csv extension")