import os
import arcpy
from datetime import datetime

start_timestamp = datetime.now()
arcpy.env.compression = "LZ77"
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3057)
# path to folder that includes .SAFE folders
workspace = r"C:\Users"

RasterList = []

# look for folders and image bands and append to list of aquisitions
for dirpath, dirnames, filenames in arcpy.da.Walk(workspace, datatype="RasterDataset"):
    for filename in filenames:
        if filename[-7:] == "B08.jp2":
            item = os.path.join(dirpath, filename)
            RasterList.append(item)

# for each item in the list
for raster in RasterList:
    band8 = raster
    band4 = raster[:-7] + "B04.jp2"
    band3 = raster[:-7] + "B03.jp2"
    BandCombination = band8 + ";" + band4 + ";" + band3
    OutputRasterName = raster[:-7] + "NIR_B843.tif"
    arcpy.CompositeBands_management(BandCombination, OutputRasterName)
    print "Done with " + OutputRasterName

print "done in: " + str(datetime.now() - start_timestamp)
