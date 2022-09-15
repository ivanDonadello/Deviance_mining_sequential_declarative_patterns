"""
Utility Names for the files as strings

@author: Giacomo Bergami
"""
import os
from pathlib import Path


def getXesName(log_path, logNr):
    return log_path.format(logNr + 1)


def embedding_path(logNr, results_folder, strategyName):
    return os.path.join(results_folder, "split" + str(logNr + 1), strategyName)


def baseline_path(logNr, results_folder):
    return embedding_path(logNr, results_folder, "baseline")


def declare_path(logNr, results_folder):
    return embedding_path(logNr, results_folder, "declare")


def declare_data_aware_path(logNr, results_folder):
    return embedding_path(logNr, results_folder, "dwd")


def hybrid_path(logNr, results_folder):
    return embedding_path(logNr, results_folder, "combined_for_hybrid")


def payload_path(logNr, results_folder):
    return embedding_path(logNr, results_folder, "payload")


def arff_trace_encodings(results_folder, encoding, split_nr):
    split = "split" + str(split_nr)
    file_loc = results_folder + "/" + split + "/" + encoding
    train_path = file_loc + "/" + "train_encodings.arff"
    test_path = file_loc + "/" + "test_encodings.arff"
    return {"train": os.path.abspath(train_path), "test": os.path.abspath(test_path)}


def csv_trace_encodings(results_folder, encoding, split_nr):
    split = "split" + str(split_nr)
    file_loc = os.path.join(results_folder, split, encoding)
    train_path = os.path.join(file_loc, encoding + "_train.csv")
    test_path = os.path.join(file_loc, encoding + "_test.csv")
    return {"train": os.path.abspath(train_path), "test": os.path.abspath(test_path)}


def extract_file_name_for_dump(results_folder, elements, key, split_nr):
    d = dict()
    tr_f, t_f = path_generic_log(results_folder, split_nr, key)
    d["train"] = os.path.abspath(tr_f)
    d["test"] = os.path.abspath(t_f)
    elements.append(d)


def path_generic_log(results_folder, split_nr, encoding):
    split = "split" + str(split_nr)
    file_loc = os.path.join(results_folder, split, encoding)
    Path(file_loc).mkdir(parents=True, exist_ok=True)
    train_path = os.path.join(file_loc, encoding + "_train.csv")
    test_path = os.path.join(file_loc, encoding + "_test.csv")
    return (train_path, test_path)
