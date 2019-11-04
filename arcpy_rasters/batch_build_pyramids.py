import arcpy
from arcpy import env
from datetime import datetime
import logging

start_timestamp = datetime.now()

# path to folder with rasters
env.workspace = r"C:\temp"
# create logging file
logging.basicConfig(filename="BuildStatisticsScriptLog.txt", level=logging.DEBUG)
RasterList = arcpy.ListRasters("*")  # list rasters
TotalRasterCount = len(RasterList)

Counter = 0  # set counter for print messages

for raster in RasterList:
    Counter += 1
    arcpy.BuildPyramids_management(raster, "-1", "NONE", "NEAREST", "DEFAULT", "75", "SKIP_EXISTING")
    print "Done with " + raster + " (" + str(Counter) + " out of " + str(TotalRasterCount) + ")"
    logging.info("done with " + raster + " (" + str(Counter) + " out of " + str(TotalRasterCount) + ")")

print "done in: " + str(datetime.now() - start_timestamp)
logging.info("done at " + str(datetime.now()))
