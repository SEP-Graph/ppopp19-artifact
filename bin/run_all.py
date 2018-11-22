#!/usr/bin/env python3
from os.path import join
from os import system
from common import SCRIPT_ROOT, get_gpu_model, OUTPUT_ROOT

gpu_model = get_gpu_model()
print("This script will evaluate Gunrock, Groute and SEP-Graph on \"%s\"" % gpu_model)

n_times = 5

for i in range(1, n_times + 1):
    print("Evaluating Gunrock (%d/%d)" % (i, n_times))
    system(join(SCRIPT_ROOT, "run_gunrock_bc.py"))
    system(join(SCRIPT_ROOT, "run_gunrock_bfs.py"))
    system(join(SCRIPT_ROOT, "run_gunrock_pr.py"))
    system(join(SCRIPT_ROOT, "run_gunrock_sssp.py"))

if 'V100' in gpu_model:
    print('"Skip Groute evaluation on %s"' % gpu_model)
else:
    for i in range(1, n_times + 1):
        print("Evaluating Groute (%d/%d)" % (i, n_times))
        system(join(SCRIPT_ROOT, "run_groute_bc.py"))
        system(join(SCRIPT_ROOT, "run_groute_bfs.py"))
        system(join(SCRIPT_ROOT, "run_groute_pr.py"))
        system(join(SCRIPT_ROOT, "run_groute_sssp.py"))

for i in range(1, n_times + 1):
    print("Evaluation SEP-Graph (%d/%d)" % (i, n_times))
    system(join(SCRIPT_ROOT, "run_sep_bc.py"))
    system(join(SCRIPT_ROOT, "run_sep_bfs.py"))
    system(join(SCRIPT_ROOT, "run_sep_pr.py"))
    system(join(SCRIPT_ROOT, "run_sep_sssp.py"))

PARSER_PATH = join(SCRIPT_ROOT, "parse_all.py")
for algo_name in ['bc', 'bfs', 'sssp', 'pr']:
    log_path = join(OUTPUT_ROOT, '%s.csv' % algo_name)
    system('%s %s > %s' % (PARSER_PATH, algo_name, log_path))

system("%s" % join(SCRIPT_ROOT, "run_fig7.py"))
system("%s" % join(SCRIPT_ROOT, "run_fig8.py"))
print("Result saved: %s" % OUTPUT_ROOT)
