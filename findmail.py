#!/usr/bin/env python

import os
from stat import S_ISDIR
import time
import argparse
from decode_mime import decode_mime_file, decode_subject

def get_info(path) -> dict:
    filename, ext = os.path.splitext(path)
    info = {}
    info.update({"Path": path})
    with open(path) as fd:
        for line in fd:
            if len(line) == 0:
                # only scan the headers.
                break
            line = line.strip()
            if line.startswith("Subject:"):
                info.update({"Subject": decode_subject(line)})
            if line.startswith("Date:"):
                info.update({"Date": line})
            if line.startswith("From:"):
                info.update({"From": decode_subject(line)})
        return info

def walk_dir(path, recursive=False, newer_than=None):
    mails = []
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
                if entry.stat().st_mtime > newer_than:
                    mails.append(entry)
                else:
                    pass
            else:
                mails.append(entry)
    for e in sorted(mails, key=lambda x: x.stat().st_mtime):
        info = get_info(e.path)
        print("##", info.get("Date"))
        print("  -", info.get("From"))
        print("  -", info.get("Subject"))
        print("  -", info.get("Path"))

def find_mail(path, recursive=False, newer_than=None):
    try:
        mode = os.stat(path).st_mode
        if not S_ISDIR(mode):
            print(f"ERROR: {path} is not a directory.")
            return
    except Exception as e:
        print(f"ERROR: {path}", e)
        return
    walk_dir(path, recursive, newer_than)

# main
ap = argparse.ArgumentParser()
ap.add_argument("mail_dir", help="a directory name")
ap.add_argument("-r", action="store_true", dest="recursively",
                help="enable to find a mail file recursively.")
ap.add_argument("-d", action="store_true", dest="debug",
                help="enable debug mode.")
opt = ap.parse_args()
ts = time.time() - 24*60*60  # 1day before
ts = time.time() - 7*24*60*60  # 1day before
ts = time.time() - 14*24*60*60  # 1day before
ts = time.time() - 30*60  # 1day before

# body
find_mail(opt.mail_dir, recursive=opt.recursively, newer_than=ts)
