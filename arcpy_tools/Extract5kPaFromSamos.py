# -*- coding: utf-8 -*-
"""
Created on Fri Apr  7 09:38:13 2017

@author: siggasif, ragnarheidar


Find all peak pressure output files from a Samos run within a given directory, 
extract 5 kPa isopressure line, create a shapefile and add two columns with 
the runout index and run name. Note, existing shp files for the same run are 
deleted in the process so take care if rerunning.

Arcpy additions by ragnarheidar. This code has been modified from its original
version so it can be run as a python script tool within ArcGIS. In addition to
the steps mentioned above,  a spatial reference is added to each shapefile and
all shapefiles are added to an existing file geodatabase. If user runs code/tool
in ArcMap, a standard symbol is applied and the output is added to the map.
"""


import shapefile
import os
import glob
import subprocess
import arcpy
from arcpy import env

# user inputs for arcpy tool
path = arcpy.GetParameterAsText(0)  # input folder with samos runs
pathshp = arcpy.GetParameterAsText(1)  # output folder for shapefiles
filegdbpath = arcpy.GetParameterAsText(2)  # path to verk.gdb file geodatabase

# path to ArcMap symbology
samos_symbols = "//nas/ofanflod/gogn/gistools/lyr/samos/samos_l.lyr"

# Spatial reference for EGSP:3057 (Lambert/ISN93)
spatial_reference = "//nas/luk/gogn/snidmat/hnitakerfi/ISN 1993 Lambert 1993.prj"

# find all files containing peak pressure fields. NOTE: this is for the structure created during batch runs
files = glob.glob(path+'\\**\\pressure\\*.txt')

# NOTE: for structure during runs made through the user interface with data exported through the report generator:
# files = glob.glob(path+'/**/raster/*_ppr*')

# path to folder where shapefiles should be stored
pathshp = path + "\\shp"
# create shp directory if it doesn't exist
if os.path.exists(pathshp)==False:
    os.system("mkdir "+pathshp)

for f in files:
    arcpy.AddMessage("Extracting 5kPa isoline for " + f)
    # print "Extracting 5kPa isoline for " + f
    # runout index
    rst = f[-6:-4]  # runout index
    # run name - note, this assumes the files are stored under folder ..../run_name/pressure/*.txt
    rname = f.split('\\')[-3]
    # name of pressure file with ending removed
    fname = f.split('\\')[-1][:-4]
    # name of output file is run name +"_" +  name of pressure field output file.
    ofile = pathshp + "\\" + rname + "_" + fname
    # remove shp, shx and dbf files (need to check first if exist!!!)
    if os.path.exists(ofile + ".shp"):
        os.system("rm " + ofile + ".shp")
    if os.path.exists(ofile + ".shx"):
        os.system("rm " + ofile + ".shx")
    if os.path.exists(ofile + ".dbf"):
        os.system("rm " + ofile + ".dbf")

    # create shapefile of 5 kPa isopressure
    subprocess.call("gdal_contour -fl 5 " + f + " " + ofile + ".shp", shell=True)
    # os.system("gdal_contour -fl 5 " + f + " " + ofile + ".shp")

    # -------Add fields to describe runout index and run name--------

    # Read in our existing shapefile
    r = shapefile.Reader(ofile + ".shp")

    # Create a new shapefile in memory
    w = shapefile.Writer()
    
    # Copy over the existing fields
    w.fields = list(r.fields)
    
    # Add our new field using the pyshp API
    # w.field("rstl", "N", "8")
    w.field("rstl", "N", "3") # ragnarheidar changed type from C to N
    w.field("upptakasv", "C", "30")
    
    # Loop through each record, add a column and insert 
    # runout index. 
    for rec in r.records():
        rec.append(rst)
        rec.append(rname)
        # Add the modified record to the new shapefile 
        w.records.append(rec)
    # Copy over the geometry without any changes
    w._shapes.extend(r.shapes())
    
    # Save as a new shapefile (or write over the old one)
    # we overwrite
    w.save(ofile + ".shp")

 # set workspace for shapefiles and file geodatabase imports
env.workspace = pathshp
# list all shapefiles and add them to a list
shapfile_list = arcpy.ListFeatureClasses()
for shape in shapfile_list:
    arcpy.AddMessage("Defining spatial reference for " + shape)
    arcpy.DefineProjection_management(shape, spatial_reference)  # add spatial reference to all shapefiles

for feature in shapfile_list:
    arcpy.AddMessage("Appending to " + feature + " to " + filegdbpath)
    # append featers from each shapefile into a file geodatabase
    arcpy.Append_management(feature, filegdbpath + "\\samos\\samos", "NO_TEST", "", "")


# Add outputs to map
Mxd = arcpy.mapping.MapDocument("CURRENT")  # create mxd object
DataFrame = arcpy.mapping.ListDataFrames(Mxd)[0]  # create dataframe object
AddSamos = arcpy.mapping.Layer(filegdbpath + "\\samos\\samos")
arcpy.mapping.AddLayer(DataFrame, AddSamos, "TOP")  # add features to dataframe
del Mxd, AddSamos  # cleanup

# Add symbology to outputs
arcpy.ApplySymbologyFromLayer_management("samos", samos_symbols)

# for fixing and for non batch runs with samos
# for rec in r.records():
#    rec.append(str(rec[1]))
#    w.records.append(rec)
