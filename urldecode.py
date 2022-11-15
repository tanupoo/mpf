#!/usr/bin/env python

import sys
import urllib.parse
from argparse import ArgumentParser

ap = ArgumentParser(description="url decoder.")
ap.add_argument("url", nargs="?",
                help="specify URL. If not specified, taken from stdin.")
opt = ap.parse_args()

if opt.url is None:
    opt.url = sys.stdin.read()

print(urllib.parse.unquote(opt.url))

