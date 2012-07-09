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

def GetFileLines (fileContents):
	return re.split ('\r\n|\r|\n', fileContents)

#
# Defined actions.
#

class Actions:

	def RemoveWhiteSpace (self, fileContents):
		return re.sub ('[ \t]+(?=\r|\n|(\r\n)|\Z)', '', fileContents)

	def ParenthesisCheck (self, fileContents):
		fileContentsCopy = str (fileContents)

		#
		# Remove quoted text.
		#

		fileContentsCopy = re.sub ('\\\\[\'\"]', '', fileContents)
		fileContentsCopy = re.sub ('[\"\'].*?[\"\']', '', fileContents)

		#
		# Find parenthesis issues.
		#

		for lineNumber, lineString in enumerate (GetFileLines (fileContentsCopy)):
			match = re.search ('[^\s\(]\(', lineString)
			if match:
				print 'Warning [{0}, {1}]: ParenthesisCheck: {2}'.format (lineNumber + 1, lineString.find (match.group (0)) + 1, match.group (0))
		return fileContents

#
# Process files.
#

actions = Actions ()
for filePath in files2Process:

	#
	# Open file and dump contents into memory.
	#

	print 'Processing File: ' + filePath
	fileContents = open (filePath, 'rb').read ()

	#
	# Execute actions against file contents.
	#

	for name, method in inspect.getmembers (actions, callable):
		print 'Running Action: ' + name
		fileContents = method (fileContents)

	#
	# Write new file contents back to file.
	#

	fileHandle = open (filePath, 'wb')
	fileHandle.write (fileContents)
	fileHandle.close ()
