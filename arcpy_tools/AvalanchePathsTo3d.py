# -*- coding: utf-8 -*-
""""
Tool Name: Avalanche paths to 3D
Source Name: AvalanchePathsTo3d.py
Version: ArcGIS 10.3.1
Author: Icelandic Meteorology Office/Ragnar H. Thrastarson
Created: 2016-10-28
Description: A python script tool that takes pre-defined avalanche
paths with pre-defined fields and converts them to 3D and adds M
coordinates by using a surface of some sort (TIN or raster). The
tool also exports both an attribute table and a coordinate table
for the output features.
"""

import arcpy

InputFileGeodatabase = arcpy.GetParameterAsText(0)  # File Geodatabase usually named verk.gdb
InputFeatureClass = arcpy.GetParameterAsText(1)  # Must be line feature class usually named braut2d
InputDEM = arcpy.GetParameterAsText(2)  # Surface that must overlap input feature class
OutputTableLocation = arcpy.GetParameterAsText(3)  # Location for braut3did table id_nafn table created by the tool

# Paths and filenames for outputs
OutputBraut3d = InputFileGeodatabase + "\\brautir\\braut3d"
OutputBraut3did = InputFileGeodatabase + "\\brautir\\braut3did"
OutputBraut3didTable = OutputTableLocation + "\\braut3did.txt"
OutputBraut3dTable = OutputTableLocation + "\\id_nafn.txt"


def generate_3d_features():
    number_of_features = str(arcpy.GetCount_management(InputFeatureClass))
    arcpy.AddMessage(number_of_features + " segments found")
    arcpy.InterpolateShape_3d(InputDEM, InputFeatureClass, OutputBraut3d)  # convert 2D to 3D
    arcpy.AddMessage("Feature class braut3d created")
    arcpy.CalculateField_management(OutputBraut3d, "ID", "!OBJECTID!", "PYTHON_9.3")  # populate fields
    arcpy.CalculateField_management(OutputBraut3d, "start", "0", "PYTHON_9.3")
    arcpy.CalculateField_management(OutputBraut3d, "end", "!shape.length@meters!", "PYTHON_9.3")
    arcpy.AddMessage("Fields ID, START and END populated")
    arcpy.env.MTolerance = "0.001"  # set tolerance for M coordinate
    arcpy.CreateRoutes_lr(OutputBraut3d, "ID", OutputBraut3did,
                          "TWO_FIELDS", "start", "end", "UPPER_LEFT",
                          "1", "0", "IGNORE", "INDEX")
    arcpy.AddMessage("Feature class braut3did created")


def export_braut3did_to_text():
    feature_counter = 1
    with open(OutputBraut3didTable, 'w') as f:
        for row in arcpy.da.SearchCursor(OutputBraut3did, ["SHAPE@"]):
            f.write(str(feature_counter) + " 0" + "\n")
            feature_counter += 1
            for part in row[0]:
                node_counter = 1
                for pnt in part:
                    f.write(str(node_counter) + " {0} {1} {2} {3}".format(pnt.X, pnt.Y, pnt.Z, pnt.M) + "\n")
                    node_counter += 1
    f.close()


def export_braut3d_attributes_to_text():
    with open(OutputBraut3dTable, 'w') as i:
        fields = ["ID", "SEG", "NAFN"]
        i.write(fields[0] + " " + fields[1] + " " + fields[2] + "\n")
        for row in arcpy.da.SearchCursor(InputFeatureClass, fields):
            i.write("{0} {1} {2}".format(row[0], row[1], row[2]) + "\n")
    i.close()

# Call function to turn 2D features to 3D, populate fields and add M coordinates
generate_3d_features()
arcpy.AddMessage("Exporting tables...")
# Call function to export coordinate table
export_braut3did_to_text()
arcpy.AddMessage("Coordinate table exported: braut3did.txt")
# Call function to export attribute table
export_braut3d_attributes_to_text()
arcpy.AddMessage("Attribute table exported: id_nafn.txt")
