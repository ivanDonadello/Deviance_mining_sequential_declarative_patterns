"""

Performing a fair split of the traces. (We could be more accurate than that, but that code is in C++)

@author: Giacomo Bergami
"""
import os
from random import shuffle

from opyenxes.data_out.XesXmlSerializer import XesXmlSerializer
from opyenxes.factory.XFactory import XFactory
import numpy
from DevianceMiningPipeline.utils import TraceUtils


def joonas_split_log_train_test(log, train_size):
    last_ind = (int)(len(log) * train_size)
    return log[:last_ind], log[last_ind:]

def abstractFairSplit(sequence, labelPredicate, getId, training_test_split):
    """
    Provides an abstract implementation of a binary fair split

    :param sequence:                Sequence of arbitrary items to be splitted in two
    :param labelPredicate:          Predicate to be used in order to assess the quality of the split
    :param training_test_split:     Percentage of training/testing

    :return:    Two distinct datasets for training and testing
    """
    traceCount = 0
    trueTraceOffset = []
    falseTraceOffset = []
    assert (isinstance(training_test_split, float))
    l = sequence
    if not (isinstance(sequence, list)):
        l = list(sequence)
    for item in l:
        if (labelPredicate(item)):
            trueTraceOffset.append(traceCount)
        else:
            falseTraceOffset.append(traceCount)
        traceCount = traceCount +1

    trueLen = float(len(trueTraceOffset))
    falseLen = float(len(falseTraceOffset))
    if not (int(training_test_split * trueLen) > 0):
        raise Exception("Error: the potitive elements in the training dataset for each split should "
                        "contain at least one trace: please re-formulate the tagging!")
    if not (int((1.0 - training_test_split) * trueLen) > 0):
        raise Exception("Error: the potitive elements in the testing dataset for each split should "
                        "contain at least one trace: please re-formulate the tagging!")
    if not (int(training_test_split * falseLen) > 0):
        raise Exception("Error: the negative elements in the training dataset for each split should "
                        "contain at least one trace: please re-formulate the tagging!")
    if not (int((1.0 - training_test_split) * falseLen) > 0):
        raise Exception("Error: the negative elements in the testing dataset for each split should "
                        "contain at least one trace: please re-formulate the tagging!")

    TrainingTest = set()
    TestSet = set()

    # Splitting each class in half, and checking whether the list is not empty
    TTr, TTt = joonas_split_log_train_test(trueTraceOffset, training_test_split)
    if not (len(TTr) > 0):
        raise Exception("Error: the true traces in the training set are empty")
    if not (len(TTt) > 0):
        raise Exception("Error: the true traces in the testing set are empty")
    for id in TTr:
        TrainingTest.add(getId(l[id]))
    for id in TTt:
        TestSet.add(getId(l[id]))

    TTr, TTt = joonas_split_log_train_test(falseTraceOffset, training_test_split)
    if not (len(TTr) > 0):
        raise Exception("Error: the false traces in the training set are empty")
    if not (len(TTt) > 0):
        raise Exception("Error: the false traces in the testing set are empty")
    for id in TTr:
        TrainingTest.add(getId(l[id]))
    for id in TTt:
        TestSet.add(getId(l[id]))

    return TrainingTest, TestSet


def generateFairLogSplit(inp_path, log, log_name, output_folder, slices, training_test_split):
    """
    Dumps the dataset into three different slices, and ensuring that each slice could be a good candidate for
    training and testing

    :param inp_path:                Serialization path, 1°
    :param log:                     Log to be splitted and serialized into different slices
    :param log_name:                Log name, so to append it to the current slice id
    :param output_folder:           Serialization path, 2°
    :param slices:                  Number of slices to be analysed
    :param training_test_split:     Percentage of the training/testing slicing into two, so to check that each
                                    slice will guarantee a good splitting
    :return:
    """

    # Skipping the splitting process if all the files have been already serialized!
    if all(map(lambda log_nr:  os.path.isfile(os.path.join(output_folder, log_name[:-4] + "_" + str(log_nr + 1) + ".xes")), range(slices))):
        return

    traceCount = 0
    trueTraceOffset = []
    falseTraceOffset = []

    ## 1) Splitting the traces in true traces and false traces
    for trace in log:
        traceLabel = str(TraceUtils.getTraceLabel(trace))
        if (traceLabel == "1"):
            trueTraceOffset.append(traceCount)
        elif (traceLabel == "0"):
            falseTraceOffset.append(traceCount)
        else:
            raise Exception("Error: the "+str(traceCount)+"-th trace has a label '"+traceLabel+"', while it should be either 0 or 1")
        traceCount = traceCount + 1

    ## 2) Checking out whether we could have problems in doing a fair split
    if (len(trueTraceOffset)<slices):
        raise Exception("Error: the true traces are, "+str(len(trueTraceOffset))+", while they should be at least in the same number of the slides, "+str(slices))
    if (len(falseTraceOffset)<slices):
        raise Exception("Error: the true traces are, "+str(len(falseTraceOffset))+", while they should be at least in the same number of the slides, "+str(slices))

    ## 3) Shuffling the partition
    shuffle(trueTraceOffset)
    shuffle(falseTraceOffset)
    log_nr = 0

    for trueSplit, falseSplit in zip(numpy.array_split(trueTraceOffset,slices), numpy.array_split(falseTraceOffset,slices)):
        trueLen = float(len(trueSplit))
        falseLen = float(len(falseSplit))
        if not (int(training_test_split * trueLen) > 0):
            raise Exception("Error: the potitive elements in the training dataset for each split should "
                            "contain at least one trace: please re-formulate the tagging!")
        if not (int((1.0-training_test_split) * trueLen) > 0):
            raise Exception("Error: the potitive elements in the testing dataset for each split should "
                            "contain at least one trace: please re-formulate the tagging!")
        if not (int(training_test_split * falseLen) > 0):
            raise Exception("Error: the negative elements in the training dataset for each split should "
                            "contain at least one trace: please re-formulate the tagging!")
        if not (int((1.0-training_test_split) * falseLen) > 0):
            raise Exception("Error: the negative elements in the testing dataset for each split should "
                            "contain at least one trace: please re-formulate the tagging!")
        # After checking that we obtained a good split, dump the datasets

        new_log = XFactory.create_log(log.get_attributes().clone())
        for elem in log.get_extensions():
            new_log.get_extensions().add(elem)
        # new_log.__classifiers = log.get_classifiers().copy()
        new_log.__globalTraceAttributes = log.get_global_trace_attributes().copy()
        new_log.__globalEventAttributes = log.get_global_event_attributes().copy()

        for tId in trueSplit:
            new_log.append(log[tId])
        for fId in falseSplit:
            new_log.append(log[fId])

        with open(os.path.join(output_folder, log_name[:-4] + "_" + str(log_nr + 1) + ".xes"), "w") as file:
            XesXmlSerializer().serialize(new_log, file)

        with open(os.path.join(inp_path, log_name[:-4] + "_" + str(log_nr + 1) + ".xes"), "w") as file:
            XesXmlSerializer().serialize(new_log, file)

        log_nr = log_nr+1
