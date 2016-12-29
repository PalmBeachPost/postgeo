Geographic tools for CSV files
============================

These small command-line tools are designed to aid in geocoding files, and in jittering, or scattering, points that overlap.

They run with Python. You'll need to install two helper files with one command, like this:

<code>pip install -r requirements.txt</code>

You'll want to edit creds.py and add your Google API key. Don't have one? Get it here:
https://console.developers.google.com/project/_/apiui/credential

In that creds.py file you'll also need to have a filename for a CSV that will be used to cache results. The default should work fine.


Command-line geocoding
----------------------

postgeo.py will handle geocoding for you; it simply requires a full address in the final column, in a regularly formatted CSV file. So a full address won't be simply "1600 Pennsylvania Ave," but rather "1600 Pennsylvania Ave. N.W., Washington, D.C." or similar.

It'll geocode an address roughly half a second using your Google API key. Remember you need to follow all the Google requirements, including you geocoding for a Google map, and recognizing it'll die after you hit the limit, which may be about 2,500 addresses per day.

With about two geocoded addresses per second, you'll get roughly 100 per minute, 6,000 per hour. You'd hit your daily (free) limit in about half an hour. Google will let you buy more capacity; the rate at the end of 2016 was $1 for 2,000 extra addresses.

Simply run it like this:

<code>postgeo.py myfile.csv</code>

It'll spit back a myfile-geo.csv.

Use postgeo.py with the -n flag if you do not want to store your cached results for later reuse. This is no longer the default, as you may wind up recoding substantially the same addresses a bunch of times. You can also force a time delay with -t followed by a number; -t .5 will give you a half-second delay between queries, while -t 3 will give you three seconds between.


Command-line jittering or clustering
------------------------------------

cellspacer.py is designed to take data that has overlapping points and spread them out in a circular pattern.

Force a distance -- the radius of spread -- with <code>-m 100</code> for a 100-meter radius (giving a circle about as wide as two football fields). At the neighborhood level, <code>-m 15</code> gives a good effect. If you're trying to show a whole city, something like 5,000 meters -- a radius of about three miles, a diameter of about six miles -- may work well. In other words, you need to pick a scale.

Cellspacer will work where a latitude-longitude pair is in the last column. Most often, you'll be feeding it something that came out of the postgeo.py geocoder, e.g.:

<code>postgeo.py mydata.csv

cellspacer -m 15 mydata-geo.csv</code>


This runs instantaneously on a dataset of 1,000 rows, but it may also be memory intensive. If you have problems on a much larger data set, let us know and we can suggest and possibly test some workarounds.

In general
----------

Pull requests are welcomed, as are suggestions.

This began as a project for Palm Beach Newspapers, owner of The Palm Beach Post and Palm Beach Daily News, a Cox Media Group company. Micheal Beatty, @amikiri , stepped in from the blue and offered some wonderful improvements.