# -*- coding: utf-8 -*-
""""
Tool Name: Avalanche paths to map
Source Name: AvalanchePathsToMap.py
Version: ArcGIS 10.3.1
Author: Icelandic Meteorology Office/Ragnar H. Thrastarson
Created: 2017-01-24
Description: A python tool script that reads text files from
an avalanche modeling process and creates multiple feature
classes for cartographic purposes. Feature classes created are
named braut_temp, braut2dnanf, rstx and merki.
"""
import arcpy
from arcpy import env

# Tool inputs
env.workspace = arcpy.GetParameterAsText(0)  # File Geodatabase usually named verk.gdb
InputFileTXY = arcpy.GetParameterAsText(1)  # Text file usually ending with -txy
InputFileTID = arcpy.GetParameterAsText(2)  # Text file usually ending with -tid
InputFileTRS = arcpy.GetParameterAsText(3)  # Text file usually ending with -trs
InputFileTPK = arcpy.GetParameterAsText(4)  # Text file usually ending with -tpk

# Outputs and path variables
OutputFeatureDataset = env.workspace + "\\brautir\\"
OutputFeatureclassBrautTemp = "braut_temp"
OutputBrautTemp = OutputFeatureDataset + OutputFeatureclassBrautTemp
OutputBraut2dnafn = OutputFeatureDataset + "braut2dnafn"
OutputRSTX = OutputFeatureDataset + "rstx"
OutputMerki = OutputFeatureDataset + "merki"

# symbology imports
rstx_symbols = "//nas/ofanflod/gogn/gistools/lyr/brautir/rst.lyr"
merki_symbols = "//nas/ofanflod/gogn/gistools/lyr/brautir/merki.lyr"
brautir_symbols = "//nas/ofanflod/gogn/gistools/lyr/brautir/brautir.lyr"

# arcpy.env.overwriteOutput = True

# Get spatial reference from a fixed location
spatial_reference = "//nas/luk/gogn/snidmat/hnitakerfi/ISN 1993 Lambert 1993.prj"


def create_braut_temp():
    arcpy.CreateFeatureclass_management(OutputFeatureDataset, OutputFeatureclassBrautTemp, "POLYLINE", "",
                                        "DISABLED", "DISABLED", spatial_reference)
    # read text file and creat a nested list with ID, X and Y
    nested_coordlist = []
    item_list = []
    with open(InputFileTXY, "r") as f:
        for line in f:
            item = line.split()
            item_list.append(item)
        item_list.pop(0)  # remove first line from text file
        item_list.pop(-1)  # remove last line from text file

    for item in item_list:
        if len(item) == 2:
            listnumber = item[0]
        elif len(item) == 3:
            item[0] = listnumber
            nested_coordlist.append(item)

    arcpy.AddMessage("List for insert cursor created")
    # Use nested list to create a polylines in feature class
    cur = None  # make sure cursor is clean

    cur = arcpy.da.InsertCursor(OutputBrautTemp, ["SHAPE@"])
    array = arcpy.Array()
    id_value = -1
    for coords in nested_coordlist:
        if id_value == -1:
            id_value = coords[0]
        if id_value != coords[0]:
            cur.insertRow([arcpy.Polyline(array)])
            array.removeAll()
        array.add(arcpy.Point(float(coords[1]), float(coords[2]), ID=int(coords[0])))
        id_value = coords[0]

    cur.insertRow([arcpy.Polyline(array)])
    # clean out cursor
    if cur:
        del cur 


def create_braut_field():
    # Create a temporary table in FGDB
    arcpy.TableToTable_conversion(InputFileTID, env.workspace, "temp_id_table")
    temp_table = env.workspace + "/temp_id_table"  # needed because of tool bug
    # add BRAUT field with a join
    arcpy.JoinField_management(OutputBrautTemp, "OBJECTID", temp_table, "File_ID", ["BRAUT"])
    arcpy.Delete_management(temp_table)  # Delete temporary table


def create_linear_reference():
    arcpy.AddField_management(OutputBrautTemp, "start", "FLOAT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.AddField_management(OutputBrautTemp, "end", "FLOAT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management(OutputBrautTemp, "start", "0", "PYTHON_9.3")
    arcpy.AddMessage("Done adding and populating fields START and END to braut_temp feature class")
    arcpy.CalculateField_management(OutputBrautTemp, "end", "!shape.length@meters!", "PYTHON_9.3")
    arcpy.env.MTolerance = "0.001"  # set tolerance for M coordinate
    arcpy.CreateRoutes_lr(OutputBrautTemp, "BRAUT", OutputBraut2dnafn,
                          "TWO_FIELDS", "start", "end", "UPPER_LEFT",
                          "1", "0", "IGNORE", "INDEX")


def create_rstx():
    arcpy.MakeRouteEventLayer_lr(OutputBraut2dnafn, "BRAUT", InputFileTRS, "NAFN POINT lengd", "rstx_events", "",
                                 "NO_ERROR_FIELD", "ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
    arcpy.CopyFeatures_management("rstx_events", OutputRSTX)
    arcpy.Delete_management("rstx_events")


def create_merki():
    arcpy.MakeRouteEventLayer_lr(OutputBraut2dnafn, "BRAUT", InputFileTPK, "NAFN POINT lengd", "merki_events", "",
                                 "NO_ERROR_FIELD", "ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
    arcpy.CopyFeatures_management("merki_events", OutputMerki)
    arcpy.Delete_management("merki_events")


create_braut_temp()
arcpy.AddMessage("Done writing features to braut_temp feature class")

create_braut_field()
arcpy.AddMessage("Added field BRAUT to braut_temp feature class")

create_linear_reference()
arcpy.AddMessage("Created braut2dnafn feature class with linear referencing")

create_rstx()
arcpy.AddMessage("Created rstx feature class")

create_merki()
arcpy.AddMessage("Created merki feature class")

# Add outputs to map
Mxd = arcpy.mapping.MapDocument("CURRENT")
DataFrame = arcpy.mapping.ListDataFrames(Mxd)[0]
AddBraut = arcpy.mapping.Layer(OutputBraut2dnafn)
AddRstx = arcpy.mapping.Layer(OutputRSTX)
AddMerki = arcpy.mapping.Layer(OutputMerki)
arcpy.mapping.AddLayer(DataFrame, AddBraut, "TOP")
arcpy.mapping.AddLayer(DataFrame, AddRstx, "TOP")
arcpy.mapping.AddLayer(DataFrame, AddMerki, "TOP")
del Mxd, AddBraut, AddRstx, AddMerki

# Add symbology to outputs
arcpy.ApplySymbologyFromLayer_management ("Braut2dnafn", brautir_symbols)
arcpy.ApplySymbologyFromLayer_management ("rstx", rstx_symbols)
arcpy.ApplySymbologyFromLayer_management ("merki", merki_symbols)
