#!/usr/bin/env python3
from os.path import exists, join
from time import time
from sys import exit
from subprocess import getstatusoutput
from common import DATASET_ROOT, WORKSPACE_ROOT, LOG_ROOT, parse_all_metadata, get_gpu_ram

SEP_PATH = join(WORKSPACE_ROOT, "sep-graph")
SEP_BUILD_PATH = join(SEP_PATH, "build")
BC_BINARY_PATH = join(SEP_BUILD_PATH, "hybrid_bc")

if not exists(BC_BINARY_PATH):
    exit("Could not found BC binary")

for data_dirname, metadata in parse_all_metadata().items():
    link = next((x for x in metadata["links"] if "undirected" in x and x.endswith("gr")), None)
    data_filename = link.split("/")[-1]
    data_path = join(join(DATASET_ROOT, data_dirname), data_filename)

    if not exists(data_path):
        exit("Could not found file %s" % data_path)

    # required parameter
    is_sparse = metadata["sparse"]
    source_node = metadata["source_node"]
    # If the total RAM more than 12GB, we will store CSR and CSC format in global memory. (for better performance)
    # If the total RAM less than 12GB, we only store CSR format, because the dataset is undirected!
    treat_as_undirected = get_gpu_ram() < 12000

    # optional parameter
    alpha = None
    beta = None
    if not bool(is_sparse):
        alpha = metadata["SEP_bfs_alpha"]
        beta = metadata["SEP_bfs_beta"]
    block_size = metadata.get("block_size", "256")

    timestamp = str(int(time()))
    log_path = join(LOG_ROOT, "SEP_bc_%s_%s.json" % (data_dirname, timestamp))
    cmd = "%s -graphfile=%s" \
          " -undirected=%s" \
          " -source_node=%s" \
          " -sparse=%s" \
          " %s" \
          " -block_size=%s" \
          " -json=%s" % (
              BC_BINARY_PATH,
              data_path,
              treat_as_undirected,
              source_node,
              is_sparse,
              "" if bool(is_sparse) else "-alpha=%s -beta=%s" % (alpha, beta), block_size, log_path)

    print('Evaluating BC implemented on SEP-Graph for "%s" dataset' % data_dirname)

    # run the program
    status, output = getstatusoutput(cmd)

    if status != 0:
        print('Failed to run: "%s"' % cmd)
        exit(output)

    print("--------------")
