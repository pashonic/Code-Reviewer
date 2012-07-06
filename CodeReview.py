import os
import sys
import fnmatch
import inspect
import re

files2Process = []
def AddFilesFromDirectory (directoryPath):
	for root, dirnames, filenames in os.walk (directoryPath):
		for filename in fnmatch.filter (filenames, '*.py'):

			#
			# Ignore this script file.
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
# Defined actions.
#

class Actions:
	def RemoveWhiteSpace (self, fileContents):
		return re.sub ('[ \t]+(?=((\r)|(\n)|(\r\n)|(\Z)))', '', fileContents)

#
# Process files.
#

actions = Actions ()
for filePath in files2Process:

	#
	# Open file and dump contents to memory.
	#
	
	print 'Processing File: ' + filePath
	fileContents = open (filePath).read ()
	
	#
	# Execute actions against file contents.
	#
	
	for name, method in inspect.getmembers (actions, callable):
		print 'Running Action: ' + name
		fileContents = method (fileContents)
		
	#
	# Write new file contents back to file.
	#	
		
	fileHandle = open (filePath, 'w')
	fileHandle.write (fileContents)
	fileHandle.close ()
