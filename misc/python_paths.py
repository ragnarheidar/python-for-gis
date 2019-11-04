import sys
import os

pathlist = sys.path
outfile = os.getcwd()
outfile = outfile + "/MyPythonPaths.txt"

with open(outfile, "w") as f:
	f.write("Current python paths:" + "\n")
	for i in pathlist:
		f.write(i + "\n")
f.close()

print "Total number of python paths: " + str(len(pathlist))
print "saved to " + outfile
