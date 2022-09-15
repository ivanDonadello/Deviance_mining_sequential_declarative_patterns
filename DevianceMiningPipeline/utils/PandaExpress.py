"""
Generating one single file for all the Pandas utils

@author: Giacomo Bergami
"""
import os
from functools import reduce

import fastcsv
import numpy
import pandas as pd

from DevianceMiningPipeline.utils.FileNameUtils import path_generic_log


def ensureDataFrameQuality(df):
    assert ('Case_ID' in df.columns)
    assert ('Label' in df.columns)
    df['Label'] = df['Label'].astype(int)  #Ensuring that the labels are in the numeric format, and not as characters!
    #also, this type cannot be sparse
    return df.sort_index()
    # rownames = df["Case_ID"]
    # df.index = rownames
    # df_numerics_only = df.select_dtypes(include=numpy.number)   # Removing string information: it won't be passed to the classifier!
    # df_numerics_only["Case_ID"] = rownames
    # return df_numerics_only

def ensureLoadedDataQuality(df):
    #cols = list(filter(lambda c : not (c == "Case_ID") , df.columns))
    #df[cols] = df[cols].apply(pd.to_numeric, axis=1)
    if "Case_ID" not in df.columns:
        df["Case_ID"] = df.index
    assert ('Label' in df.columns)
    return df.sort_index()

def fast_csv_serializer(df,path):
    df = ensureDataFrameQuality(df)
    l = list(df.select_dtypes(include=numpy.number).columns.tolist())
    if  "Label" not in l:
        l.append("Label")
    l.append("Case_ID")
    df = df[l]
    if not df.empty:
        with open(path,"w") as file:
            writer = fastcsv.Writer(file)
            writer.writerow(list(df.columns))
            for _, row in df.iterrows():
                writer.writerow(list(row))
            writer.flush()
            file.close()


def serialize(df, path, index = False):
    fast_csv_serializer(df, path)
    # df = ensureDataFrameQuality(df)
    # if not df.empty:
    #     assert isinstance(df, pd.DataFrame)
    #     df.to_csv(path, index=index)

def ExportDFRowNamesAsSets(test_df, train_df):
    return set(train_df["Case_ID"].to_list()), set(test_df["Case_ID"].to_list())

def ExportDFRowNamesAsLists(test_df, train_df):
    return list(train_df["Case_ID"].to_list()), list(test_df["Case_ID"].to_list())

def extendDataFrameWithLabels(df, map_rowid_to_label):
    assert ('Case_ID' in df.columns)
    assert ('Label' not in df.columns)
    ls = list()
    for trace_id in df["Case_ID"]:
        ls.append(map_rowid_to_label[trace_id])
    df["Label"] = ls
    return df


def fast_csv_parse(complete_path):
    """
    Using a non-standard library (C/C++ based) to parse the file efficiently. DataFrames from Pandas are a complete
    waste of time...

    :param complete_path:
    :return:
    """
    idx = []
    row_list = []
    with open(complete_path) as file:
        firstLine = True
        colNames = []
        cols = {}
        index = 1
        for line in fastcsv.Reader(file):
            index = index+1
            if firstLine:
                colNames = line
                firstLine = False
            else:
                row = {}
                for (key,value) in zip(colNames, line):
                    if not (key == "Case_ID"):
                        if len(value) == 0: #Sometimes, a nan is just an empty string
                            value = 0.0
                        else:
                            value = float(value)
                    else:
                        idx.append(value)
                    if (key == "Label"):
                        assert (value == 0.0) or (value == 1.0)
                    row[key] = value
                row_list.append(row)
    if len(idx) == 0:
        idx = None
    return pd.DataFrame(row_list, index=idx)

def dataframe_join_withChecks(left, right):
    j = None
    idTest = ('Case_ID' in left.columns) and ('Case_ID' in right.columns)
    j = left.join(right, lsuffix='_left', rsuffix='_right')
    if idTest:
        assert ((list(map(lambda x: str(x), j["Case_ID_right"].to_list())) == list(map(lambda x: str(x), j["Case_ID_left"].to_list())))) #
        assert ((list(map(lambda x: str(x), j["Case_ID_right"].to_list())) == list(map(lambda x: str(x), j.index))))
    assert ((list(map(lambda x: int(x), j["Label_right"].to_list())) == list(map(lambda x: int(x), j["Label_left"].to_list()))))
    assert ('Label_left' in j)
    assert ('Label_right' in j)
    j.drop("Label_left", axis=1, inplace=True)
    if idTest:
        assert (('Case_ID_left' in j) and ('Case_ID_right' in j))
        j.drop("Case_ID_left", axis=1, inplace=True)
        j.rename(columns={'Label_right': 'Label', 'Case_ID_right': 'Case_ID'}, inplace=True)
    else:
        assert ('Case_ID' in j)
    return j

def dataframe_multiway_equijoin(ls):
    return reduce(dataframe_join_withChecks, ls)

