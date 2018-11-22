#!/usr/bin/env python3
from os import system, chdir, path, mkdir
from common import WORKSPACE_ROOT, get_env

GUNROCK_PATH = path.join(WORKSPACE_ROOT, "gunrock")
GUNROCK_BUILD_PATH = path.join(GUNROCK_PATH, "build")
BOOST_PATH = path.join(WORKSPACE_ROOT, "boost_1_58_0")

if not path.exists(BOOST_PATH):
    print("cd " + WORKSPACE_ROOT)
    chdir(WORKSPACE_ROOT)

    print("Downloading Boost 1.58.0")
    system("wget -P /tmp/ http://sourceforge.net/projects/boost/files/boost/1.58.0/boost_1_58_0.tar.bz2")

    system("rm -rf /tmp/boost_1_58_0")

    print("Extracting boost into /tmp/boost_1_58_0")
    system("tar -xjvf /tmp/boost_1_58_0.tar.bz2 -C /tmp/")

    print("cd /tmp/boost_1_58_0")
    chdir("/tmp/boost_1_58_0")

    print("Run bootstrap.sh")
    system("./bootstrap.sh")

    print("Run \"b2 install --prefix=%s\"" % BOOST_PATH)
    system("./b2 install --prefix=" + BOOST_PATH)

    if path.exists(BOOST_PATH):
        print("Boost Installed!")
    else:
        exit("Failed to install Boost")

chdir(WORKSPACE_ROOT)

if not path.exists(GUNROCK_PATH):
    system("git clone --recursive https://github.com/gunrock/gunrock.git")
    chdir(GUNROCK_PATH)
    system("git checkout b3416cbcd59c393e3bb9a7fccc81810acf5f04d5")

chdir(GUNROCK_PATH)

if not path.exists(GUNROCK_BUILD_PATH):
    mkdir(GUNROCK_BUILD_PATH)

chdir(GUNROCK_BUILD_PATH)

env_dict = get_env()
CMAKE_PATH = env_dict["cmake_path"]
GCC_PATH = env_dict["gcc_path"]
GPP_PATH = env_dict["gpp_path"]

system(
    "cmake .. -DBoost_NO_BOOST_CMAKE=TRUE -DBoost_NO_SYSTEM_PATHS=TRUE -DBOOST_ROOT=%s -DCMAKE_C_COMPILER=%s -DCMAKE_CXX_COMPILER=%s" % (
    BOOST_PATH, GCC_PATH, GPP_PATH))
system("n=$(nproc) && make -j $n")