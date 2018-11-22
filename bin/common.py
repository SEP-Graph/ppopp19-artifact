#!/usr/bin/env python3
from sys import exit
from os import listdir, mkdir
from os.path import dirname, join, abspath, isdir, isfile, exists
from subprocess import getstatusoutput, getoutput
from json import load
from re import search

SCRIPT = abspath(__file__)
SCRIPT_ROOT = dirname(SCRIPT)
WORKSPACE_ROOT = dirname(SCRIPT_ROOT)
LOG_ROOT = join(WORKSPACE_ROOT, "log")
OUTPUT_ROOT = join(WORKSPACE_ROOT, "output")
DATASET_ROOT = join(WORKSPACE_ROOT, "dataset")

if not exists(LOG_ROOT):
    mkdir(LOG_ROOT)

if not exists(OUTPUT_ROOT):
    mkdir(OUTPUT_ROOT)


def parse_metadata(json_path):
    with open(json_path, "r") as fi:
        return load(fi)


def parse_all_metadata():
    res = {}

    for data_dirname in listdir(DATASET_ROOT):
        data_dirpath = join(DATASET_ROOT, data_dirname)

        if isdir(data_dirpath):
            meta_filepath = None

            for meta_filename in listdir(data_dirpath):
                meta_filepath = join(data_dirpath, meta_filename)
                if isfile(meta_filepath) and meta_filepath.endswith(".json"):
                    break

            if not meta_filepath:
                exit("Can not found metadata in folder: %s" % data_dirpath)
            res[data_dirname] = parse_metadata(meta_filepath)

    return res


def get_all_dataset_path(format="gr", undirected=True):
    if format != "gr" and format != "mtx":
        raise AttributeError("Only accepts gr or mtx format")

    res = []
    all_metadata = parse_all_metadata()

    for data_dirname, metadata in all_metadata.items():
        links = list(filter(lambda x: x.endswith(format), metadata["links"]))

        for link in links:
            data_filename = link.split("/")[-1]
            data_path = join(join(DATASET_ROOT, data_dirname), data_filename)

            if (undirected and "undirected" in link) or (not undirected and "undirected" not in link):
                res.append({"data_dirname": data_dirname, "data_filename": data_filename, "data_path": data_path})
    return res


def get_env():
    # Looking for GCC and NVCC path
    status, GCC_PATH = getstatusoutput("which gcc")
    if status == 0:
        print("Found gcc: %s" % GCC_PATH)
    else:
        exit("Could not found gcc")

    status, GPP_PATH = getstatusoutput("which g++")
    if status == 0:
        print("Found g++: %s" % GPP_PATH)
    else:
        exit("Could not found g++")

    status, NVCC_PATH = getstatusoutput("which nvcc")
    if status == 0:
        print("Found nvcc: %s" % NVCC_PATH)
    else:
        exit("Could not found nvcc")

    status, CMAKE_PATH = getstatusoutput("which cmake")
    if status == 0:
        print("Found cmake: %s" % CMAKE_PATH)
    else:
        exit("Could not found cmake")

    # Checking GCC and CUDA version
    gcc_version = getoutput("%s --version" % GCC_PATH)
    match = search("\d\.\d\.\d", gcc_version)
    if match is None:
        exit("Failed to check GCC version")

    if match.group() not in ["5.2.0", "5.3.0", "5.4.0"]:
        exit("GCC >= 5.2.0 is required, but GCC %s is found" % match.group())

    cuda_version = getoutput("%s --version" % NVCC_PATH)
    match = search("\d+\.\d", cuda_version)
    if match is None:
        exit("Failed to check CUDA version")

    if match.group() not in ["9.0", "9.1", "9.2", "10.0"]:
        exit("CUDA >= 9.0 is required, but CUDA %s is found" % match.group())

    cmake_version = getoutput("%s --version" % CMAKE_PATH)
    match = search("\d\.\d", cmake_version)
    if match is None:
        exit("Failed to check CMAKE version")

    if float(match.group()) <= 2.8:
        exit("CMAKE >= 2.8 is required, but CMAKE %s is found" % match.group())

    return {"cmake_path": CMAKE_PATH, "gcc_path": GCC_PATH, "gpp_path": GPP_PATH}


def get_gpu_model():
    status, gpu_model = getstatusoutput("nvidia-smi --query-gpu=name --format=csv,noheader --id=0")

    gpu_model = gpu_model.strip()
    SUPPORTED_LIST = ["1080", "P100", "V100"]

    if status != 0:
        return "unknown"
    else:
        for key_word in SUPPORTED_LIST:
            if key_word in gpu_model:
                return gpu_model
        return "unsupported"


def get_gpu_ram():
    status, gpu_ram = getstatusoutput("nvidia-smi --query-gpu=memory.total --format=csv,noheader --id=0")

    gpu_ram = gpu_ram.strip()

    if status != 0:
        return -1
    else:
        return int(gpu_ram.split(' ')[0])
