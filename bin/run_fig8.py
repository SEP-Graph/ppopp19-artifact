#!/usr/bin/env python3
from os.path import exists, join
from time import time
from sys import exit
from subprocess import getstatusoutput
from re import search, compile
from common import DATASET_ROOT, WORKSPACE_ROOT, OUTPUT_ROOT, parse_all_metadata, get_gpu_ram

SEP_PATH = join(WORKSPACE_ROOT, "sep-graph")
SEP_BUILD_PATH = join(SEP_PATH, "build")
SSSP_BINARY_PATH = join(SEP_BUILD_PATH, "hybrid_sssp")

if not exists(SSSP_BINARY_PATH):
    exit("Could not found SSSP binary")

for data_dirname, metadata in parse_all_metadata().items():
    if data_dirname != 'soc-twitter':
        continue

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
        alpha = metadata["SEP_sssp_alpha"]
        beta = metadata["SEP_sssp_beta"]
    block_size = metadata.get("block_size", "256")

    timestamp = str(int(time()))
    cmd = "%s" \
          " -graphfile=%s" \
          " -undirected=%s" \
          " -source_node=%s" \
          " -sparse=%s" \
          " -trace" \
          " %s" \
          " -block_size=%s" % (
              SSSP_BINARY_PATH,
              data_path,
              treat_as_undirected,
              source_node,
              is_sparse,
              "" if bool(is_sparse) else "-alpha=%s -beta=%s" % (alpha, beta), block_size)

    print('Evaluating Fig8 on SEP-Graph on SEP-Graph for "%s" dataset' % data_dirname)

    # run the program
    status, output = getstatusoutput(cmd)

    if status != 0:
        print('Failed to run: "%s"' % cmd)
        exit(output)
    else:
        pattern = compile(
            "Round: (\d+) Policy to execute: (.*?) Time: (\d+\.\d+) In-nodes: (\d+) Out-nodes: (\d+) Input-edges: (\d+) Output-edges: (\d+) Total-workload: (\d+)")
        nodes = None
        log_path = join(OUTPUT_ROOT, "fig8.csv")

        with open(log_path, 'w') as fo:
            fo.write("Round,Variant,E'/outDegree(A),|V|/|A|\n")

            for line in output.split('\n'):
                match = search('(\d+) nodes', line)
                if match:
                    nodes = int(match.groups()[0])

                match = search(pattern, line)
                if match:
                    round = match.groups()[0]
                    variant = match.groups()[1]
                    A_len = int(match.groups()[4])
                    out_degree = int(match.groups()[6])
                    E = int(match.groups()[7])
                    if out_degree > 0 and A_len > 0:
                        fo.write("%s,%s,%d,%d\n" % (round, variant, E // out_degree, nodes // A_len))
