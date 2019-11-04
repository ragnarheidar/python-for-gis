import arcpy
from datetime import datetime

start_timestamp = datetime.now()

arcpy.env.workspace = r"C:\temp"

RasterList = arcpy.ListRasters("*")

for raster in RasterList:
    xmin = arcpy.GetRasterProperties_management(raster, 'LEFT')
    xmax = arcpy.GetRasterProperties_management(raster, 'RIGHT')
    ymin = arcpy.GetRasterProperties_management(raster, 'BOTTOM')
    ymax = arcpy.GetRasterProperties_management(raster, 'TOP')
    centerX = (float(xmax.getOutput(0)) + float(xmin.getOutput(0))) / 2
    centerY = (float(ymax.getOutput(0)) + float(ymin.getOutput(0))) / 2
    print raster + " center X: " + str(centerX) + " center Y: " + str(centerY)

print "done in: " + str(datetime.now() - start_timestamp)
