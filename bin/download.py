#!/usr/bin/env python3
from os import listdir, system
from os.path import exists, join, isdir, isfile
from sys import exit
from common import DATASET_ROOT, parse_all_metadata

if not exists(DATASET_ROOT):
    exit("Can not found dataset path")

res = parse_all_metadata()

for data_dirname, metadata in res.items():
    links = metadata["links"]

    for link in links:
        data_filename = link.split("/")[-1]
        data_dirpath = join(DATASET_ROOT, data_dirname)
        data_path = join(data_dirpath, data_filename)

        if exists(data_path):
            print("%s exists" % data_filename)
        else:
            system('wget -P %s %s' % (data_dirpath, link))

print("All dataset downloaded")
