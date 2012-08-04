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
    sys.exit(0)
Fix = False
LineCheck = False
for arg in sys.argv[1:]:
    if re.match('fix\=(true|1|)', arg.lower()):
        Fix = True
        continue
    if re.match('linecheck\=(true|1)', arg.lower()):
        LineCheck = True
        continue
    if os.path.isdir(arg):
        AddFilesFromDirectory(directoryPath)
    else:
        files2Process.append(arg)

#
# Don't fix anything in LineCheck mode.
#

if LineCheck:
    Fix = False

#
# Add working directory by default if no arguments were given.
#

if (len(files2Process) == 0):
    AddFilesFromDirectory('.')

#
# Helper objects.
#

PythonCode = ['[\=\+\-\*/\%\!\<\>\~\^\|\&]{1,2}', 'if', 'else', 'elif', 'return', 'def',
              'print', 'for', 'while', 'not', 'in', 'is', 'is not', 'or', 'class']

def GetFileLines(text):
    return re.split('\r\n|\r|\n', text)

def RemoveComments(text):
    commentList = []
    for count, quote in enumerate(re.finditer('(?<!\\\\)\#[^\r\n]+', text, re.DOTALL)):
        capture = quote.group(0)
        replace = re.sub('.', chr(249), quote.group(0))
        text = text[:quote.start(0)] + replace + text[quote.end(0):]
        commentList.append(capture)
    return (text, commentList)

def RestoreComments(text, commentList):
    for quote in commentList :
        text = re.sub('{0}+'.format(chr(249)), quote.replace('\\', '\\\\'), text, 1)
    return text

def RemoveQuotes(text):
    quoteList = []
    text, commentList = RemoveComments(text)
    for count, quote in enumerate(re.finditer('(?<!\\\\)(?P<quote>[\"\']).*?(?<!\\\\)(?P=quote)', text)):
        capture = quote.group(0)
        replace = re.sub('.', chr(250), quote.group(0))
        text = text[:quote.start(0)] + replace + text[quote.end(0):]
        quoteList.append(capture)
    text = RestoreComments(text, commentList)
    return (text, quoteList)

def RestoreQuotes(text, quoteList):
    for quote in quoteList:
        text = re.sub('{0}+'.format(chr(250)), quote.replace('\\', '\\\\'), text, 1)
    return text

#
# Defined actions.
#

class Actions:

    #
    # Fix code that has more than one space between code items.
    # Example: fileContentsTemp   =    method(fileContents)
    # Should Be: fileContentsTemp = method(fileContents)
    #

    def InnerSpace(self, text):
        text, savedQuotes = RemoveQuotes(text)
        text, savedComments = RemoveComments(text)
        text = re.sub('(?<=\S)[ \t]+(?=\S)', ' ', text)
        text = RestoreComments(text, savedComments)
        return RestoreQuotes(text, savedQuotes)

    #
    # Fix inner parenthesis issues.
    # Example: function(   ok    )
    # Should Be: function(ok)
    #

    def InnerParenthesis(self, text):
        text, savedQuotes = RemoveQuotes(text)
        text, savedComments = RemoveComments(text)
        text = re.sub('(?<=[\(\[\{])[ \t]+', '', text)
        text = re.sub('[ \t]+(?=[\)\]\}])', '', text)
        text = RestoreComments(text, savedComments)
        return RestoreQuotes(text, savedQuotes)

    #
    # Fix outter parenthesis issues.
    # Example: function (ok)
    # Should Be: function(ok)
    #

    def OuterParenthesis(self, text):
        text, savedQuotes = RemoveQuotes(text)
        text, savedComments = RemoveComments(text)
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
        text = RestoreComments(text, savedComments)
        return RestoreQuotes(text, savedQuotes)

    #
    # Replace Tabs with spaces.
    #

    def Tabs(self, text):
        return re.sub('\t', ' ' * 4, text)

    #
    # Remove white space.
    #

    def WhiteSpace(self, text):
        return re.sub('[ \t]+(?=\r|\n|(\r\n)|\Z)', '', text)

#
# Modes.
#

def LineCheckMode(filePath):
    for lineNum, lineText in enumerate(open(filePath, 'rb').readlines()):
        originalLineText = str(lineText)
        for name, method in inspect.getmembers(actions, callable):
            lineText = method(lineText)
            if not (originalLineText == lineText):
                print '{0}:{1}'.format(lineNum + 1, name)
            lineText = str(originalLineText)

def FindFixMode(filePath):
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

#
# Process files.
#

actions = Actions()
for filePath in files2Process:

    #
    # Open file and dump contents into memory.
    #

    print '***Processing File: ' + filePath
    if (LineCheck):
        LineCheckMode(filePath)
    else:
        FindFixMode(filePath)
