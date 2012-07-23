import os
import sys
import fnmatch
import inspect
import re
import sys

files2Process = []
def AddFilesFromDirectory(directoryPath):
    for root, dirnames, filenames in os.walk(directoryPath):
        for filename in fnmatch.filter(filenames, '*.py'):

            #
            # Ignore this script file.
            #

            if sys.argv[1] in filename:
                continue
            files2Process.append(os.path.join(root, filename))

#
# Process arguments.
#

if (len(sys.argv) < 2):
    print "No Files Processed"
    sys.exit (0)
Fix = False
for arg in sys.argv[1:]:
    if re.match('fix\=(true|1|false|0)', arg.lower()):
        Fix = bool(re.search('true|1', arg.lower()))
        continue
    if os.path.isdir(arg):
        AddFilesFromDirectory(directoryPath)
    else:
        files2Process.append(arg)

#
# Add working directory by default if no arguments were given.
#

if (len(files2Process) == 0):
    AddFilesFromDirectory('.')

#
# Helper functions.
#

PythonCode = ['[\=\+\-\*/\%\!\<\>\~\^\|\&]{1,2}', 'if', 'else', 'elif', 'return', 'def', 
              'print', 'for', 'while', 'not', 'in', 'is', 'is not', 'or', 'class']

def GetFileLines(text):
    return re.split('\r\n|\r|\n', text)

def RemoveQuotes(text):
    quoteList = []
    for count, quote in enumerate(re.finditer('(?<!\\\\)(?P<quote>[\"\']).*?(?<!\\\\)(?P=quote)', text)):
        capture = quote.group(0)
        replace = re.sub('.', chr(250), quote.group(0))
        text = text[:quote.start(0)] + replace + text[quote.end(0):]
        quoteList.append(capture)
    return (text, quoteList)

def RestoreQuotes(text, quoteList):
    for quote in quoteList:
        text = re.sub('{0}+'.format(chr(250)), quote.replace('\\', '\\\\'), text, 1)
    return text

#
# Defined actions.
#

class Actions:
    def InnerSpace(self, text):
        text, savedQuotes = RemoveQuotes(text)
        text = re.sub('(?<=\S)[ \t]+(?=\S)', ' ', text)
        return RestoreQuotes(text, savedQuotes)

    def Parenthesis(self, text):
        text, savedQuotes = RemoveQuotes(text)
        textCopy = str(text)
        while True:
            badCandidate = re.search('\w+[ \t]+\(', textCopy)
            if not badCandidate:
                break

            #
            # Check if candidate is an exception.
            #

            isExcep = False
            for exception in PythonCode:
                if re.match('\A{0}[ \t]+\('.format(exception), badCandidate.group(0)):
                    textCopy = textCopy[:badCandidate.start(0)] + re.sub('.', chr(250), badCandidate.group(0)) + textCopy[badCandidate.end(0):]
                    isExcep = True
                    break
            if isExcep:
                continue

            #
            # Modify and re-add bad candidate.
            #

            candidateText = re.sub('[ \t]+\(', '(', badCandidate.group(0))
            textCopy = textCopy[:badCandidate.start(0)] + candidateText + textCopy[badCandidate.end(0):]
            text = text[:badCandidate.start(0)] + candidateText + text[badCandidate.end(0):]
        return RestoreQuotes(text, savedQuotes)

    def Tabs(self, text):
        return re.sub('\t', ' ' * 4, text)

    def WhiteSpace(self, text):
        return re.sub('[ \t]+(?=\r|\n|(\r\n)|\Z)', '', text)

#
# Process files.
#

actions = Actions()
for filePath in files2Process:

    #
    # Open file and dump contents into memory.
    #

    print 'Processing File: ' + filePath
    fileContents = open(filePath, 'rb').read()

    #
    # Execute actions against file contents.
    #

    originalContents = str(fileContents)
    for name, method in inspect.getmembers(actions, callable):
        print 'Checking {0}...'.format(name),
        fileContentsTemp = str(fileContents)
        fileContentsTemp = method(fileContents)

        #
        # No problems were found if contents did not change.
        #

        if not(fileContents == fileContentsTemp):
            foundMsg = 'Found'
            print 'Found{0}'.format(' and Fixed' if Fix else '')
            fileContents = fileContentsTemp
        else:
            print 'Pass'

    #
    # Write new file contents back to file.
    #

    if Fix:
        fileHandle = open(filePath, 'wb')
        fileHandle.write(fileContents)
        fileHandle.close()
