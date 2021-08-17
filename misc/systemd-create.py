#!/usr/bin/env python3

"""Convert prototype systemd files (and the files they execute)
to actual systemd specific files with usernames and paths to use..
"""

import sys, os, stat, json, time, argparse, traceback, glob
import textwrap, pprint
from pathlib import Path

# Each entry contains two items. The first is the location of the prototype
# file, and the second is the name and location of the transformed file.
FILE_LOCATIONS = [ \
    ['misc/fisb-rest.service.prototype', 'misc/fisb-rest.service'], \
    ['misc/fisb-rest_service.prototype', 'fisb-rest_service'], \
    ]

def checkFileExistence(fisbpath):
    """Check that all the files in FILE_LOCATIONS exist in the correct places.

    If the files all exist, nothing is printed. If a file does not exist,
    it is printed and the function will return False.
    
    Args:
        fisbpath (str): Path to base fisb (fisb-decode or fisb-rest)

    Returns:
        bool: True if all the files exist. Else False.
    """
    noErrors = True

    for x in FILE_LOCATIONS:
        fullpath = os.path.join(fisbpath, x[0])
        if not Path(fullpath).is_file():
            print('{} cannot be found.'.format(fullpath))
            noErrors = False

    return noErrors

def makeSubstitutions(username, fisbpath):
    """Make substitions in the files to change to reflect the username and path.

    The files are read, the substitions made, and the files are written to the
    correct output file.

    Args:
        username (str):
        fisbpath (str): Path to base fisb (fisb-decode or fisb-rest)
    """
    for x in FILE_LOCATIONS:
        readpath = os.path.join(fisbpath, x[0])
        writepath = os.path.join(fisbpath, x[1])

        contents = Path(readpath).read_text()
        contents = contents.replace('<username>', username)
        contents = contents.replace('<path>', fisbpath)

        Path(writepath).write_text(contents)

        if '_service' in writepath:
            os.chmod(writepath, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)

def main(username, fisbpath):
    """Substitute arguments of username and path into files for systemd.
    
    Args:
        username (str):
        fisbpath (str): Path to base fisb (fisb-decode or fisb-rest)
    """
    # Remove any trailing '\' from pathname
    if (fisbpath[-1] == '/') or (fisbpath[-1] == '\\'):
        fisbpath = fisbpath[:-1]
    
    if checkFileExistence(fisbpath):
        makeSubstitutions(username, fisbpath)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument('username', help='User to run systemd script under')
    parser.add_argument('fisbpath', help="Path to fisb-rest (i.e. '/home/username/fisb-rest'). Do not include trailing slash.")

    args = parser.parse_args()
        
    # Call main routine
    main(args.username, args.fisbpath)
