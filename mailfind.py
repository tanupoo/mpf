#!/usr/bin/env python

import os
from stat import S_ISDIR
import time
import argparse
from decode_mime import get_mail_info
import re
from datetime import datetime, timedelta
from dateutil import tz

tz_str = "Asia/Tokyo"

def find_mail_quick(
        path: str,
        recursive: bool,
        dt_begin: datetime,
        dt_end: datetime
        ):
    target_mails = []  # updated in walk_dir()
    ts_begin = dt_begin.timestamp()
    ts_end = dt_end.timestamp()
    def walk_dir(path):
        with os.scandir(path) as fd:
            for entry in fd:
                if entry.name.startswith(".."):
                    continue
                elif entry.is_dir():
                    if recursive:
                        walk_dir(entry.path, recursive)
                elif entry.is_symlink():
                    continue
                else:
                    if ts_begin <= entry.stat().st_mtime <= ts_end:
                        target_mails.append(entry)
                    else:
                        # just ignore if span doesn't exist.
                        pass
    #
    try:
        mode = os.stat(path).st_mode
        if not S_ISDIR(mode):
            print(f"ERROR: {path} is not a directory.")
            return
    except Exception as e:
        print(f"ERROR: {path}", e)
        return
    walk_dir(path)
    mail_infos = []
    for entry in target_mails:
        if opt.debug:
            print("-->", entry.path)
        info = get_mail_info(entry.path, default_tz)
        dt_of_mtime = datetime.fromtimestamp(entry.stat().st_mtime, tz=default_tz)
        mail_date = info.get("Date")
        if mail_date is not None:
            local_date = mail_date.astimezone(tz=default_tz)
        else:
            local_date = None
        if opt.debug:
            print("  mtime:", dt_of_mtime)
            print("  Date :", mail_date)
        info.update({
                "mtime": dt_of_mtime,
                "localDate": local_date,
                })
        mail_infos.append(info)
    #
    for mi in sorted(mail_infos, key=lambda x: (x.get("Date") or x.get("mtime"))):
        print("##", mi.get("Path"))
        print("  mtime:", mi.get("mtime"))
        print("  Mail :", mi.get("Date"))
        print("  Local:", mi.get("localDate"))
        print("  From :", mi.get("From"))
        print("  Subject:", mi.get("Subject"))

def find_mail(
        path: str,
        recursive: bool,
        dt_begin: datetime,
        dt_end: datetime
        ):
    mail_infos = []  # updated in walk_dir()
    def walk_dir(path):
        with os.scandir(path) as fd:
            for entry in fd:
                if entry.name.startswith(".."):
                    continue
                elif entry.is_dir():
                    if recursive:
                        walk_dir(entry.path, recursive)
                elif entry.is_symlink():
                    continue
                else:
                    if opt.debug:
                        print("-->", entry.path)
                    info = get_mail_info(entry.path, default_tz)
                    dt = info.get("Date")
                    dt_of_mtime = datetime.fromtimestamp(entry.stat().st_mtime, tz=default_tz)
                    if opt.debug:
                        print("  mtime:", dt_of_mtime)
                        print("  Date :", dt)
                    if dt is None:
                        dt = dt_of_mtime
                    if dt.tzinfo is None:
                        dt = dt.astimezone(tz=default_tz)
                    if dt_begin <= dt <= dt_end:
                        mail_date = info.get("Date")
                        if mail_date is not None:
                            local_date = mail_date.astimezone(tz=default_tz)
                        else:
                            local_date = None
                        info.update({
                                "mtime": dt_of_mtime,
                                "localDate": local_date,
                                })
                        mail_infos.append(info)
                    else:
                        # just ignore if span doesn't exist.
                        pass
    #
    try:
        mode = os.stat(path).st_mode
        if not S_ISDIR(mode):
            print(f"ERROR: {path} is not a directory.")
            return
    except Exception as e:
        print(f"ERROR: {path}", e)
        return
    walk_dir(path)
    for mi in sorted(mail_infos, key=lambda x: (x.get("Date") or x.get("mtime"))):
        print("##", mi.get("Path"))
        print("  mtime:", mi.get("mtime"))
        print("  Mail :", mi.get("Date"))
        print("  Local:", mi.get("localDate"))
        print("  From :", mi.get("From"))
        print("  Subject:", mi.get("Subject"))

