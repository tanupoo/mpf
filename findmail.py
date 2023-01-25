#!/usr/bin/env python

import os
from stat import S_ISDIR
import time
import argparse
from decode_mime import get_mail_info
import re
from datetime import datetime, timedelta
from dateutil import tz

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
                        # The 2nd filter will be done later at get_mail_info().
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
        if opt.debug:
            print("-->", e.path)
        info = get_mail_info(e.path)
        print("##", info.get("Date"))
        print("  -", info.get("From"))
        print("  -", info.get("Subject"))
        print("  -", info.get("Path"))

def datetime_before_month(dt, m):
    delta_y = m // 12
    delta_m = m % 12
    y = dt.year - delta_y
    m = dt.month - delta_m
    if dt.month <= delta_m:
        y -= 1
        m += 12
    try:
        return datetime(y, m, dt.day, dt.hour, dt.minute, dt.second)
    except ValueError as e:
        if "day is out of range for month" in str(e):
            next_month = datetime(y, m, 28) + timedelta(days=4)
            d = (next_month - timedelta(days=next_month.day)).day
            return datetime(y, m, d, dt.hour, dt.minute, dt.second)
        else:
            raise

# main
ap = argparse.ArgumentParser()
ap.add_argument("mail_dir", help="a directory name")
ap.add_argument("-r", action="store_true", dest="recursively",
                help="enable to find a mail file recursively.")
ap.add_argument("-t", action="store", dest="time_span",
                help="specify the span string to be picked. "
                    "The string is either xm, xd, xw, xH, or xM (x is an integer.)"
                )
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
    if r := re.match("(\d+)m", opt.time_span):
        ts_limit = datetime_before_month(dt, int(r.group(1))).timestamp()
    else:
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
        ts_limit = (dt - timedelta(seconds=delta)).timestamp()
else:
    ts_limit = (dt - timedelta(seconds=60*60)).timestamp()

# body
find_mail(opt.mail_dir, recursive=opt.recursively, newer_than=ts_limit)
