import os
import sys
import fnmatch

files2Process = []

def AddFilesFromDirectory (directoryPath):
	for root, dirnames, filenames in os.walk(directoryPath):
		for filename in fnmatch.filter(filenames, '*.py'):
			files2Process.append (os.path.join(root, filename))

for arg in sys.argv[1:]:
	if os.path.isdir (arg):
		AddFilesFromDirectory (directoryPath)
	else:
		files2Process.append (arg)

if (len (sys.argv) <= 1):
	AddFilesFromDirectory ('.')


for i in files2Process:
	print i
