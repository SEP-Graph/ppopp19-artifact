#!/usr/bin/env python3
from os import system, chdir, path, mkdir
from os.path import join
from common import WORKSPACE_ROOT, get_env

GROUTE_PATH = path.join(WORKSPACE_ROOT, "groute")
GROUTE_BUILD_PATH = path.join(GROUTE_PATH, "build")

chdir(WORKSPACE_ROOT)

if not path.exists(GROUTE_PATH):
    system("git clone --recursive https://github.com/groute/groute.git")
    chdir(GROUTE_PATH)
    system("git checkout 7a77c467867b55c92110bad019447eb305fe6ec1")
    system("git apply %s" % (join(WORKSPACE_ROOT, "groute.patch")))

chdir(GROUTE_PATH)

if not path.exists(GROUTE_BUILD_PATH):
    mkdir(GROUTE_BUILD_PATH)

chdir(GROUTE_BUILD_PATH)

env_dict = get_env()
CMAKE_PATH = env_dict["cmake_path"]
GCC_PATH = env_dict["gcc_path"]
GPP_PATH = env_dict["gpp_path"]

system("cmake .. -DCMAKE_C_COMPILER=%s -DCMAKE_CXX_COMPILER=%s" % (GCC_PATH, GPP_PATH))
system("n=$(nproc) && make -j $n")
