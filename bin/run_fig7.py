#!/usr/bin/env python3
from os.path import exists, join
from time import time
from sys import exit
from subprocess import getstatusoutput
from re import search, compile
from common import DATASET_ROOT, WORKSPACE_ROOT, OUTPUT_ROOT, parse_all_metadata, get_gpu_ram

SEP_PATH = join(WORKSPACE_ROOT, "sep-graph")
SEP_BUILD_PATH = join(SEP_PATH, "build")
PR_BINARY_PATH = join(SEP_BUILD_PATH, "hybrid_pr")

if not exists(PR_BINARY_PATH):
    exit("Could not found Pagerank binary")

for data_dirname, metadata in parse_all_metadata().items():
    fig_subname = None
    if data_dirname == 'kron':
        fig_subname = 'a'
    elif data_dirname == 'road_usa':
        fig_subname = 'b'
    else:
        continue

    link = next((x for x in metadata["links"] if "undirected" in x and x.endswith("gr")), None)
    data_filename = link.split("/")[-1]
    data_path = join(join(DATASET_ROOT, data_dirname), data_filename)

    if not exists(data_path):
        exit("Could not found file %s" % data_path)

    is_sparse = metadata['sparse']
    # If the total RAM more than 12GB, we will store CSR and CSC format in global memory. (for better performance)
    # If the total RAM less than 12GB, we only store CSR format, because the dataset is undirected!
    treat_as_undirected = get_gpu_ram() < 12000

    timestamp = str(int(time()))

    cmd = "%s" \
          " -undirected=%s" \
          " -graphfile=%s" \
          " -wl_alloc_factor=0.4" \
          " -sparse=%s" \
          " -wl_sort" \
          " -trace" % (
              PR_BINARY_PATH,
              treat_as_undirected,
              data_path,
              is_sparse)

    print('Evaluating Fig7 on SEP-Graph for "%s" dataset' % data_dirname)

    # run the program
    status, output = getstatusoutput(cmd)

    if status != 0:
        print('Failed to run: "%s"' % cmd)
        exit(output)
    else:
        log_path = join(OUTPUT_ROOT, "fig7_%s.csv" % fig_subname)
        pattern = compile('Round: (\d+) Policy to execute: (.*?) Time: (\d+\.\d+)')

        with open(log_path, 'w') as fo:
            fo.write('Round,Variant,Time\n')

            for line in output.split('\n'):
                match = search(pattern, line)

                if match:
                    round = match.groups()[0]
                    variant_name = match.groups()[1]
                    exe_time = match.groups()[2]
                    fo.write('%s,%s,%s\n' % (round, variant_name, exe_time))
    print("--------------")
