#!/usr/bin/env python

import xml.dom.minidom
from xml.parsers.expat import ExpatError
from argparse import ArgumentParser
import sys
import re

def do_parse(fd, indent=2):
    """
    getting the line when an error happens,
    reading lines from the fd instead directly parsing fd.
    """
    lines = fd.readlines()
    try:
        doc = xml.dom.minidom.parseString("".join(lines))
    except ValueError as e:
        print(f"ERROR: {e}")
        exit(1)
    except xml.parsers.expat.ExpatError as e:
        print(f"ERROR: {e}")
        if r := re.match("[^:]+: line (\d+)", str(e)):
            print(lines[int(r.group(1))], end="")
        exit(1)
    #
    lines = []
    for line in doc.toprettyxml(indent=" "*indent).split("\n"):
        if len(line.strip()):
            lines.append(line)
    print("\n".join(lines))

ap = ArgumentParser()
ap.add_argument("file", nargs="*")
ap.add_argument("-i", action="store", dest="indent",
                type=int, default=2,
                help="specify the size of the indent.")
opt = ap.parse_args()

if len(opt.file) == 0:
    do_parse(sys.stdin, opt.indent)
else:
    for f in opt.file:
        do_parse(open(f), opt.indent)

