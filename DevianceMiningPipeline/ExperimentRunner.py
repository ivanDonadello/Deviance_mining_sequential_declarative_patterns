"""
Full pipeline for deviance mining experiments

Author: Joonas Puura
"""

import os
import gc
import pdb

import pandas as pd
import numpy as np

import shutil
import yaml

from sklearn.tree import DecisionTreeClassifier
from sklearn.feature_selection import SelectKBest, chi2

from . import baseline_runner, declaredevmining, model
from DevianceMiningPipeline.utils.GoodPrintResults import do_dump_benchmark
from .deviancecommon import read_XES_log
from .sequence_runner import run_sequences, generateSequences
from .ddm_newmethod_fixed_new import declare_data_aware_embedding, fisher_calculation

from sklearn.preprocessing import StandardScaler

## Remove features ...
from skfeature.function.similarity_based import fisher_score
from sklearn.decomposition import PCA
from collections import defaultdict

from .payload_extractor import payload_extractor2, payload_embedding
from .utils import *

from .utils.DumpUtils import read_generic_embedding_dump, multidump_compact, read_arff_embedding_dump, \
    dump_custom_dataframes, dump_extended_dataframes, genericDump, check_dump_exists, load_yaml_file, dump_in_primary_memory_as_table_csv
from .utils.FileNameUtils import csv_trace_encodings
from .utils.PandaExpress import dataframe_multiway_equijoin

dataset_composition = {
    "bs_data": ["baseline", "payload"],
    "baseline_dwd": ["baseline", "dwd"],
    "dc_data": ["declare", "payload"],
    "dc_dwd": ["declare", "dwd"],
    "dc_dwd_payload": ["declare", "payload", "dwd"],
    "hybrid": ["declare", "combined_for_hybrid"],
    "hybrid_data": ["declare", "payload", "combined_for_hybrid"],
    "hybrid_dwd": ["declare", "dwd", "combined_for_hybrid"],
    "hybrid_dwd_payload": ["declare", "dwd", "payload", "combined_for_hybrid"]
}

folder_to_internal = {
    "combined_for_hybrid": "combined_for_hybrid",
    "bs": "baseline",
    "dc": "declare",
    "payload_for_training": "payload",
    "hybrid": "hybrid",
    "bs_data": "bs_data",
    "baseline_dwd": "baseline_dwd",
    "mr": "mr",
    "tr": "tr",
    "mra": "mra",
    "tra": "tra",
    "dc_data": "dc_data",
    "mr_data": "mr_data",
    "mra_data": "mra_data",
    "tr_data": "tr_data",
    "tra_data": "tra_data",
    "dc_dwd": "dc_dwd",
    "dc_dwd_payload": "dc_dwd_payload",
    "hybrid_data": "hybrid_data",
    "hybrid_dwd": "hybrid_dwd",
    "hybrid_dwd_payload": "hybrid_dwd_payload",
    "dwd": "dwd"
}

internal_to_folder = dict()
for k in folder_to_internal:
    internal_to_folder[folder_to_internal[k]] = k

