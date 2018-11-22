#!/usr/bin/env python3
from sys import argv, exit
from os.path import join
from os import listdir
from re import search
from json import load
from common import LOG_ROOT


def parse_gunrock(algo_name):
    result = {}

    for log_name in listdir(LOG_ROOT):
        match = search("Gunrock_%s_(.*?)_" % algo_name, log_name)

        if match:
            log_path = join(LOG_ROOT, log_name)
            dataset = match.groups()[0]
            time = None

            with open(log_path, 'r') as fi:
                json = load(fi)
                if 'process_times' in json:
                    time = float(json['process_times'][0])

            if dataset not in result:
                result[dataset] = []
            if time:
                result[dataset].append(time)

    return result


def parse_groute(algo_name):
    result = {}

    for log_name in listdir(LOG_ROOT):
        match = search("Groute_%s_(.*?)_" % algo_name, log_name)

        if match:
            log_path = join(LOG_ROOT, log_name)
            dataset = match.groups()[0]
            time = None

            with open(log_path, 'r') as fi:
                for line in fi:
                    match = search("(\d+\.\d+) ms. <filter>", line)
                    if match:
                        time = float(match.groups()[0])

            if dataset not in result:
                result[dataset] = []
            if time:
                result[dataset].append(time)

    return result


def parse_sep(algo_name):
    result = {}

    for log_name in listdir(LOG_ROOT):
        match = search("SEP_%s_(.*?)_" % algo_name, log_name)

        if match:
            log_path = join(LOG_ROOT, log_name)
            dataset = match.groups()[0]
            time = None

            with open(log_path, 'r') as fi:
                json = load(fi)
                if 'time_total' in json:
                    time = float(json['time_total'])

            if dataset not in result:
                result[dataset] = []
            if time:
                result[dataset].append(time)

    return result


def avg_time(time_list):
    if len(time_list) < 3:
        return sum(time_list) / len(time_list)

    return (sum(time_list) - max(time_list) - min(time_list)) / (len(time_list) - 2)


def print_result(algo_name):
    gunrock_result = parse_gunrock(algo_name)
    groute_result = parse_groute(algo_name)
    sep_result = parse_sep(algo_name)

    dataset = set()
    for name in gunrock_result.keys():
        dataset.add(name)
    for name in groute_result.keys():
        dataset.add(name)
    for name in sep_result.keys():
        dataset.add(name)

    dataset = sorted(dataset)

    for name in dataset:
        print(",%s" % name, end='')

    print('\nGunrock,', end='')

    for name in dataset:
        if name not in gunrock_result:
            print('-,', end='')
        else:
            print("%f," % avg_time(gunrock_result[name]), end='')

    print('\nGroute,', end='')

    for name in dataset:
        if name not in groute_result:
            print('-,', end='')
        else:
            print("%f," % avg_time(groute_result[name]), end='')

    print('\nSEP-Graph,', end='')

    for name in dataset:
        if name not in sep_result:
            print('-,', end='')
        else:
            print("%f," % avg_time(sep_result[name]), end='')

    print()


if __name__ == '__main__':
    if len(argv) != 2:
        exit("Usage: parse_all.py algo_name (bc, bfs, sssp, pr)")

    algo_name = argv[1]
    if algo_name not in ['bc', 'bfs', 'sssp', 'pr']:
        exit("Unsupported algorithm")

    print_result(algo_name)
