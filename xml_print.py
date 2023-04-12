#!/usr/bin/env python

import xml.dom.minidom
from argparse import ArgumentParser
import sys

def do_parse(fd, indent=2):
    try:
        document = xml.dom.minidom.parse(fd)
        print(document.toprettyxml(indent=" "*indent))
    except ValueError as e:
        print(e)
        exit(1)

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

