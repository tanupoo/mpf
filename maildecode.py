#!/usr/bin/env python

from decode_mime import decode_mime_file

from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter
ap = ArgumentParser(description="mail decoder.")
ap.add_argument("mail_file", nargs="?", help="specify a filename.")
ap.add_argument("-x", action="store", dest="decode", type=int,
                help="specify the number of the content to be decoded."
                    " if 0, it shows the header.")
ap.add_argument("-o", action="store", dest="out_file",
                help="specify the name to save data in case "
                    "when the content type is image.")
ap.add_argument("-v", action="store_true", dest="verbose",
                help="enable verbose mode.")
opt = ap.parse_args()

decode_mime_file(opt.mime_file, opt.decode, opt.out_file, opt.verbose)
