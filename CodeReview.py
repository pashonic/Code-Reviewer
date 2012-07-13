import os
import sys
import fnmatch
import inspect
import re
import sys

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

Fix = False
for arg in sys.argv[1:]:
    if re.match ('fix\=(true|1)', arg.lower ()):
        Fix = True
        continue
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
# Helper functions.
#

def GetFileLines (text):
    return re.split ('\r\n|\r|\n', text)

def RemoveQuotes (text):
    quoteList = []
    for count, quote in enumerate (re.finditer ('(?<!\\\\)(?P<quote>[\"\']).*?(?<!\\\\)(?P=quote)', text)):
        capture = quote.group (0)
        replace = re.sub ('.', chr (234), quote.group (0))
        text = text[:quote.start (0)] + replace + text[quote.end (0):]
        quoteList.append (capture)
    return (text, quoteList)

def RestoreQuotes (text, quoteList):
    for quote in quoteList:
        text = re.sub ('{0}+'.format (chr (234)), quote, text, 1)
    return text

#
# Defined actions.
#

class Actions:

    def Tabs (self, text):
        return re.sub ('\t', ' ' * 4, text)

    def WhiteSpace (self, text):
        return re.sub ('[ \t]+(?=\r|\n|(\r\n)|\Z)', '', text)

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

    originalContents = str (fileContents)
    for name, method in inspect.getmembers (actions, callable):
        print 'Checking {0}...'.format (name),
        fileContentsTemp = str (fileContents)
        fileContentsTemp = method (fileContents)

        #
        # No problems were found if contents did not change.
        #

        if not (fileContents == fileContentsTemp):
            foundMsg = 'Found'
            if Fix:
                fileContents = fileContentsTemp
                foundMsg += ' and Fixed'
            print foundMsg
        else:
            print 'Pass'

    #
    # Write new file contents back to file.
    #

    if not (originalContents == fileContents):
        fileHandle = open (filePath, 'wb')
        fileHandle.write (fileContents)
        fileHandle.close ()
