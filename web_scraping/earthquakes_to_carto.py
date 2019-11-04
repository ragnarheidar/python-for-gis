"""
Icelandic earthquakes in Iceland for the past 48 hours into CartoDB.
This script will:
1. Scrape earthquakes from the Iceland Met Office (past 48 hrs.)
2. Parse the resaults into a csv table and save it
3. Create a Python list from csv file
4. Use CartoDB SQL API to:
  a) Truncate a table in CartoDB
  b) Insert new records into the same table by wrapping Python list into SQL query

Author: Ragnar Heidar Thrastarson, 2014.
Credits: Thanks to Richard and Maptime NYC.

To run every hour in crontab use:
0 * * * * python /home/pi/ECartoDB.py
"""

import urllib2
import urllib
from bs4 import BeautifulSoup
import datetime
import csv

# Variables defined and open/create csv file
vi_url = "http://www.vedur.is/skjalftar-og-eldgos/jardskjalftar#view=table"
page = urllib2.urlopen(vi_url)
soup = BeautifulSoup(page.read(), "html.parser")
# timestamp = datetime.datetime.now().strftime("%Y_%m_%dT%H%M%S")
outfilename = "iceland_quake.csv"
f = open(outfilename, "w")
f.write("quake_datetime, lat, lon, depth, size, quality, catagory\n")

# Get soup from JS variable
package = soup("script")[5]
package = package.encode("utf-8")
start_location = package.find("quakeInfo")
end_location = start_location + 9
quake_string_start_location = end_location + 5
js_var_tag = package[start_location:end_location]
print "Tag found at " + str(start_location) + ":" + str(end_location)

if js_var_tag == "quakeInfo": # check if position in soup is correct
    package = package[quake_string_start_location:]
    package = package.rstrip("</script>")
    package = package.rstrip("\n")
    package = package.rstrip("}];")
    package_list = package.split("},{")
    print str(len(package_list)) + " earthquakes found"
    for i in package_list:
        year = i.split(",")[0]
        year = year.lstrip("'t':new Date(")
        month = i.split(",")[1]
        month = str(month)
        month = month.split("-")[0]
        day = i.split(",")[2]
        hour = i.split(",")[3]
        minu = i.split(",")[4]
        sec = i.split(",")[5]
        sec = sec.rstrip(")")
        lat = i.split("'")[9]
        lat = lat.replace(",", ".")
        lon = i.split("'")[13]
        lon = lon.replace(",", ".")
        depth = i.split("'")[17]
        depth = depth.replace(",", ".")
        size = i.split("'")[21]
        size = size.replace(",", ".")
        quality = i.split("'")[25]
        quality = quality.replace(",", ".")
        catag = float(size)
        catag = int(catag)
        quakeline = year + "-" + month + "-" + day + "T" + hour + ":" + minu + ":" + sec + "Z," + lat + "," + lon + "," + depth + "," + size + "," + quality + "," + str(catag)
        f.write(quakeline + "\n")
    f.close()
    
else:
    print "Earthauakes NOT found!" # if position not correct, quit script
    quit()
       
# Convert CSV file to Python list formatted for the CartoDB SQL API
quakelist = []
with open(outfilename, 'rb') as csvfile:
    quakereader = csv.reader(csvfile, delimiter = ',')
    next(quakereader)
    for row in quakereader:
        qtime = row[0:1]
        qlat = [float(c) for c in row[1:2]]
        qlon = [float(c) for c in row[2:3]]
        qdepth = [float(c) for c in row[3:4]]
        qsize = [float(c) for c in row[4:5]]
        qqual = [float(c) for c in row[5:6]]
        qcat = [int(c) for c in row [6:7]]
        qline = str(qtime + qlat + qlon + qdepth + qsize + qqual + qcat).strip('[]')
        geoqline = str(qlat + qlon).strip('[]') + "),"
        qqline = "(CDB_LatLng(" + geoqline + qline + ")"
        quakelist.append(qqline)

csvfile.close()

# Delete and insert rows with CartoDB SQL API
username = "ragnarheidar"
apikey = 'cda5e618022b44269b2e0a87f2876402c4ba7d26'
truncate = "DELETE FROM iceland_quake48"
insert = "INSERT INTO iceland_quake48 (the_geom, quake_datetime, lat, lon, depth, size, quality, catagory) (VALUES %s)" % ','.join(quakelist)
url = "https://%s.cartodb.com/api/v1/sql" % username

params_del = {
    'api_key' : apikey,
    'q'       : truncate
}

params_ins = {
    'api_key' : apikey,
    'q'       : insert
}

req_del = urllib2.Request(url, urllib.urlencode(params_del))
response = urllib2.urlopen(req_del)
print "Old rows deleted"
req_ins = urllib2.Request(url, urllib.urlencode(params_ins))
response = urllib2.urlopen(req_ins)
print "New rows inserted"
