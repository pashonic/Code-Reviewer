Python Code Reviewer
=============

Description
-------
<p>I wrote a review script for python code for my own use but maybe you can use it. It detects issues specific to my own coding standard. It can both find and fix issues.  I use it for work and personal projects.</p>

Restrictions
-------
 *  Python 2.6 to 2.7

Usage
-------
python CodeReview.py help

```
python CodeReview.py [file]* [Directory]* [fix =(1| true |0| false)]?
                         [linecheck =(1| true |0| false)]?

    No Arguments Given = fix =0 and linecheck =0 and script will
                         scan all python files in working directory.

    Argument Details:
    file -      File to scan
                Note: Multiple files can be given.

    directory - Directory to recursively search for files to scan
                Note: Multiple directories can be given

    fix -       Option to fix found issues
                Default = Disabled

    linecheck - Enabled line check mode
                Default = Disabled.
                Note: linecheck =1 will disable fix.

    Example call:
    python CodeReview.py file2fix.py fix =1
```