#
# set timespan
#
def set_timespan(
        ts_begin_str: str,
        ts_end_str: str
        ) -> tuple:
    #
    def get_last_day_of_month(y: int, m: int) -> int:
        next_month = datetime(y, m, 28) + timedelta(days=4)
        return (next_month - timedelta(days=next_month.day)).day
    #
    def datetime_before_year(dt: datetime, delta_y: int) -> datetime:
        if dt.year - delta_y % 4 == 0 and dt.month == 2 and dt.day == 29:
            d = 28
        else:
            d = dt.day
        return datetime(dt.year - delta_y, dt.month, d, dt.hour, dt.minute, dt.second,
                        tzinfo=dt.tzinfo)
        """
        y = dt.year - y
        try:
            return datetime(y, dt.month, dt.day, dt.hour, dt.minute, dt.second,
                            tzinfo=dt.tzinfo)
        except ValueError as e:
            if "day is out of range for month" in str(e):
                d = get_last_day_of_month(y, dt.month)
                return datetime(y, dt.month, d, dt.hour, dt.minute, dt.second,
                                tz=dt.tzinfo)
            else:
                raise
        """
    #
    def datetime_before_month(dt: datetime, delta_m: int) -> datetime:
        delta_y = delta_m // 12
        delta_m = delta_m % 12
        y = dt.year - delta_y
        m = dt.month - delta_m
        if dt.month <= delta_m:
            y -= 1
            m += 12
        try:
            return datetime(y, m, dt.day, dt.hour, dt.minute, dt.second,
                            tzinfo=dt.tzinfo)
        except ValueError as e:
            if "day is out of range for month" in str(e):
                d = get_last_day_of_month(y, m)
                return datetime(y, m, d, dt.hour, dt.minute, dt.second,
                                tz=dt.tzinfo)
            else:
                raise
    #
    def parse_timespan_string(span_str: str) -> datetime:
        if span_str is None:
            return dt_now
        elif r := re.match("(\d+)y", span_str):
            return datetime_before_year(dt_now, int(r.group(1)))
        elif r := re.match("(\d+)m", span_str):
            return datetime_before_month(dt_now, int(r.group(1)))
        else:
            if r := re.match("(\d+)w", span_str):
                delta = int(r.group(1)) * 7*24*60*60
            elif r := re.match("(\d+)d", span_str):
                delta = int(r.group(1)) * 24*60*60
            elif r := re.match("(\d+)H", span_str):
                delta = int(r.group(1)) * 60*60
            elif r := re.match("(\d+)M", span_str):
                delta = int(r.group(1)) * 60
            else:
                raise ValueError(f"unknown format {span_str}")
            return (dt_now - timedelta(seconds=delta))
    #
    dt_now = datetime.now(tz=default_tz)
    if ts_begin_str or ts_end_str:
        dt_begin = parse_timespan_string(ts_begin_str)
        dt_end = parse_timespan_string(ts_end_str)
    else:
        # default is 1 hour.
        dt_begin = dt_now - timedelta(seconds=60*60)
        dt_end = dt_now
    return dt_begin, dt_end

# main
ap = argparse.ArgumentParser()
ap.add_argument("mail_dir", help="a directory name")
ap.add_argument("-r", action="store_true", dest="recursively",
                help="enable to find a mail file recursively.")
ap.add_argument("-a", action="store", dest="ts_begin",
                help="specify the start span string.")
ap.add_argument("-b", action="store", dest="ts_end",
                help="specify the end span string.")
ap.add_argument("-m", action="store_true", dest="use_mail_date",
                help="specify to use Date field in the message.")
ap.add_argument("--help-timespan", action="store_true", dest="show_help_timespan",
                help="show help of time span.")
ap.add_argument("--tz", action="store", dest="tz_str",
                help="specify the timezone.")
ap.add_argument("-d", action="store_true", dest="debug",
                help="enable debug mode.")
opt = ap.parse_args()

if opt.show_help_timespan:
    print("""
    Example:
        -a 5H: from 5 hours ago to now.
        -a 17d -b 10d: from 17 days before, and to 10 days before.
    """)
    exit(0)

if opt.tz_str:
    tz_str = opt.tz_str
default_tz = tz.gettz(tz_str)
dt_begin, dt_end = set_timespan(opt.ts_begin, opt.ts_end)
if opt.debug:
    print("dt_begin:", dt_begin)
    print("dt_end:", dt_end)

# body
if opt.use_mail_date:
    find_mail(opt.mail_dir,
            recursive=opt.recursively,
            dt_begin=dt_begin,
            dt_end=dt_end)
else:
    find_mail_quick(opt.mail_dir,
            recursive=opt.recursively,
            dt_begin=dt_begin,
            dt_end=dt_end)
