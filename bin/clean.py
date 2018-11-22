#!/usr/bin/env python3
from os.path import join
from os import system
from common import WORKSPACE_ROOT, LOG_ROOT, OUTPUT_ROOT

rtn = input("%s/* will be REMOVED. (y/n)" % LOG_ROOT)
if rtn == "y":
    system("rm -f %s/*" % LOG_ROOT)

rtn = input("%s/* will be REMOVED. (y/n)" % OUTPUT_ROOT)
if rtn == "y":
    system("rm -f %s/*" % OUTPUT_ROOT)

GUNROCK_PATH = join(WORKSPACE_ROOT, "gunrock")
GUNROCK_BUILD_PATH = join(GUNROCK_PATH, "build")

rtn = input("%s will be REMOVED. (y/n)" % GUNROCK_BUILD_PATH)
if rtn == "y":
    system("rm -rf %s" % GUNROCK_BUILD_PATH)

GROUTE_PATH = join(WORKSPACE_ROOT, "groute")
GROUTE_BUILD_PATH = join(GROUTE_PATH, "build")

rtn = input("%s will be REMOVED. (y/n)" % GROUTE_BUILD_PATH)
if rtn == "y":
    system("rm -rf %s" % GROUTE_BUILD_PATH)

SEP_PATH = join(WORKSPACE_ROOT, "sep-graph")
SEP_BUILD_PATH = join(SEP_PATH, "build")
rtn = input("%s will be REMOVED. (y/n)" % SEP_BUILD_PATH)
if rtn == "y":
    system("rm -rf %s" % SEP_BUILD_PATH)
