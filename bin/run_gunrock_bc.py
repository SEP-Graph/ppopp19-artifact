#!/usr/bin/env python3
from os.path import exists, join
from time import time
from sys import exit
from subprocess import getstatusoutput
from common import WORKSPACE_ROOT, DATASET_ROOT, LOG_ROOT, get_all_dataset_path, parse_all_metadata

GUNROCK_PATH = join(WORKSPACE_ROOT, "gunrock")
GUNROCK_BUILD_PATH = join(GUNROCK_PATH, "build")
GUNROCK_BIN_PATH = join(GUNROCK_BUILD_PATH, "bin")
BC_BINARY_PATH = join(GUNROCK_BIN_PATH, "bc")

if not exists(BC_BINARY_PATH):
    exit("Could not found BC binary")

for data_dirname, metadata in parse_all_metadata().items():
    link = next((x for x in metadata["links"] if "undirected" in x and x.endswith("mtx")), None)
    data_filename = link.split("/")[-1]
    data_path = join(join(DATASET_ROOT, data_dirname), data_filename)

    if not exists(data_path):
        exit("Could not found file %s" % data_path)

    source_node = metadata["source_node"]
    traversal_mode = metadata["Gunrock_traversal_mode"]
    timestamp = str(int(time()))

    log_path = join(LOG_ROOT, "Gunrock_bc_%s_%s.json" % (data_dirname, timestamp))
    cmd = "%s" \
          " market %s" \
          " --device=0" \
          " --traversal-mode=%s" \
          " --src=%s" \
          " --jsonfile=%s" \
          " --quick" % (
        BC_BINARY_PATH,
        data_path,
        traversal_mode,
        source_node,
        log_path)

    print('Evaluating BC implemented on Gunrock for "%s" dataset' % data_dirname)

    # run the program
    status, output = getstatusoutput(cmd)

    if status != 0:
        print('Failed to run: "%s"' % cmd)
        exit(output)

    print("--------------")
