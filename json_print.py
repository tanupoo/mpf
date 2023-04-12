#!/usr/bin/env python

import sys
from argparse import ArgumentParser
try:
    from pyjson5 import load as jsonload
except ModuleNotFoundError:
    from json import load as jsonload
    print("WARNING: doesn't find pyjson5. may cause an error", file=sys.stderr)
import json

def do_parse(fd):
    try:
        print(json.dumps(jsonload(fd), indent=4, sort_keys=opt.sort,
            ensure_ascii=False))
    except ValueError as e:
        print(e)
        exit(1)

ap = ArgumentParser()
ap.add_argument("file", nargs="*")
ap.add_argument("-s", action="store_true", dest="sort",
                help="enable to sort by keys.")
opt = ap.parse_args()

if len(opt.file) == 0:
    do_parse(sys.stdin)
else:
    for f in opt.file:
        do_parse(open(f))

