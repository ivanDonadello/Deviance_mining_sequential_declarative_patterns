import os

import fastcsv
import numpy
import pandas as pd

from . import PandaExpress
from .FileNameUtils import path_generic_log
from .PandaExpress import ensureDataFrameQuality, dataframe_join_withChecks, fast_csv_parse
from scipy.io import arff

def read_single_arff_dump(arff_file, csv_file, doQualityCheck = True):
    arff_pd  = pd.DataFrame(arff.loadarff(os.path.abspath((arff_file)))[0])
    arff_pd.fillna(0, inplace=True)
    arff_pd.rename(columns={"label": "Label"}, inplace=True)
    arff_pd = arff_pd.astype(dtype=pd.SparseDtype("int", 0))
    getOnlyLabels = pd.read_csv((csv_file), sep=";", index_col="Case_ID", na_filter=False, usecols=["Case_ID", "Label"])
    assert (len(arff_pd.index) == len(getOnlyLabels.index))
    assert ("Case_ID" not in arff_pd)
    arff_pd.index = getOnlyLabels.index
    arff_pd["Case_ID"] = getOnlyLabels.index
    if doQualityCheck:
        assert len(dataframe_join_withChecks(arff_pd, getOnlyLabels).index) == len(arff_pd.index)
    arff_pd["Label"] = getOnlyLabels["Label"]
    return arff_pd

def read_arff_embedding_dump(complete_path,  training_ids, testing_ids, doQualityCheck = True):
    arff_training = os.path.join(complete_path, "train_encodings.arff")
    arff_testing = os.path.join(complete_path, "test_encodings.arff")
    csv_training = os.path.join(complete_path, "crosstrain.csv")
    csv_testing = os.path.join(complete_path, "crosstest.csv")

    #Reading the most complete information possible from the arff files
    full_df = pd.concat([ensureDataFrameQuality(read_single_arff_dump(arff_training, csv_training, doQualityCheck)),
                         ensureDataFrameQuality(read_single_arff_dump(arff_testing, csv_testing, doQualityCheck))])

    # These are not the actual training and test set, rather like the one used by weka to learn the embedding!
    # Exploiting the previously mined index ids to get the information
    train_df = full_df[full_df.index.isin(training_ids)]
    test_df = full_df[full_df.index.isin(testing_ids)]
    if doQualityCheck:
        assert (len(train_df.index) == len(training_ids))
        assert (len(test_df.index) == len(testing_ids))
        assert ((len(train_df.index)+len(test_df.index))==len(full_df.index))
    return train_df, test_df




def read_all_numeric_columns_except_one(complete_path):
    print("Reading: "+ complete_path)
    return fast_csv_parse(complete_path)
    #
    # print("Parsing the colnames...")
    # columns = set(pd.read_csv(complete_path, sep=",", na_filter=False, index_col=0, nrows=0).columns.tolist())
    # hasCaseId = "Case_ID" in columns
    # d = dict.fromkeys(columns, numpy.float64)
    # if hasCaseId:
    #     d["Case_ID"] = str
    # print("Reading: "+ complete_path)
    # return ensureLoadedDataQuality(pd.read_csv(complete_path, sep=",", index_col="Case_ID", na_filter=False, dtype=d))

def load_yaml_file(results_folder, split_nr, encoding, dictionary):
    split = "split" + str(split_nr)
    file_loc = os.path.join(results_folder, split, encoding)
    train_path = os.path.join(file_loc, encoding+"_train.csv")
    test_path = os.path.join(file_loc, encoding+"_test.csv")
    dictionary["train"] = os.path.abspath(train_path)
    dictionary["test"] = os.path.abspath(test_path)
    return train_path, test_path

def read_generic_embedding_dump(results_folder, split_nr, encoding, dictionary):
    """
    This method reads the log, that has been already serialized for a vectorial representation

    :param results_folder:  Folder from which we have to read the serialization
    :param split_nr:        Number of current fold for the k-fold
    :param encoding:        Encoding stored in the folder
    :return:
    """
    train_path, test_path = load_yaml_file(results_folder, split_nr, encoding, dictionary)
    train_df = read_all_numeric_columns_except_one(train_path)
    test_df = read_all_numeric_columns_except_one(test_path)
    train_df = train_df.drop(['index'], axis=1, errors='ignore')
    test_df = test_df.drop(['index'], axis=1, errors='ignore')
    return train_df, test_df


def check_dump_exists(results_folder, split_nr, encoding):
    split = "split" + str(split_nr)
    file_loc = os.path.join(results_folder, split, encoding)
    train_path = os.path.join(file_loc, encoding+"_train.csv")
    test_path = os.path.join(file_loc, encoding+"_test.csv")
    return (os.path.isfile(train_path) and os.path.isfile(test_path))


def dump_extended_dataframes(train_df, test_df, results_folder, split_nr, encoding):
    train_path, test_path = path_generic_log(results_folder, split_nr, encoding)
    print("Dumping extended data frames into " + train_path +" and "+test_path)
    not_label = set([col for col in train_df.columns if col != 'Label'])
    new_cols = list(not_label) + ['Label']
    PandaExpress.serialize(train_df[new_cols], train_path)
    PandaExpress.serialize(test_df[list(set.intersection(not_label, test_df.columns)) + ['Label']], test_path)
    return (train_path, test_path)

def dump_custom_dataframes(train_df, test_df, train_path, test_path):
    print("Dumping extended data frames into " + train_path +" and "+test_path)
    not_label = set([col for col in train_df.columns if col != 'Label'])
    new_cols = list(not_label) + ['Label']
    PandaExpress.serialize(train_df[new_cols], train_path)
    PandaExpress.serialize(test_df[list(set.intersection(not_label, test_df.columns)) + ['Label']], test_path)
    return (train_path, test_path)

def multidump_compact(results_folder, elements, forMultiDump,  payload_train_df, payload_test_df, split_nr):
        tr_f, t_f = dump_extended_dataframes(payload_train_df, payload_test_df, results_folder, split_nr,
                                             forMultiDump)
        d = dict()
        d["train"] = os.path.abspath(tr_f)
        d["test"] = os.path.abspath(t_f)
        elements.append(d)

def genericDump(output_path, train_df, test_df, trainFile, testFile):
    doSaveTest = len(test_df.index) > 0
    train_df = PandaExpress.ensureDataFrameQuality(train_df)
    test_df = PandaExpress.ensureDataFrameQuality(test_df)
    PandaExpress.serialize(train_df, os.path.join(output_path, trainFile))
    if doSaveTest:
        PandaExpress.serialize(test_df, os.path.join(output_path, testFile))
    return PandaExpress.ExportDFRowNamesAsSets(test_df, train_df)

def dump_in_primary_memory_as_table_csv(self, strategy, training_df, testing_df, doResetIndex=True):
    if not strategy in self.in_memory_db:
        self.in_memory_db[strategy] = list()
    if doResetIndex:
        self.in_memory_db[strategy].append((ensureDataFrameQuality(training_df).reset_index().set_index("Case_ID", drop=False).sort_index(),
                                            ensureDataFrameQuality(testing_df).reset_index().set_index("Case_ID", drop=False).sort_index()))
    else:
        self.in_memory_db[strategy].append((ensureDataFrameQuality(training_df).sort_index(),
                                            ensureDataFrameQuality(testing_df).sort_index()))