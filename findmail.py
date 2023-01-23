#!/usr/bin/env python

import os
from stat import S_ISDIR
import time
import argparse
from decode_mime import decode_mime_file, decode_subject
import re
from datetime import datetime, timedelta
from dateutil.parser import parse as dt_parse
from dateutil import tz
from email.parser import Parser as emailParser

def get_info(
        path: str,
        ) -> dict:
    filename, ext = os.path.splitext(path)
    info = {}
    info.update({"Path": path})
    with open(path) as fd:
        items = dict(emailParser().parse(fd))
    info.update({"Date": dt_parse(items.get("Date"))})
    info.update({"Subject": decode_subject(items.get("Subject"))})
    info.update({"From": decode_subject(items.get("From"))})
    return info

def find_mail(path, recursive=False, newer_than=None):
    mails = []  # updated in walk_dir()
    def walk_dir(path, recursive=False, newer_than=None):
        with os.scandir(path) as fd:
            for entry in fd:
                if entry.name.startswith(".."):
                    continue
                elif entry.is_dir():
                    if recursive:
                        walk_dir(entry.path, recursive)
                elif entry.is_symlink():
                    continue
                elif newer_than:
                    if entry.stat().st_mtime >= newer_than:
                        # this is the 1st filter.
                        # The 2nd filter will be done later at get_info().
                        mails.append(entry)
                    else:
                        pass
                else:
                    mails.append(entry)
    #
    try:
        mode = os.stat(path).st_mode
        if not S_ISDIR(mode):
            print(f"ERROR: {path} is not a directory.")
            return
    except Exception as e:
        print(f"ERROR: {path}", e)
        return
    walk_dir(path, recursive, newer_than)
    for e in sorted(mails, key=lambda x: x.stat().st_mtime):
        info = get_info(e.path)
        print("##", info.get("Date"))
        print("  -", info.get("From"))
        print("  -", info.get("Subject"))
        print("  -", info.get("Path"))

# main
ap = argparse.ArgumentParser()
ap.add_argument("mail_dir", help="a directory name")
ap.add_argument("-r", action="store_true", dest="recursively",
                help="enable to find a mail file recursively.")
ap.add_argument("-t", action="store", dest="time_span",
                help="specify the span string to be picked.")
ap.add_argument("--tz", action="store", dest="tz",
                help="specify the timezone.")
ap.add_argument("-d", action="store_true", dest="debug",
                help="enable debug mode.")
opt = ap.parse_args()

# time_span is None: ts -> None
# ts is not None and tz is None: newer_than -> ts
dt = datetime.now()
if opt.tz:
    dt = datetime.now(tz=tz.gettz("Asia/Tokyo"))
    ts_limit = dt.timestamp()
if opt.time_span:
    if r := re.match("(\d+)w", opt.time_span):
        delta = int(r.group(1)) * 7*24*60*60
    elif r := re.match("(\d+)d", opt.time_span):
        delta = int(r.group(1)) * 24*60*60
    elif r := re.match("(\d+)h", opt.time_span):
        delta = int(r.group(1)) * 60*60
    elif r := re.match("(\d+)m", opt.time_span):
        delta = int(r.group(1)) * 60
    else:
        raise ValueError(f"unknown format {opt.time_span}")
else:
    delta = 60*60 # 1 hour
ts_limit = (dt - timedelta(seconds=delta)).timestamp()

# body
find_mail(opt.mail_dir, recursive=opt.recursively, newer_than=ts_limit)
