# PythonCodeReview  Copyright (C) 2012  Aaron Greene
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

def PrintHelp():
    print '''
    How to use:
    python CodeReview.py [file]* [Directory]* [fix =(1| true |0| false)]?
                         [linecheck =(1| true |0| false)]?

    No Arguments Given = fix =0 and linecheck =0 and script will
                         scan all python files in working directory.

    Argument Details:
    file - File to scan
                Note: Multiple files can be given.

    directory - Directory to recursively search for files to scan
                Note: Multiple directories can be given

    fix - Option to fix found issues
                Default = Disabled

    linecheck - Enabled line check mode
                Default = Disabled.
                Note: linecheck =1 will disable fix.

    Example call:
    python CodeReview.py file2fix.py fix =1'''

import os
import sys
import fnmatch
import inspect
import re
import sys

#
# Helper objects.
#

PythonCodeOperators = '[\=\+\-\*/\%\!\<\>\~\^\|\&]+'
PythonCodeWords = '(if)|(else)|(elif)|(return)|(def)|(print)|(for)|(while)|(not)|(in)|(is)|(is not)|(or)|(class)|(import)'
PythonCodeAll = '(({0})|{1})'.format(PythonCodeOperators, PythonCodeWords)

def AddFilesFromDirectory(directoryPath):
    for root, dirnames, filenames in os.walk(directoryPath):
        for filename in fnmatch.filter(filenames, '*.py'):

            #
            # Ignore this script file.
            #

            if sys.argv[1] in filename:
                continue
            Files2Process.append(os.path.join(root, filename))

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
    text, savedComments = RemoveComments(text)
    for count, quote in enumerate(re.finditer('(?<!\\\\)(?P<quote>[\"\']).*?(?<!\\\\)(?P=quote)', text)):
        capture = quote.group(0)
        replace = re.sub('.', chr(250), quote.group(0))
        text = text[:quote.start(0)] + replace + text[quote.end(0):]
        quoteList.append(capture)
    text = RestoreComments(text, savedComments)
    return (text, quoteList)

def RestoreQuotes(text, quoteList):
    for quote in quoteList:
        text = re.sub('{0}+'.format(chr(250)), quote.replace('\\', '\\\\'), text, 1)
    return text

#
# Defined action class.
#

class Actions:

    #
    # Fix instances where there is no space between operators and letters.
    # Example: fileContentsTemp=method(fileContents)
    # Should Be: fileContentsTemp = method(fileContents)
    # Note: Does not catch object names that end with number.
    #

    def Operator_Space(self, text):
        text, savedQuotes = RemoveQuotes(text)
        text, savedComments = RemoveComments(text)
        while True:
            badCandidate = re.search('([A-Za-z]{0})|({0}[A-Za-z])'.format(PythonCodeOperators), text)
            if not badCandidate:
                break
            fixedCandidateText = badCandidate.group(0)
            if re.search('\A\w', fixedCandidateText):
                fixedCandidateText = fixedCandidateText[0] + ' ' + fixedCandidateText[1:]
            else:
                fixedCandidateText = fixedCandidateText[:-1] + ' ' + fixedCandidateText[-1]
            text = text[:badCandidate.start(0)] + fixedCandidateText + text[badCandidate.end(0):]
        text = RestoreComments(text, savedComments)
        return RestoreQuotes(text, savedQuotes)

    #
    # Fix code that has more than one space between code items.
    # Example: fileContentsTemp   =    method(fileContents)
    # Should Be: fileContentsTemp = method(fileContents)
    #

    def Inner_Space(self, text):
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

    def Inner_Parenthesis_Space(self, text):
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

    def Outer_Parenthesis_Space(self, text):
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

            if re.match('\A{0}[ \t]+\('.format(PythonCodeAll), badCandidate.group(0)):
                textCopy = textCopy[:badCandidate.start(0)] + re.sub('.', chr(250), badCandidate.group(0)) + textCopy[badCandidate.end(0):]
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

    def White_Space(self, text):
        return re.sub('[ \t]+(?=\r|\n|(\r\n)|\Z)', '', text)

#
# Script execution modes.
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
# Process arguments.
#

Files2Process = []
if (len(sys.argv) < 2):
    print "No Files Processed"
    sys.exit(0)
Fix = False
LineCheck = False
for arg in sys.argv[1:]:
    if re.match('help', arg.lower()):
        PrintHelp()
        sys.exit(0)
    if re.match('fix\=(true|1|)', arg.lower()):
        Fix = True
        continue
    if re.match('linecheck\=(true|1)', arg.lower()):
        LineCheck = True
        continue
    if os.path.isdir(arg):
        AddFilesFromDirectory(directoryPath)
    else:
        Files2Process.append(arg)

#
# Don't fix anything in LineCheck mode.
#

if LineCheck:
    Fix = False

#
# Add working directory by default if no arguments were given.
#

if (len(Files2Process) == 0):
    AddFilesFromDirectory('.')
#
# Process files.
#

actions = Actions()
for filePath in Files2Process:
    print '>>>Processing File: ' + filePath
    if (LineCheck):
        LineCheckMode(filePath)
    else:
        FindFixMode(filePath)
