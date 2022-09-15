import os
import sys

from opyenxes.data_out.XesXmlSerializer import XesXmlSerializer
from opyenxes.factory.XFactory import XFactory

from DevianceMiningPipeline.DataPreparation.RetagLogWithUniqueIds import changeLog
from DevianceMiningPipeline.LogTaggingViaPredicates import logTagger


def main(argv):
    assert (len(argv)>=4)
    posLogFile = argv[1]
    negLogFile = argv[2]
    mergedFile = argv[3]
    finalPosName, posLog = changeLog(posLogFile, True)
    finalNegName, negLog = changeLog(negLogFile, True, len(posLog)+1)

    print("Checking that the ids are unique")
    l = list(map(lambda x: x.get_attributes()["concept:name"].get_value(), posLog))
    l.extend(map(lambda x: x.get_attributes()["concept:name"].get_value(), negLog))
    assert (len(l) == len(set(l)))
    print("OK!")

    print("Tagging the dataset")
    logTagger(posLog, lambda x: True, False, False)
    logTagger(negLog, lambda x: False, False, False)

    logProps = posLog.get_attributes().clone()
    logProps.update(negLog.get_attributes())
    new_log = XFactory.create_log(logProps)
    new_log.get_extensions().update(posLog.get_extensions())
    new_log.get_extensions().update(negLog.get_extensions())


    # new_log.__classifiers = log.get_classifiers().copy()
    new_log.__globalTraceAttributes = []
    new_log.__globalTraceAttributes.extend(posLog.get_global_trace_attributes())
    new_log.__globalTraceAttributes.extend(negLog.get_global_trace_attributes())
    new_log.__globalEventAttributes = []
    new_log.__globalEventAttributes.extend(posLog.get_global_event_attributes())
    new_log.__globalEventAttributes.extend(negLog.get_global_event_attributes())

    for negTrace in negLog:
        #negTrace.get_attributes()["Label"] = XFactory.create_attribute_literal("Label", "1" if (str(negTrace.get_attributes()["Label"]) == "1") else "0")
        #del negTrace.get_attributes()["Label"]
        new_log.append(negTrace)
    for negTrace in posLog:
        #negTrace.get_attributes()["Label"] = XFactory.create_attribute_literal("Label", "1" if (str(negTrace.get_attributes()["Label"]) == "1") else "0")
        #del negTrace.get_attributes()["Label"]
        new_log.append(negTrace)



    with open(mergedFile, "w") as file:
        XesXmlSerializer().serialize(new_log, file)

if __name__ == '__main__':
    main(["", "/media/giacomo/BigData/environment/data/logs/bank_pos.xes", "/media/giacomo/BigData/environment/data/logs/bank_neg.xes",  "/media/giacomo/BigData/environment/data/logs/bank.xes"])