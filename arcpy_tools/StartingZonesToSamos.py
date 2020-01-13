# -*- coding: utf-8 -*-
""""
Tool Name: Starting Zones to SAMOS
Source Name: StartingZonesToSamos.py
Version: ArcGIS 10.3.1
Author: Icelandic Meteorology Office/Ragnar H. Thrastarson
Created: 2015-07-20
Lates update: 2018-12-05
Description: A python script tool that uses the ArcPy module
to convert a polygon feature class to a specific text based
output. Output includes parameters, number of vertices in each
feature and X and Y coordinates of each vertex for each feature.
The output is specific for the avalanche simulation software SAMOS.

Parameters
1 Input feature class. Avalanche Starting zone, must be polygon
2 Output feature class. Text based output with REL extension
3 Snow depth in m
4 Snow density in kg/m3
5 Type of starting zone
6 Field used to order starting zones in the output REL file
7 SQL Clause if user only needs a subset of the starting zones

"""
import arcpy

InputFC = arcpy.GetParameterAsText(0) # input feature class, tool parameter needs to be set to polygon only
OutputFile = arcpy.GetParameterAsText(1) # output file is a text file with or without the REL extension
Parameter1 = arcpy.GetParameterAsText(2) # snow depth in m
Parameter2 = arcpy.GetParameterAsText(3) # snow density in kg/m3
Parameter3 = arcpy.GetParameterAsText(4) # type of starting zone
SortField = arcpy.GetParameterAsText(5) # field used to order starting zones in output REL file


TemporaySortField = "sort_tmp"
SortClause = "ORDER BY " + TemporaySortField

# define function
def FeatureToSamos():
    arcpy.arcpy.AddField_management(InputFC, TemporaySortField, "SHORT")
    arcpy.AddMessage("Temporay sort field created")
    arcpy.CalculateField_management(InputFC, TemporaySortField, "!" + SortField + "!", "PYTHON_9.3")
    arcpy.AddMessage("Temporay sort field populated with " + SortField)
    try:
        with open(OutputFile, 'w') as f: # create and open output file in write mode
            for row in arcpy.da.SearchCursor(InputFC, ["SHAPE@", TemporaySortField], sql_clause=(None, SortClause)): # for each feature in feature class
                f.write(str(Parameter1.replace(",", ".")) + " " + str(Parameter2.replace(",", ".")) + " " + str(Parameter3.replace(",", ".")) + "\n") # write parameters in first line and move to next line
                # f.write(str(SortField + " " + "{}".format(row[1])) + "\n") # DEV sort
                for part in row[0]: # for each feature
                    vert_count = len(part) # create a variable with the number of vertices
                    f.write(str(vert_count) + "\n") # write the number of vertices and move to next line
                    for pnt in part: # for each node
                        f.write("{0} {1}".format(pnt.X, pnt.Y) + "\n") # write the coordinates of each node and move to next line
        f.close() # save and close output file
        arcpy.AddMessage("REL file created")

    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages())

    finally:
        arcpy.DeleteField_management(InputFC, [TemporaySortField])
        arcpy.AddMessage("Temporay sort field deleted")


# test if output file has REL extension
if OutputFile.lower()[-4:] == ".rel": # if yes, run function
    FeatureToSamos()
else:
    OutputFile = OutputFile + ".rel" # if no, add the REL extension and run function
    FeatureToSamos()
