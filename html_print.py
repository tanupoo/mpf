#!/usr/bin/env python

from html.parser import HTMLParser
from argparse import ArgumentParser
import sys

debug = True

class MyHTMLParser(HTMLParser):

    def __init__(self, indent_unit=2, debug=False, *args, **kwargs):
        HTMLParser.__init__(self, *args, **kwargs)
        self.indent_unit = indent_unit
        self.debug = debug
        self.indent = 0

    def debug_print(self, trig: str, *args):
        print(f"- {trig}: {self.get_starttag_text}", flush=True)

    def handle_starttag(self, tag, attrs):
        if self.debug:
            self.debug_print("starttag()", tag, attrs)
        line_text = self.get_starttag_text()
        print(f"{' '*self.indent}{line_text}", flush=True)
        if tag not in ["meta", "link", "input"]:
            self.indent += self.indent_unit

    def handle_data(self, data):
        if self.debug:
            self.debug_print("data()", data)
        data = data.strip()
        if data:
            #print(f"{' '*self.indent}{data}", flush=True)
            print(f"{data}", flush=True)

    def handle_endtag(self, tag):
        if self.debug:
            self.debug_print("endtag()", tag)
        self.indent -= self.indent_unit
        print(f"{' '*self.indent}</{tag}>", flush=True)

    def handle_startendtag(self, tag, attrs):
        if self.debug:
            self.debug_print("startendtag()", tag, attrs)
        print(f"/>", end="", flush=True)

    def handle_comment(self, data):
        if self.debug:
            self.debug_print("comment()", data)
        print(f"{' '*self.indent}<!--{data}-->", flush=True)

    def handle_decl(self, decl):
        if self.debug:
            self.debug_print("decl()", decl)
        print(f"{' '*self.indent}<!{decl}>", flush=True)

    def handle_pi(self, data):
        if self.debug:
            self.debug_print("pi()", data)
        print(f"{' '*self.indent}<!{data}>", flush=True)

    def unknown_decl(self, data):
        if self.debug:
            self.debug_print("unknown()", data)
        print(f"{' '*self.indent}<!{data}>", flush=True)

#
# main
#
def do_parse(fd, indent_unit=2, debug=False):
    try:
        html_text = fd.read()
        p = MyHTMLParser(indent_unit=indent_unit, debug=debug)
        p.feed(html_text)
        p.close()
    except ValueError as e:
        print("ERROR", e)
        exit(1)

ap = ArgumentParser()
ap.add_argument("file", nargs="*")
ap.add_argument("-i", action="store", dest="indent",
                type=int, default=2,
                help="specify the indent size.")
ap.add_argument("-d", action="store_true", dest="debug",
                help="enable debug mode.")
opt = ap.parse_args()

if len(opt.file) == 0:
    do_parse(sys.stdin, indent_unit=opt.indent, debug=opt.debug)
else:
    for f in opt.file:
        do_parse(open(f), indent_unit=opt.indent, debug=opt.debug)

