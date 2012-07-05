import os
import sys
import fnmatch

files2Process = []
def AddFilesFromDirectory (directoryPath):
	for root, dirnames, filenames in os.walk (directoryPath):
		for filename in fnmatch.filter (filenames, '*.py'):
			
			#
			# Ignore the this script file.
			#
			
			if sys.argv[1] in filename:
				continue
			files2Process.append (os.path.join (root, filename))

#
# Process arguments.
#

for arg in sys.argv[1:]:
	if os.path.isdir (arg):
		AddFilesFromDirectory (directoryPath)
	else:
		files2Process.append (arg)

#
# Add working directory by default if no arguments were given.
#

if (len (files2Process) == 0):
	AddFilesFromDirectory ('.')

#
# Process files.
#

for filePath in files2Process:
	fileContents = open (filePath).read ()
	
def RemoveWhiteSpace (fileContents)
	return 
