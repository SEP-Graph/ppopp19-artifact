#!/usr/bin/env python3
from os.path import exists, join
from time import time
from sys import exit
from re import search
from subprocess import getstatusoutput
from common import WORKSPACE_ROOT, DATASET_ROOT, LOG_ROOT, get_all_dataset_path, parse_all_metadata

GUNROCK_PATH = join(WORKSPACE_ROOT, "gunrock")
GUNROCK_BUILD_PATH = join(GUNROCK_PATH, "build")
GUNROCK_BIN_PATH = join(GUNROCK_BUILD_PATH, "bin")
PR_BINARY_PATH = join(GUNROCK_BIN_PATH, "pr")

if not exists(PR_BINARY_PATH):
    exit("Could not found Pagerank binary")

for data_dirname, metadata in parse_all_metadata().items():
    link = next((x for x in metadata["links"] if "undirected" in x and x.endswith("mtx")), None)
    data_filename = link.split("/")[-1]
    data_path = join(join(DATASET_ROOT, data_dirname), data_filename)

    if not exists(data_path):
        exit("Could not found file %s" % data_path)

    timestamp = str(int(time()))

    log_path = join(LOG_ROOT, "Gunrock_pr_%s_%s.json" % (data_dirname, timestamp))
    cmd = "%s" \
          " market %s" \
          " --device=0" \
          " --jsonfile=%s" \
          " --quick" % (
              PR_BINARY_PATH,
              data_path,
              log_path)

    print('Evaluating Pagerank implemented on Gunrock for "%s" dataset' % data_dirname)

    # run the program
    status, output = getstatusoutput(cmd)

    if status != 0:
        print('Failed to run: "%s"' % cmd)
        exit(output)

    match = search("Total rank : (\d+\.\d+)", output)
    # if match:
        # print("Total rank: %s\n" % match.groups()[0])
    print("--------------")