class ExperimentRunner:
    def __init__(self, experiment_name, output_file, results_folder, inp_path, log_name, output_folder, log_template,
                 dt_max_depth=15, dt_min_leaf=None, selection_method="fisher", selection_counts=None,
                 coverage_threshold=None, sequence_threshold=5, payload=False, payload_settings=None,
                 reencode=False, payload_type=None, payload_dwd_settings=None):

        if not payload_type:
            self.payload_type = "normal"
        else:
            self.payload_type = payload_type

        self.payload_dwd_settings = payload_dwd_settings

        self.payload = payload
        self.payload_settings = payload_settings

        self.counter = 0

        self.reencode = reencode

        self.experiment_name = experiment_name
        self.output_file = output_file
        self.results_folder = results_folder
        self.dt_max_depth = dt_max_depth
        self.dt_min_leaf = dt_min_leaf

        self.inp_path = inp_path
        self.log_name = log_name
        self.output_folder = output_folder

        if not os.path.exists(output_folder):
            os.mkdir(output_folder)

        self.log_template = log_template
        self.log_path = os.path.join(self.output_folder, log_template)
        self.log_path_seq = log_template

        self.train_output_file = "train_" + output_file
        self.test_output_file = "test_" + output_file

        if not coverage_threshold and (selection_method == "coverage" or selection_method == "rf_importance"):
            self.coverage_threshold = 20
        else:
            self.coverage_threshold = coverage_threshold

        self.sequence_threshold = sequence_threshold

        self.method = selection_method
        if not selection_counts and selection_method == "fisher":
            self.selection_counts = [100, 500, 1000]
        else:
            self.selection_counts = selection_counts
        self.encodings = ["tr", "tra", "mr", "mra"]

        self.in_memory_db = dict()
        self.yaml_file = {}

    def interpret_results(self, results, model_type, sequence_encoding=None):
            models = defaultdict(dict)
            rules = []

            if model_type == "sequence":
                test_model_eval = model.ModelEvaluation.ModelEvaluation(
                    "TEST Model {} {} with selection {}".format(model_type, sequence_encoding, self.method))
                train_model_eval = model.ModelEvaluation.ModelEvaluation(
                    "TRAIN Model {} {} with selection {}".format(model_type, sequence_encoding, self.method))
            else:
                test_model_eval = model.ModelEvaluation.ModelEvaluation(
                    "TEST Model {} with selection {}".format(model_type, self.method))
                train_model_eval = model.ModelEvaluation.ModelEvaluation(
                    "TRAIN Model {} with selection {} ".format(model_type, self.method))

            for r in results:
                train_model_eval.add_results_dict(r["result"]["train"])
                test_model_eval.add_results_dict(r["result"]["test"])
                rules.append(r["result"]["rules"])

            models["train"] = train_model_eval
            models["test"] = test_model_eval
            models["rules"] = rules

            return models

    @staticmethod
    def create_folder_structure(directory, max_iterations, payload=False, payload_type=None):
        os.makedirs("./output/", exist_ok=True)
        os.makedirs(directory, exist_ok=True)

        # first level
        for i in range(1, max_iterations + 1):
            current_dir = os.path.join(directory, "split" + str(i))
            # os.makedirs(current_dir) --> See documentation: this is completely useless, as it will be created with the first leaf creation

            # second level
            os.makedirs(os.path.join(current_dir, "baseline"), exist_ok=True)
            os.makedirs(os.path.join(current_dir, "declare"), exist_ok=True)
            os.makedirs(os.path.join(current_dir, "mr"), exist_ok=True)
            os.makedirs(os.path.join(current_dir, "mra"), exist_ok=True)
            os.makedirs(os.path.join(current_dir, "tr"), exist_ok=True)
            os.makedirs(os.path.join(current_dir, "tra"), exist_ok=True)
            os.makedirs(os.path.join(current_dir, "combined_for_hybrid"), exist_ok=True)

            if payload:
                if payload_type == "normal" or "both":
                    os.makedirs(os.path.join(current_dir, "payload"), exist_ok=True)
                if payload_type == "dwd" or "both":
                    os.makedirs(os.path.join(current_dir, "dwd"), exist_ok=True)

    @staticmethod
    def cross_validation_pipeline(inp_path, log_name, output_folder, max_splits, training_test_split):  # max_splits = 5
        # Skipping the splitting process if all the files have been already serialized!
        if all(map(lambda log_nr: os.path.isfile(
                os.path.join(output_folder, log_name[:-4] + "_" + str(log_nr + 1) + ".xes")), range(max_splits))):
            return
        else:
            # 1. Load file
            log = read_XES_log(os.path.join(inp_path, log_name))

            # 2. Shuffling & Split into 5 parts for cross validation
            FairLogSplit.generateFairLogSplit(inp_path, log, log_name, output_folder, max_splits, training_test_split)

            del log
            gc.collect()

    @staticmethod
    def correct_read_sequence_log(results_folder, encoding, split_nr, training_ids, testing_ids):  # split_perc = 0.8
        split = "split" + str(split_nr + 1)
        ## TODO: perform fair loading: receive the offsets from the input
        file_loc = os.path.join(results_folder, split, encoding)
        # train_path = file_loc + "/" + "globalLog.csv"
        # global_df = pd.read_csv(train_path, sep=";", index_col="Case_ID", na_filter=False)
        # size_df = len(global_df)
        # train_size = int(split_perc * size_df)
        # train_df = global_df.iloc[:train_size, ]
        # test_df = global_df.iloc[train_size:, ]
        train_df, test_df = read_arff_embedding_dump(file_loc, training_ids, testing_ids)
        return train_df, test_df

    def feature_selection(self, train_df, test_df, y_train, params, payload_train_df=None, payload_test_df=None, ):
        if payload_train_df is not None:
            train_df = pd.concat([train_df, payload_train_df], axis=1)
            test_df = pd.concat([test_df, payload_test_df], axis=1)

        ## Enforcing the fact that we want to perform analyses over numerical type
        ## Still, Joonas produces columns that contains strings, forsooth!
        train_df = train_df.select_dtypes(['number'])
        test_df = test_df.select_dtypes(['number'])
        train_df = train_df.transpose().drop_duplicates().transpose()
        remaining_columns = list(set(train_df.columns).intersection(set(test_df.columns)))
        test_df = test_df[remaining_columns]

        # remove no-variance, constants
        train_df = train_df.loc[:, (train_df != train_df.iloc[0]).any()]
        remaining_columns = list(set(train_df.columns).intersection(set(test_df.columns)))
        test_df = test_df[remaining_columns]
        train_df = train_df[remaining_columns]

        # Turn into np object
        X_train = train_df.values
        X_test = test_df.values
        feature_names = None

        selection_method = self.method

        if selection_method == "PCA":
            # PCA
            standardizer = StandardScaler().fit(X_train)

            # Standardize first
            X_train = standardizer.transform(X_train)
            X_test = standardizer.transform(X_test)

            # Apply PCA
            pca = PCA(n_components=3)

            pca.fit(X_train)
            X_train = pca.transform(X_train)
            X_test = pca.transform(X_test)

            feature_names = None

        elif selection_method == "chi2":

            sel_count = self.selection_counts

            fitt = SelectKBest(chi2, k=min(X_train.shape[1], sel_count)).fit(X_train, y_train)

            X_train = fitt.transform(X_train)
            X_test = fitt.transform(X_test)

            feature_names = train_df.columns[fitt.get_support()]

        elif selection_method == "fisher":
            sel_count = params["selection_count"]
            scores = fisher_calculation(X_train, y_train)
            # scores = fisher_score.fisher_score(X_train, y_train)
            # selected_ranks = fisher_score.feature_ranking(scores)[:sel_count]
            selected_ranks = fisher_score.fisher_score(X_train, y_train, mode='rank')[:sel_count]

            X_train = X_train[:, selected_ranks]
            X_test = X_test[:, selected_ranks]
            for i, rank in enumerate(selected_ranks[:10]):
                print(train_df.columns[rank], scores[i])

            feature_names = train_df.columns[selected_ranks]

        elif selection_method == "coverage":
            # Alternative version
            # commented code is with an old version of skfeature
            # scores = fisher_calculation(X_train, y_train)
            # selected_ranks = fisher_score.feature_ranking(scores)
            selected_ranks = fisher_score.fisher_score(X_train, y_train, mode='rank')

            threshold = self.coverage_threshold

            # Start selecting from selected_ranks until every trace is covered N times
            trace_remaining = dict()
            for i, trace_name in enumerate(train_df.index.values):
                trace_remaining[i] = threshold

            chosen = 0
            # Go from higher to lower
            for rank in selected_ranks:
                if len(trace_remaining) == 0:
                    break
                chosen += 1
                # Get column
                marked_for_deletion = set()
                for k in trace_remaining.keys():
                    if train_df.iloc[k, rank] > 0:

                        trace_remaining[k] -= 1
                        if trace_remaining[k] <= 0:
                            marked_for_deletion.add(k)

                for k in marked_for_deletion:
                    del trace_remaining[k]

            X_train = X_train[:, selected_ranks[:chosen]]
            X_test = X_test[:, selected_ranks[:chosen]]

            feature_names = train_df.columns[selected_ranks[:chosen]]

        return X_train, X_test, feature_names

    def train_and_evaluate_select(self, train_df: pd.DataFrame, test_df: pd.DataFrame,
                                  payload_train_df=None, payload_test_df=None, params=None,
                                  exp_name=None, split_nr=None, dump_to_folder=None) -> (dict, dict):
        """
        Trains and evaluates model
        :param train_df:
        :param test_df:
        :param params:
        :return:
        """

        self.counter += 1
        # Pwoblem (sic!): sometimes, it happens that the Case_Id column is used for training.
        train_df = train_df.drop(['Case_Id'], axis=1, errors='ignore')
        train_df = train_df.drop(['index'], axis=1, errors='ignore')
        test_df = test_df.drop(['Case_Id'], axis=1, errors='ignore')
        test_df = test_df.drop(['index'], axis=1, errors='ignore')

        y_train = train_df.pop('Label').values  # pop: removing the column from the table, while preserving the values
        y_test = test_df.pop('Label').values
        X_train, X_test, feature_names = self.feature_selection(train_df, test_df, y_train, params=params,
                                                                payload_train_df=payload_train_df,
                                                                payload_test_df=payload_test_df)
        if not (dump_to_folder is None):
            assert ((isinstance(dump_to_folder, tuple)) and ((len(dump_to_folder) == 3)))
            X_traincpy = pd.DataFrame(data=X_train, columns=feature_names)
            X_traincpy["Label"] = y_train
            X_testcpy = pd.DataFrame(data=X_test, columns=feature_names)
            X_testcpy["Label"] = y_test
            dump_extended_dataframes(X_traincpy, X_testcpy, dump_to_folder[0], dump_to_folder[1], dump_to_folder[2])

        # Train classifier
        clf = DecisionTreeClassifier(max_depth=self.dt_max_depth)  # , min_samples_leaf=self.dt_min_leaf)
        if (np.isnan(y_train).any()) or (np.isnan(X_train).any()) or (np.isnan(y_test).any()) or (
        np.isnan(X_test).any()):
            nanYtrain = ~np.isnan(y_train)
            X_train = X_train[nanYtrain]
            y_train = y_train[nanYtrain]
            X_train[np.isnan(X_train)] = -1

            nanYtest = ~np.isnan(y_test)
            X_test = X_test[nanYtest]
            y_test = y_test[nanYtest]
            X_test[np.isnan(X_test)] = -1
        clf.fit(X_train, y_train, check_input=False)

        # Evaluate model
        train_results, test_results = ModelUtils.evaluate_dt_model(clf, X_train, y_train, X_test, y_test)
        rules = ModelUtils.export_text2(clf, feature_names.to_list())

        return train_results, test_results, rules

    def train(self, train_df, test_df, split_nr=None, exp_name=None):
        if self.method == "fisher":
            selection_counts = self.selection_counts
            results = []
            # Trying all selection counts
            for selection_count in selection_counts:
                train_results, test_results, rules = self.train_and_evaluate_select(train_df.copy(), test_df.copy(),
                                                                                    params={
                                                                                        "selection_count": selection_count})
                result = {
                    "train": train_results,
                    "test": test_results,
                    "selection_count": selection_count,
                    "rules": rules
                }
                results.append(result)

            return results
        else:
            train_results, test_results, rules = self.train_and_evaluate_select(train_df.copy(),
                                                                                test_df.copy(),
                                                                                split_nr=split_nr, exp_name=exp_name)
            result = {
                "train": train_results,
                "test": test_results,
                "rules": rules
            }

            return result

    # def abstract_train(self, str_key, yamlfile, dataset, max_range):
    #     results = []
    #     elements = []
    #     for split_nr in range(1, max_range + 1):
    #         d = dict()
    #         train_df, test_df = read_generic_embedding_dump(self.results_folder, split_nr, dataset, d)
    #         elements.append(d)
    #         tr_result = self.train(train_df, test_df, split_nr=split_nr, exp_name=dataset)
    #
    #         result = {
    #             "result": tr_result,
    #             "split": split_nr
    #         }
    #         results.append(result)
    #
    #     assert (not (str_key in yamlfile))
    #     yamlfile[str_key] = elements
    #     return results

    def abstract_train2(self, str_key, dataset, max_range):

        if (not (str_key in self.in_memory_db.keys())) or (not (str_key in self.yaml_file.keys())):
            #assert str_key in self.in_memory_db.keys()
            self.load_data(str_key, dataset, max_range)
        assert not ((not (str_key in self.in_memory_db.keys())) or (not (str_key in self.yaml_file.keys())))
        split_nr = 1
        results = []
        for train_df, test_df in self.in_memory_db[str_key]:
            tr_result = self.train(train_df, test_df, split_nr=split_nr, exp_name=dataset)
            result = {
                "result": tr_result,
                "split": split_nr
            }
            results.append(result)
            split_nr = split_nr + 1

        #assert (not (str_key in self.yaml_file))
        return results

    def load_data(self, str_key, dataset, max_range):
        training = []
        testing = []
        elements = []
        doLoad = not (str_key in self.in_memory_db.keys())
        requiresYaml = not (str_key in self.yaml_file.keys())

        #assert not doLoad
        if not all([check_dump_exists(self.results_folder, split_nr, dataset) for split_nr in range(1, max_range + 1)]):
            raise Exception("Error: database '" + str_key + "' was not loaded, and therefore cannot be loaded. We "
                                                           "suggest you to re-run the pipeline")

        for split_nr in range(1, max_range + 1):
            d = dict()
            if requiresYaml:
                load_yaml_file(self.results_folder, split_nr, dataset, d)
                elements.append(d)
            if doLoad:
                train_df, test_df = read_generic_embedding_dump(self.results_folder, split_nr, dataset, d)
                training.append(train_df)
                testing.append(test_df)
        if doLoad:
            self.in_memory_db[str_key] = list(zip(training, testing))
        if requiresYaml:
            self.yaml_file[str_key] = elements

    def multijoined_dump(self, str_key, dataset_list, max_range, storeInMemory = False):
        training = []
        testing = []
        doAdd = storeInMemory or str_key in self.yaml_file.keys()
        for split_nr in range(1, max_range + 1):
            trainls = []
            testls = []
            for dataset1 in dataset_list:
                cmp = internal_to_folder[dataset1]
                train1_df = None
                test1_df = None
                if cmp in self.in_memory_db:
                    train1_df, test1_df = self.in_memory_db[cmp][split_nr-1]
                else:
                    train1_df, test1_df = read_generic_embedding_dump(self.results_folder, split_nr, dataset1, dict())
                trainls.append(train1_df)
                testls.append(test1_df)
            train_df = PandaExpress.dataframe_multiway_equijoin(trainls)
            test_df = PandaExpress.dataframe_multiway_equijoin(testls)
            if doAdd:
                training.append(train_df)
                testing.append(test_df)
            multidump_compact(self.results_folder, [], str_key, train_df, test_df, split_nr)
        if doAdd:
            self.in_memory_db[str_key] = list(zip(training, testing))

    # def load_data(self, max_range):
    #     self.load_data("bs", "baseline", max_range)
    #     self.load_data("dc", "declare", max_range)
    #     self.load_data("payload_for_training", "payload", max_range)
    #     self.load_data("hybrid", "hybrid", max_range)
    #     self.load_data("bs_data", "bs_data", max_range)
    #     self.load_data("baseline_dwd", "baseline_dwd", max_range)
    #     for encoding in self.encodings:
    #         key = encoding+"_data"
    #         self.load_data(key, key, max_range)
    #     self.load_data("dc_data", "dc_data", max_range)
    #     self.load_data("dc_dwd", "dc_dwd", max_range)
    #     self.load_data("dc_dwd_payload", "dc_dwd_payload", max_range)
    #     self.load_data("hybrid_data", "hybrid_data", max_range)
    #     self.load_data("hybrid_dwd", "hybrid_dwd", max_range)
    #     self.load_data("hybrid_dwd_payload", "hybrid_dwd_payload", max_range)

    def baseline_train(self, max_range):
        return self.abstract_train2("bs", "baseline", max_range)

    def declare_train(self, max_range):
        return self.abstract_train2("dc", "declare", max_range)

    def payload_train(self, max_range):
        return self.abstract_train2("payload_for_training", "payload", max_range)

    def hybrid_train(self, max_range):
        #combined_for_hybrid
        return self.abstract_train2("hybrid", "hybrid", max_range)

    def baseline_train_with_data(self, max_range):
        return self.abstract_train2("bs_data", "bs_data", max_range)

    def baseline_train_with_dwd(self, max_range):
        return self.abstract_train2("baseline_dwd", "baseline_dwd", max_range)

    def sequence_train_with_data(self, encoding, max_range):
        key = encoding + "_data"
        return self.abstract_train2(key, key, max_range)

    def declare_train_with_data(self, max_range):
        return self.abstract_train2("dc_data", "dc_data", max_range)

    def declare_train_with_dwd(self, max_range: object) -> object:
        return self.abstract_train2("dc_dwd", "dc_dwd", max_range)

    def declare_train_with_dwd_data(self, max_range):
        return self.abstract_train2("dc_dwd_payload", "dc_dwd_payload", max_range)

    def hybrid_with_data(self, max_range):
        return self.abstract_train2("hybrid_data", "hybrid_data", max_range)

    def hybrid_with_dwd(self, max_range):
        return self.abstract_train2("hybrid_dwd", "hybrid_dwd", max_range)

    def hybrid_with_dwd_and_payload(self, max_range):
        return self.abstract_train2("hybrid_dwd_payload", "hybrid_dwd_payload", max_range)

    def train_and_eval_benchmark(self, max_splits):
        all_results = {}
        #
        print("Started working on baseline.")
        baseline_results = self.baseline_train(max_splits)
        all_results["bs"] = self.interpret_results(baseline_results, "baseline")

        print("Started working on declare.")
        declare_results = self.declare_train(max_splits)
        all_results["dc"] = self.interpret_results(declare_results, "declare")

        print("Started working on sequenceMR.")
        sequence_results = self.abstract_train2("mr", "mr", max_splits)
        all_results["mr"] = self.interpret_results(sequence_results, "sequence", "mr")
        #
        print("Started working on sequenceTR.")
        sequence_results = self.abstract_train2("tr", "tr", max_splits)
        all_results["tr"] = self.interpret_results(sequence_results, "sequence", "tr")
        #
        print("Started working on sequenceTRA.")
        sequence_results = self.abstract_train2("tra", "tra", max_splits)
        all_results["tra"] = self.interpret_results(sequence_results, "sequence", "tra")
        #
        print("Started working on sequenceMRA.")
        sequence_results = self.abstract_train2("mra", "mra",  max_splits)
        all_results["mra"] = self.interpret_results(sequence_results, "sequence", "mra")
        #
        print("Started working on hybrid.")
        hybrid_results = self.hybrid_train(max_splits)
        all_results["hybrid"] = self.interpret_results(hybrid_results, "hybrid")
        #
        if self.payload:
            print("Started working on payload train.")
            payload_results = self.payload_train(max_splits)  # self.payload_train("bs", yaml_file)
            all_results["payload"] = self.interpret_results(payload_results, "payload")
        #
            print("Started working on baseline with data.")
            baseline_results = self.baseline_train_with_data(max_splits)
            all_results["bs_data"] = self.interpret_results(baseline_results, "baseline")
        #
            print("Started working on declare with data.")
            declare_results = self.declare_train_with_data(max_splits)
            all_results["dc_data"] = self.interpret_results(declare_results, "declare")
        #
            print("Started working on sequenceMR with data.")
            sequence_results = self.sequence_train_with_data("mr", max_splits)
            all_results["mr_data"] = self.interpret_results(sequence_results, "sequence", "mr")
        #
            print("Started working on sequenceTR with data.")
            sequence_results = self.sequence_train_with_data("tr", max_splits)
            all_results["tr_data"] = self.interpret_results(sequence_results, "sequence", "tr")
        #
            print("Started working on sequenceTRA with data.")
            sequence_results = self.sequence_train_with_data("tra", max_splits)
            all_results["tra_data"] = self.interpret_results(sequence_results, "sequence", "tra")
        #
            print("Started working on sequenceMRA with data.")
            sequence_results = self.sequence_train_with_data("mra", max_splits)
            all_results["mra_data"] = self.interpret_results(sequence_results, "sequence", "mra")
        #
            print("Started working on hybrid with data.")
            payload_results = self.hybrid_with_data(max_splits)
            all_results["hybrid_data"] = self.interpret_results(payload_results, "hybrid_data")
        #
            if self.payload_type == "both":
                print("Started working on declare with dwd.")
                declare_results = self.declare_train_with_dwd(max_splits)
                all_results["dc_dwd"] = self.interpret_results(declare_results, "declare_dwd")
        #
                print("Started working on declare with dwd and payload.")
                declare_results = self.declare_train_with_dwd_data(max_splits)
                all_results["dc_dwd_payload"] = self.interpret_results(declare_results, "declare_payload_dwd")
        #
                print("Started working on hybrid with dwd.")
                payload_results = self.hybrid_with_dwd(max_splits)
                all_results["hybrid_dwd"] = self.interpret_results(payload_results, "hybrid_dwd")
        #
                print("Started working on hybrid with dwd and usual payload.")
                payload_results = self.hybrid_with_dwd_and_payload(max_splits)
                all_results["hybrid_dwd_payload"] = self.interpret_results(payload_results, "hybrid_data_dwd")

        weka_yaml_file = os.path.join(self.results_folder, "for_weka_experiments.yaml")
        if not (os.path.exists(weka_yaml_file)):
            print("Writing the yaml file:")
            with open(weka_yaml_file, 'w') as file:
                yaml.dump(self.yaml_file, file)

        do_dump_benchmark(all_results, self.results_folder, self.dt_max_depth, self.experiment_name)

    def prepare_cross_validation(self, max_splits, training_test_split):  # max_splits = 5
        self.cross_validation_pipeline(self.inp_path, self.log_name, self.output_folder, max_splits,
                                       training_test_split)

    def prepare_data(self, max_splits, training_test_split, missing_literal, doForce=False, threshold_split = 0.1):
        self.create_folder_structure(self.results_folder, max_splits, payload=self.payload,
                                     payload_type=self.payload_type)
        isTrue = True
        ignored = []
        if self.payload_dwd_settings is not None:
            ignored = self.payload_dwd_settings["ignored"]
        TrL_TeL_pair_list = list()

        print("New code by Giacomo Bergami, for evenly splitting and storing the database")
        for i in range(max_splits):
            print("Current run: " + str(i))
            baseline_path = FileNameUtils.baseline_path(i, self.results_folder)
            declare__path = FileNameUtils.declare_path(i, self.results_folder)
            payload__path = FileNameUtils.payload_path(i, self.results_folder)
            declared_data_path = FileNameUtils.declare_data_aware_path(i, self.results_folder)

            print("\t - reading the log")
            log = read_XES_log(FileNameUtils.getXesName(self.log_path, i))
            TrainingId, TestingId = FairLogSplit.abstractFairSplit(log,
                                                                   TraceUtils.isTraceLabelPositive,
                                                                   TraceUtils.getTraceId,
                                                                   training_test_split)
            TrL_TeL_pair_list.append([list(TrainingId), list(TestingId)])

            print("\t * obtaining the canonical XES representation")
            logTraining, logTesting = LogUtils.xes_to_tracelist_split(log, TrainingId, TestingId)

            print("\t * obtaining the splitted propositional representation")
            propositionalTraining, propositionalTesting = \
                LogUtils.xes_to_propositional_split(log, TrainingId, TestingId)

            print("\t * obtaining the data propositional representation")
            dataPropositionalTraining, dataPropositionalTesting = \
                LogUtils.xes_to_data_propositional_split(log, TrainingId, TestingId, doForce)
            #"""
            print("\t - writing baseline split")
            STr, STt = baseline_runner.baseline_embedding(baseline_path, propositionalTraining, propositionalTesting, None)
            assert (STr == TrainingId)
            assert (STt == TestingId)

            print("\t - writing declare split")
            STr, STt = declaredevmining.declare_embedding(declare__path, propositionalTraining, propositionalTesting, self,
                                                          reencode=self.reencode, candidate_threshold=threshold_split,
                                                          constraint_threshold=threshold_split)
            assert (STr == TrainingId)
            assert (STt == TestingId)
            #
            if self.payload:
                if self.payload_type == "normal" or self.payload_type == "both":
                    print("\t - writing payload embedding")
                    STr, STt = payload_embedding(payload__path, self.payload_settings, logTraining, logTesting, None)
                    assert (STr == TrainingId)
                    assert (STt == TestingId)
                if self.payload_type == "dwd" or self.payload_type == "both":
                    print("\t - writing declare with data embedding")
                    STr, STt = declare_data_aware_embedding(ignored, declared_data_path, dataPropositionalTraining,
                                                            dataPropositionalTesting, missing_literal, self, candidate_threshold=threshold_split,
                                                          constraint_threshold=threshold_split)
                    assert (STr == TrainingId)
                    assert (STt == TestingId)
            del STr
            del STt
            del TrainingId
            del TestingId
            del logTraining
            del logTesting
            gc.collect()
        #"""
        print("~~ Run sequence miner for all the params")
        #pdb.set_trace()
        strategies = run_sequences(self.inp_path, self.log_path_seq, self.results_folder, self.err_logger, max_splits,
                                   sequence_threshold=self.sequence_threshold)
        print("~~ Providing the correct CSV dump for the sequence miner")
        #
        for i in range(max_splits):
            hybrid___path = FileNameUtils.hybrid_path(i, self.results_folder)
            allTr = []
            allTe = []
            TrainingId, TestingId = TrL_TeL_pair_list[i]
            for strategy in strategies:
                #pdb.set_trace()
                training_df, testing_df = ExperimentRunner.correct_read_sequence_log(self.results_folder, strategy, i,
                                                                                     TrainingId, TestingId)
                allTr.append(training_df)
                allTe.append(testing_df)
                d = csv_trace_encodings(self.results_folder, strategy, i + 1)
                dump_custom_dataframes(training_df, testing_df, d["train"], d["test"])
        #
                dump_in_primary_memory_as_table_csv(self, strategy, training_df, testing_df, False)
        #
            allTr = dataframe_multiway_equijoin(allTr)
            allTe = dataframe_multiway_equijoin(allTe)
        #
            dump_in_primary_memory_as_table_csv(self, "combined_for_hybrid", allTr, allTe, False)
            genericDump(hybrid___path, allTr, allTe, "combined_for_hybrid_train.csv", "combined_for_hybrid_test.csv")
        #
            del allTr
            del allTe
            gc.collect()
        #
        print("\t - writing bs_data")
        self.multijoined_dump("bs_data", ["baseline", "payload"], max_splits)
        #
        print("\t - writing baseline_dwd")
        self.multijoined_dump("baseline_dwd", ["baseline", "dwd"], max_splits, isTrue)
        #
        print("\t - writing dc_data")
        self.multijoined_dump("dc_data", ["declare", "payload"], max_splits, isTrue)
        #
        print("\t - writing dc_dwd")
        self.multijoined_dump("dc_dwd", ["declare", "dwd"], max_splits, isTrue)
        #
        print("\t - writing dc_dwd_payload")
        self.multijoined_dump("dc_dwd_payload", ["declare", "payload", "dwd"], max_splits, isTrue)
        #
        for strategy in strategies:
            print("\t - writing " + strategy + "_data")
            self.multijoined_dump(strategy + "_data", [strategy, "payload"], max_splits)
        #
        print("\t - writing hybrid")
        self.multijoined_dump("hybrid", ["declare", "combined_for_hybrid"], max_splits, isTrue)
        #
        print("\t - writing hybrid_data")
        self.multijoined_dump("hybrid_data", ["declare", "payload", "combined_for_hybrid"], max_splits, isTrue)
        #
        print("\t - writing hybrid_dwd")
        self.multijoined_dump("hybrid_dwd", ["declare", "dwd", "combined_for_hybrid"], max_splits, isTrue)
        #
        print("\t - writing hybrid_dwd_payload")
        self.multijoined_dump("hybrid_dwd_payload", ["declare", "dwd", "payload", "combined_for_hybrid"], max_splits, isTrue)

    def clean_data(self):
        shutil.rmtree(self.results_folder)
