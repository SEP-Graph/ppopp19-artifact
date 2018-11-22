#!/usr/bin/env python3
from os.path import exists, join
from time import time
from sys import exit
from subprocess import getstatusoutput
from common import WORKSPACE_ROOT, DATASET_ROOT, LOG_ROOT, get_all_dataset_path, parse_all_metadata

GROUTE_PATH = join(WORKSPACE_ROOT, "groute")
GROUTE_BUILD_PATH = join(GROUTE_PATH, "build")
BFS_BINARY_PATH = join(GROUTE_BUILD_PATH, "bfs")

if not exists(BFS_BINARY_PATH):
    exit("Could not found BFS binary")

for data_dirname, metadata in parse_all_metadata().items():
    link = next((x for x in metadata["links"] if "undirected" in x and x.endswith("gr")), None)
    data_filename = link.split("/")[-1]
    data_path = join(join(DATASET_ROOT, data_dirname), data_filename)

    if not exists(data_path):
        exit("Could not found file %s" % data_path)

    # required parameter
    is_sparse = bool(metadata["sparse"])
    source_node = metadata["source_node"]
    prio_delta = metadata["Groute_bfs_prio_delta_fused"]

    timestamp = str(int(time()))
    log_path = join(LOG_ROOT, "Groute_bfs_%s_%s.log" % (data_dirname, timestamp))
    cmd = "%s" \
          " -graphfile=%s" \
          " -num_gpus=1" \
          " -startwith=1" \
          " -wl_alloc_factor=0.4" \
          " -prio_delta=%s" \
          " -source_node=%s" \
          " -cta_np=%s" % (
              BFS_BINARY_PATH,
              data_path,
              prio_delta,
              source_node,
              not is_sparse)

    print('Evaluating BFS implemented on Groute for "%s" dataset' % data_dirname)


    # run the program
    status, output = getstatusoutput(cmd)

    if status != 0:
        print('Failed to run: "%s"' % cmd)
        exit(output)

    with open(log_path, "w") as fo:
        fo.write("cmd: %s\n\n" % cmd)
        fo.write(output)

    print("--------------")
