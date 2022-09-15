"""
Counts traces, events, etc. to describe datasets.

"""
from time import time
from opyenxes.data_in.XUniversalParser import XUniversalParser

def read_XES_log(path):
    tic = time()
    print("Parsing log")
    with open(path) as log_file:
        log = XUniversalParser().parse(log_file)[0]  # take first log from file
    toc = time()
    print("Log parsed, took {} seconds..".format(toc - tic))
    return log

def count_cases(log):
    total = len(log)
    deviant = 0
    normal = 0
    for trace in log:
        attribs = trace.get_attributes()
        if str(attribs["Label"]) == str(1):
            deviant += 1
        elif str(attribs["Label"]) == str(0):
            normal += 1
    return normal, deviant, total


def count_total_events(log):
    deviant_events = 0
    normal_events = 0
    for trace in log:
        attribs = trace.get_attributes()
        events_length = len(trace)
        if str(attribs["Label"]) == str(1):
            deviant_events += events_length
        elif str(attribs["Label"]) == str(0):
            normal_events += events_length
    return normal_events, deviant_events


def calc_avg(event_count, trace_count):
    return int(round(event_count / trace_count))


def describe(description, folder, file):
    print(description)
    log = read_XES_log(folder + file)
    normal, deviant, total = count_cases(log)
    print("Norm, Deviant, Total", normal, deviant, total)
    normal_events, deviant_events = count_total_events(log)
    print("Avg norm {}, dev {}".format(calc_avg(normal_events, normal), calc_avg(deviant_events, deviant)))
    print("Avg total {}".format(calc_avg(normal_events+deviant_events, total)))


