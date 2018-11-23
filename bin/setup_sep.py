#!/usr/bin/env python3
from os.path import exists, join
from os import mkdir, system, chdir
from common import WORKSPACE_ROOT, get_env

SEP_PATH = join(WORKSPACE_ROOT, "sep-graph")
SEP_BUILD_PATH = join(SEP_PATH, "build")

chdir(WORKSPACE_ROOT)

if not exists(SEP_PATH):
    exit("Could not found %s. Make sure you clone the project with --recursive flag" % SEP_PATH)

chdir(SEP_PATH)

if not exists(SEP_BUILD_PATH):
    mkdir(SEP_BUILD_PATH)

chdir(SEP_BUILD_PATH)

env_dict = get_env()
CMAKE_PATH = env_dict["cmake_path"]
GCC_PATH = env_dict["gcc_path"]
GPP_PATH = env_dict["gpp_path"]
# -DCUDA_TOOLKIT_ROOT_DIR=/opt/cuda-9.1 you may use this parameter
system("%s .. -DCMAKE_C_COMPILER=%s -DCMAKE_CXX_COMPILER=%s" % (CMAKE_PATH, GCC_PATH, GPP_PATH))
system("n=$(nproc) && make -j $n")
