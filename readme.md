Geographic tools for CSV files
============================

These small command-line tools are designed to aid in geocoding files, and in jittering, or scattering, points that overlap.

They run with Python. You'll need to install one helper file ("pip install geopy")

You'll want to edit creds.py and add your Google API key. Don't have one? Get it here:
https://console.developers.google.com/project/_/apiui/credential


Command-line geocoding
----------------------

postgeo.py will handle geocoding for you; it simply requires a full address in the final column, in a regularly formatted CSV file. So a full address won't be simply "1600 Pennsylvania Ave," but rather "1600 Pennsylvania Ave. N.W., Washington, D.C." or similar.

It'll geocode an address roughly every two seconds using your Google API key. Remember you need to follow all the Google requirements, including you geocoding for a Google map, and recognizing it'll die after you hit the limit, which may be about 2,500 addresses per day.

If you get an address every 2 seconds, you'll get 30 per minute, 1,800 per hour; you'll hit your limit in about an hour and a half.

Simply run it like this: postgeo.py myfile.csv.

It'll spit back a myfile-geo.csv.


Command-line jittering or clustering
------------------------------------

cellspacer.py is designed to take data that has overlapping points and spread them out in a circular pattern. There's a hard-coded field that can be edited -- "meters=100" -- to adjust for whether you're trying to spread points around houses or neighborhoods or cities or states or zipcodes.

This runs instantaneously on a dataset of 1,000 rows, but it may also be memory intensive. If you have problems on a much larger data set, let us know and we can suggest and possibly test some workarounds.

In general
----------

Pull requests are welcomed, as are suggestions. All credit goes to Palm Beach Newspapers, owner of The Palm Beach Post and Palm Beach Daily News, a Cox Media Group company.
