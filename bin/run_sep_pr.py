#!/usr/bin/env python3
from os.path import exists, join
from time import time
from sys import exit
from subprocess import getstatusoutput
from common import DATASET_ROOT, WORKSPACE_ROOT, LOG_ROOT, parse_all_metadata, get_gpu_ram

SEP_PATH = join(WORKSPACE_ROOT, "sep-graph")
SEP_BUILD_PATH = join(SEP_PATH, "build")
PR_BINARY_PATH = join(SEP_BUILD_PATH, "hybrid_pr")

if not exists(PR_BINARY_PATH):
    exit("Could not found Pagerank binary")

for data_dirname, metadata in parse_all_metadata().items():
    link = next((x for x in metadata["links"] if "undirected" in x and x.endswith("gr")), None)
    data_filename = link.split("/")[-1]
    data_path = join(join(DATASET_ROOT, data_dirname), data_filename)

    if not exists(data_path):
        exit("Could not found file %s" % data_path)

    is_sparse = metadata['sparse']
    pr_error_tolerance = metadata["SEP_pr_error"]
    # If the total RAM more than 12GB, we will store CSR and CSC format in global memory. (for better performance)
    # If the total RAM less than 12GB, we only store CSR format, because the dataset is undirected!
    treat_as_undirected = get_gpu_ram() < 12000


    timestamp = str(int(time()))
    log_path = join(LOG_ROOT, "SEP_pr_%s_%s.json" % (data_dirname, timestamp))

    cmd = "%s" \
          " -undirected=%s" \
          " -graphfile=%s" \
          " -error=%s" \
          " -wl_alloc_factor=0.4" \
          " -sparse=%s" \
          " -json=%s" % (
              PR_BINARY_PATH,
              treat_as_undirected,
              data_path,
              pr_error_tolerance,
              is_sparse,
              log_path)

    print('Evaluating Pagerank implemented on SEP-Graph for "%s" dataset' % data_dirname)

    # run the program
    status, output = getstatusoutput(cmd)

    if status != 0:
        print('Failed to run: "%s"' % cmd)
        exit(output)

    print("--------------")
