#!/usr/bin/env python

import sys
import quopri
from argparse import ArgumentParser

ap = ArgumentParser(description="quoted-printable encoder.")
ap.add_argument("string", nargs="?",
                help="specify string. If not specified, taken from stdin.")
ap.add_argument("-n", action="store_true", dest="no_newline",
                help="specify not to print the trailing newline character.")
opt = ap.parse_args()

if opt.string is None:
    opt.string = sys.stdin.read()

print(quopri.encodestring(opt.string.encode()).decode(),
      end="" if opt.no_newline else "\n")

