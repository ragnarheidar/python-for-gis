# -- coding: utf-8 --
import folium
import csv

# Link to Esri World Imagery service plus attribution
IMO_basemap = "https://luk.vedur.is/arcgis/rest/services/grunnkort/grunnkort_cache_wmerc84/MapServer/tile/{z}/{y}/{x}"
IMO_Attribution = "Tiles &copy; Veðurstofa Íslands | Landmælingar Íslands | Map data © OpenStreetMap contributors"
WeatherStationsCSV = "IMO_weatherstations_2017_06_26.csv"

MapObject = folium.Map(location=[64.9865, -18.5867], tiles=IMO_basemap, attr=IMO_Attribution, zoom_start=7)

StationGroup = folium.FeatureGroup(name="Station")

with open(WeatherStationsCSV) as CSVinput:
    reader = csv.reader(CSVinput, delimiter=";")
    next(reader)
    for row in reader:
        lat = float(row[3])
        lon = float(row[4])
        name = str(row[1])
        original_z = row[5]
        EU_dem_z = row[10]
        LMI_dem_z = row[11]
        ArcticDEM_z = row[12]
        Tooltip = name
        StationGroup.add_child(folium.Marker(location=[lat, lon], popup="Name"))

MapObject.add_child(StationGroup)
MapObject.add_child(folium.LayerControl())
MapObject.save(outfile="WeatherStations.html")
