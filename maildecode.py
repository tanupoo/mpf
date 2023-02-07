#!/usr/bin/env python

from decode_mime import decode_mime_file
from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter
from dateutil.tz import tz

tz_str = "Asia/Tokyo"

ap = ArgumentParser(description="mail decoder.")
ap.add_argument("mail_file", nargs="?", help="specify a filename.")
ap.add_argument("-x", action="store", dest="decode", type=int,
                help="specify the number of the content to be decoded."
                    " if 0, it shows the header.")
ap.add_argument("-o", action="store", dest="out_file",
                help="specify the name to save data in case "
                    "when the content type is image.")
ap.add_argument("--tz", action="store", dest="tz_str",
                help="specify the timezone.")
ap.add_argument("-v", action="store_true", dest="verbose",
                help="enable verbose mode.")
opt = ap.parse_args()

if opt.tz_str:
    tz_str = opt.tz_str
default_tz = tz.gettz(tz_str)
decode_mime_file(opt.mail_file, opt.decode, opt.out_file, default_tz, opt.verbose)
