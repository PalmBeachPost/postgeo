#!/python/python27
from geopy.geocoders import GoogleV3
import json
import sys
import csv
import time
import creds

GoogleAPIkey=creds.access['GoogleAPIkey']

geolocator = GoogleV3(api_key=GoogleAPIkey, timeout=10)
#### This thing assumes you're throwing it at a CSV that ends in .csv or .CSV or similar.
#### Your full address field -- "1600 Pennsylvania Ave. NW, Washington, D.C., USA" -- MUST be the final column.



# Let's set up a buffer, in case we're running with a sorted list that has overlapping points.
lastfulladdy="1600 Pennsylvania Ave. NW, Washington, D.C. 20500"
lastlat="-77.036482"
lastlong="38.897667"
lastaccuracy="Rooftop"
lastlatlong="-77.036482, 38.897667"

try:
	inputfilename=sys.argv[1]
	outputfilename=inputfilename[:inputfilename.rfind(".")] + "-geo" +inputfilename[inputfilename.rfind("."):]
	with open(outputfilename, 'wb') as outputfile:
		put = csv.writer(outputfile)
		with open(inputfilename, 'rb') as inputfilehandle:
			rows = csv.reader(inputfilehandle)
			headers=rows.next()
			headers.append("lat")
			headers.append("long")
			headers.append("accuracy")
			headers.append("latlong")
			put.writerow(headers)
#			print headers
			for row in rows:
#				print row
				fulladdy=row[-1]
				if fulladdy == lastfulladdy:
					print "Repeated address found for " + fulladdy
					row.append(lastlat)
					row.append(lastlong)
					row.append(lastaccuracy)
					row.append(lastlatlong)
					put.writerow(row)
				else:					
					location = geolocator.geocode(fulladdy)
					try:
						mylatlong = str(location.latitude) + ", " + str(location.longitude)
						mylat=str(location.latitude)
						mylong=str(location.longitude)
						myaccuracy=location.raw["geometry"]["location_type"]
						row.append(mylat)
						row.append(mylong)
						row.append(myaccuracy)
						row.append(mylatlong)
						put.writerow(row)
						print "Found: " + fulladdy
						lastfulladdy=fulladdy
						lastlat=mylat
						lastlong=mylong
						lastaccuracy=myaccuracy
						time.sleep(1)
					except AttributeError:
						print "Something went wrong on " + fulladdy	
except IndexError:
	print 'Run this script with the CSV filename you want to geocode, like "postgeo.py mydata.csv"'
	print 'Geocodable location data must be in the last field.'
	
