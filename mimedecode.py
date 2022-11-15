#!/usr/bin/env python

import sys
import email

def main(opt):
    if opt.mime_file is None:
        msg = email.message_from_file(sys.stdin)
    else:
        with open(opt.mime_file, "r") as fd:
            msg = email.message_from_file(fd)
    #
    cid=-1
    for p in msg.walk():
        cid += 1
        # if cid == 0, show header and exit.
        if cid == 0:
            if opt.decode == 0:
                for k,v in p.items():
                    print(f"{k}: {v}")
                break
            else:
                print(f"# Date: {p.get('Date')}")
                print(f"From: {p.get('From')}")
                print(f"To: {p.get('To')}")
                print(f"Subject: {p.get('Subject')}")
                continue
        #
        ct = f"{p.get_content_maintype()}/{p.get_content_subtype()}"
        # Content-Disposition: attachment; filename="SIG-SWO-056-16.pdf"
        if opt.decode is None:
            #print("{}# {}".format("\n" if cid != 1 else "", cid))
            print(f"\n# {cid}")
            for k,v in p.items():
                print(f"{k}: {v}")
            #print("content-type", ct)
            #cte = p.get("Content-Transfer-Encoding")
            #if cte is not None:
            #    print("encoding:", cte)
            body = p.get_payload(decode=True)
            if body is not None:
                print("size:", len(body))
            else:
                print("size:", 0)
        elif opt.decode == cid:
            body = p.get_payload(decode=True)
            if body is not None:
                if opt.out_file:
                    with open(opt.out_file, "wb") as fd:
                        fd.write(body)
                elif ct in [ "text/plain", "text/html" ]:
                    charset = p.get_charsets()[0]
                    print(body.decode(charset))
                else:
                    print(f"ERROR: the option -o is required for {ct}")

from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter
ap = ArgumentParser(description="mime decoder.")
ap.add_argument("mime_file", nargs="?", help="specify a filename.")
ap.add_argument("-x", action="store", dest="decode", type=int,
                help="specify the number of the content to be decoded."
                    " if 0, it shows the header.")
ap.add_argument("-o", action="store", dest="out_file",
                help="specify the name to save data in case "
                    "when the content type is image.")
opt = ap.parse_args()
main(opt)
