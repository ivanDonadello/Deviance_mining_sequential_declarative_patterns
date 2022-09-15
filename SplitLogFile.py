from opyenxes.data_in.XUniversalParser import XUniversalParser
from opyenxes.data_out.XesXmlSerializer import XesXmlSerializer
from opyenxes.factory.XFactory import XFactory
import os

def read_XES_log(path, ithLog = 0):
    with open(path) as log_file:
        return XUniversalParser().parse(log_file)[ithLog]

from pathlib import Path
def mkdirs(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def extractLogCopy(log):
    new_log = XFactory.create_log(log.get_attributes().clone())
    new_log.get_extensions().update(log.get_extensions())
    new_log.__globalTraceAttributes = []
    new_log.__globalTraceAttributes.extend(log.get_global_trace_attributes())
    new_log.__globalEventAttributes = []
    new_log.__globalEventAttributes.extend(log.get_global_event_attributes())
    return new_log


if __name__ == "__main__":
    readPath = "/media/giacomo/BigData/environment/data/logs/"
    outputPath = "/media/giacomo/OutputBlank/sepsis_KR-20210716T084433Z-001/logs/"
    log_file_tagged = "sepsis_decl.xes"

    assert log_file_tagged[-3:] == "xes"
    toRead = os.path.join(readPath, log_file_tagged)
    assert os.path.isfile(toRead)
    log = read_XES_log(toRead)

    negLog = extractLogCopy(log)
    posLog = extractLogCopy(log)

    for trace in negLog:
        if trace.get_attributes()["Label"].get_value() == "1":
            posLog.append(trace)
        elif trace.get_attributes()["Label"].get_value() == "0":
            negLog.append(trace)
        else:
            assert False

    output_file = os.path.join(outputPath, log_file_tagged[:-4])
    mkdirs(log_file_tagged)
    with open(os.path.join(log_file_tagged, "model_true_true.xes"), "w") as file:
        XesXmlSerializer().serialize(posLog, file)
    with open(os.path.join(log_file_tagged, "model_false_false.xes"), "w") as file:
        XesXmlSerializer().serialize(negLog, file)