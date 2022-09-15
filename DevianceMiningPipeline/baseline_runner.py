"""
Code to find and encode IA encoding (Individual Activities) or baseline

"""
from .deviancecommon import read_XES_log, xes_to_positional, extract_unique_events_transformed
import numpy as np
from .declaredevmining import split_log_train_test
import pandas as pd
from DevianceMiningPipeline.utils.PathUtils import *
from .utils import PandaExpress
from .utils.DumpUtils import genericDump, dump_in_primary_memory_as_table_csv


def transform_log(train_log, activity_set):
    train_names = []

    train_labels = []
    train_data = []
    for trace in train_log:
        name = trace["name"]
        label = trace["label"]
        res = []
        train_labels.append(label)
        train_names.append(name)
        for event in activity_set:
            if event in trace["events"]:
                res.append(len(trace["events"][event]))
            else:
                res.append(0)

        train_data.append(res)

    np_train_data = np.array(train_data)
    train_df = pd.DataFrame(np_train_data)
    train_df.columns = activity_set
    train_df["Case_ID"] = train_names
    train_df["Label"] = train_labels
    train_df.set_index("Case_ID")
    return train_df

#
# def baseline(inp_folder, logPath, splitSize, self):
#     log = read_XES_log(logPath)
#     transformed_log = xes_to_positional(log)
#     train_log, test_log = split_log_train_test(transformed_log, splitSize)
#
#     # Collect all different IA's
#     return baseline_embedding(inp_folder, train_log, test_log, self)

def baseline_embedding(inp_folder, train_log, test_log, self = None):
    activitySet = list(extract_unique_events_transformed(train_log))
    # Transform to matrix
    # train data
    if len(train_log) > 0:
        print("Train data")
        train_df = transform_log(train_log, activitySet)
    else:
        train_df = pd.DataFrame()
    # test data
    if len(test_log) > 0:
        print("Test data")
        test_df = transform_log(test_log, activitySet)
    else:
        test_df = pd.DataFrame()
    mkdir_test(inp_folder)

    ## Sorting the dataframes by rowname, so to guarantee that the dataframes match by row id!

    j= genericDump(inp_folder, train_df, test_df, "baseline_train.csv", "baseline_test.csv")
    if self is not None:
        dump_in_primary_memory_as_table_csv(self, "bs", train_df, test_df)
    return j




