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

def RemoveQuotes (string):
	string = re.sub ('\\\\[\'\"]', '', string)
	string = re.sub ('[\"\'].*?[\"\']', '', string)
	return string

#
# Defined actions.
#

class Actions:
	
	def ReplaceTabsWithSpaces (self, fileContents):
		return re.sub ('\t', ' ' * 4, fileContents)

	def RemoveWhiteSpace (self, fileContents):
		return re.sub ('[ \t]+(?=\r|\n|(\r\n)|\Z)', '', fileContents)

	def LineCheck (self, fileContents):
		
		#
		# Declare line issues.
		#
		
		issues = [('No Parenthesis Space', '[^\s\(]\(', [RemoveQuotes]),
		          ('Double Quote',         '[^\\\\]?\".*?[^\\\\]?\"', [])]
		
		#
		# Find line issues.
		#
		
		for lineNumber, lineString in enumerate (GetFileLines (fileContents)):
			for name, reg, extraWorks in issues:
				lineStringTemp = str (lineString)
				for extraWork in extraWorks:
					lineStringTemp = extraWork (lineStringTemp)
				match = re.search (reg, lineStringTemp)
				if match:
					print 'Warning [{0}, {1}]: {2}: {3}'.format (lineNumber + 1,
															     lineStringTemp.find (match.group (0)) + 1,
															     name,
															     match.group (0))
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
