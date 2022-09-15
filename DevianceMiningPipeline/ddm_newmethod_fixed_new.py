"""
Last version for data-aware declare mining
"""
import pdb

from .declaretemplates_data import *
from .deviancecommon import read_XES_log, xes_to_data_positional
from .declaredevmining import split_log_train_test, extract_unique_events_transformed
from .declaredevmining import filter_candidates_by_support, count_classes

from skfeature.function.similarity_based import fisher_score
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.tree import DecisionTreeClassifier, export_graphviz




import numpy as np
import pandas as pd

import os
from .utils import PandaExpress
from .utils.DumpUtils import genericDump, dump_in_primary_memory_as_table_csv
from .utils.PandaExpress import extendDataFrameWithLabels
from .utils.TraceUtils import trace_to_label_map, propositionalized_trace_to_label_map


def fisher_calculation(X, y):
    """
    https://papers.nips.cc/paper/2909-laplacian-score-for-feature-selection.pdf
    :param data:
    :return:
    """

    #print(X[0,:])
    # Find mean and variance for full dataset

    #for i in range(X.shape[1]):
    #    print(X[:,i].dtype)
    feature_mean = np.mean(X, axis=0)
    #feature_var = np.var(X, axis=0)

    # Find variance for each class, maybe do normalization as well??
    # ID's for
    n_positive = (y == 1).sum()
    n_negative = (y == 0).sum()

    # Split positive and neg samples
    pos_samples = X[y == 1]
    neg_samples = X[y == 0]

    # get variance and mean for positive and negative labels for all features
    pos_variances = np.var(pos_samples, axis=0)
    neg_variances = np.var(neg_samples, axis=0)

    # get means
    pos_means = np.mean(pos_samples, axis=0)
    neg_means = np.mean(neg_samples, axis=0)

    #print(pos_variances)
    #print(neg_variances)

    # Calculate Fisher score for each feature
    Fr = np.zeros(X.shape[1])

    for i in range(X.shape[1]):
        Fr[i] = n_positive * np.power(pos_means[i] - feature_mean[i], 2) + \
                n_negative * np.power(neg_means[i] - feature_mean[i], 2)
        denom = (n_positive * pos_variances[i] + n_negative * neg_variances[i])
        if (denom == 0):
            Fr[i] = 0
        else:
            Fr[i] /= (n_positive * pos_variances[i] + n_negative * neg_variances[i])
    return Fr


def transform_results_to_numpy(results, train_log):
    """
    Transforms results structure into numpy arrays
    :param results:
    :param train_log:
    :return:
    """
    labels = [trace["label"] for trace in train_log]
    trace_names = [trace["name"] for trace in train_log]
    matrix = []
    featurenames = []

    for feature, result in results.items():
        matrix.append(result)
        featurenames.append(feature)

    nparray_data = np.array(matrix).T
    nparray_labels = np.array(labels)
    nparray_names = np.array(trace_names)
    return nparray_data, nparray_labels, featurenames, nparray_names


def find_if_satisfied_by_class(constraint_result, log, support_norm, support_dev):
    fulfill_norm = 0
    fulfill_dev = 0
    for i, trace in enumerate(log):
        ## TODO: Find if it is better to have > 0 or != 0.
        if constraint_result[i] > 0:
        #if constraint_result[i] != 0:
            if trace["label"] == 1:
                fulfill_dev += 1
            else:
                fulfill_norm += 1

    norm_pass = fulfill_norm >= support_norm
    dev_pass = fulfill_dev >= support_dev

    return norm_pass, dev_pass


def apply_template_to_log(template, candidate, log):
    results = []
    for trace in log:
        result, vacuity = apply_template(template, trace, candidate)
        results.append(result)
    return results


def apply_data_template_to_log(template, candidate, log):
    results = []
    for trace in log:
        results.append(apply_data_template2(template, trace, candidate))
    return results


def apply_data_template_to_log2(template, candidate, log):
    return map(lambda trace: apply_data_template(template, trace, candidate), log)

def generate_train_candidate_constraints(candidates, templates, train_log, constraint_support_norm,
                                         constraint_support_dev, filter_t=True):
    all_results = {}
    for template in templates:
        print("Started working on {}".format(template))
        for candidate in candidates:
            if len(candidate) == template_sizes[template]:
                constraint_result = apply_template_to_log(template, candidate, train_log)
                satis_normal, satis_deviant = find_if_satisfied_by_class(constraint_result, train_log,
                                                                         constraint_support_norm,
                                                                         constraint_support_dev)
                if not filter_t or (satis_normal or satis_deviant):
                    all_results[(template, candidate)] = constraint_result
    return all_results


def generate_test_candidate_constraints(candidates, templates, test_log, train_results):
    all_results = {}
    for template in templates:
        print("Started working on {}".format(template))
        for candidate in candidates:
            if len(candidate) == template_sizes[template]:
                if (template, candidate) in train_results:
                    constraint_result = apply_template_to_log(template, candidate, test_log)
                    all_results[(template, candidate)] = constraint_result
    return all_results



def find_fulfillments_violations(candidate, template, log):
    """
    For each trace in positional log give fulfilled and violated positions
    :param candidate:
    :param template:
    :param log:
    :return:
    """
    outp = apply_data_template_to_log(template, candidate, log)
    return outp




def get_data_snapshots(trace, fulfilled, violated):
    positive_snapshots = []
    negative_snapshots = []

    pos_locs = set(fulfilled)
    neg_locs = set(violated)

    current_snap = {}
    for i, event_data in enumerate(trace["data"]):
        for k, val in event_data.items():
            current_snap[k] = val

        if i in pos_locs:
            positive_snapshots.append(dict(current_snap))
        elif i in neg_locs:
            negative_snapshots.append(dict(current_snap))


    return positive_snapshots, negative_snapshots



class DRC:

    def init_d_dictionary(self, d, features, id_label, label_label):
        d[id_label] = list()
        d[label_label] = list()
        for feature in features:
            d[feature] = list()
        return d

    def create_sample2(self, d, samples, features, label, id_label, label_label):
        #features_data = []
        for smp_id, pos_act in samples:
            #act_features = []
            d[id_label].append(smp_id)
            d[label_label].append(label)
            #act_features.append(smp_id)
            for feature in features:
                ft_type = feature[1]
                if feature in pos_act:
                    ft_val = pos_act[feature]
                    if ft_type == "boolean":
                        if ft_val == "true":
                            d[feature].append(1)
                        else:
                            d[feature].append(0)
                    elif ft_type == "literal":
                        d[feature].append(ft_val)
                    elif ft_type == "continuous":
                        d[feature].append(float(ft_val))
                    elif ft_type == "discrete":
                        d[feature].append(int(ft_val))
                    else:
                        print("SHOULDNT BE HERE!")
                        raise Exception("Incorrect feature type in creation of samples")
                else:
                    if ft_type == "boolean":
                        d[feature].append(0)
                    elif ft_type == "literal":
                        d[feature].append("Missing")
                    elif ft_type == "continuous":
                        d[feature].append(0.0)
                    elif ft_type == "discrete":
                        d[feature].append(0)
                    else:
                        print("SHOULDNT BE HERE!")
                        raise Exception("Incorrect feature type in creation of samples")
            #act_features.append(label)
            #features_data.append(act_features)
        return d

    def finalize_map(self, d, features, missing_literal):
        for feature in features:
            ft_type = feature[1]
            if ft_type == "boolean":
                d[feature] = pd.array(d[feature], dtype=pd.SparseDtype("int", 0))
            elif missing_literal is not None and ft_type == "literal":
                d[feature] = pd.array(d[feature], dtype=pd.SparseDtype("str", missing_literal))
            elif ft_type == "continuous":
                d[feature] = pd.array(d[feature], dtype=pd.SparseDtype("float", 0))
            elif ft_type == "discrete":
                d[feature] = pd.array(d[feature], dtype=pd.SparseDtype("int", 0))
        return d


    def create_data_aware_features(self, train_log, test_log, ignored, missing_literal, constraint_threshold = 0.1, candidate_threshold = 0.1):
        # given log
        # 0.0. Extract events

        # 1.1. Apriori mine events to be used for constraints

        # 2. Find declare constraints to be used, On a limited set of declare templates
        # 2.1. Find support for all positive and negative cases for the constraints
        # 2.2. Filter the constraints according to support
        # -- Encode the data
        # 3. Sort constraints according to Fisher score (or other metric)
        # 4. Pick the constraint with highest Fisher score.
        # 5. Refine the constraint with data
        # 5.1. Together with data, try to create a better rule.
        # ---- In this case, every node will become a small decision tree of its own!

        # 5.2. If the Fisher score of new rule is greater, change the current rule to a refined rule
        # --- Refined rule is - constraint + a decision rules / tree, learne
        # Reorder constraints for next level of decision tree .. It is exactly like Gini impurity or sth..

        # Get templates from fabrizios article

        """
        responded existence(A, B), data on A
        response(A, B), data on A
        precedence(A, B), data on B
        alternate response(A, B), data on A
        alternate precedence(A, B), data on B
        chain response(A,B), data on A
        chain precedence(A, B), data on B
        not resp. existence (A, B), data on A
        not response (A, B), data on A
        not precedence(A, B), data on B
        not chain response(A,B), data on A
        not chain precedence(A,B), data on B

        :param log:
        :param label:
        :return:
        """

        not_templates = ["not_responded_existence",
                         "not_precedence",
                         "not_response",
                         "not_chain_response",
                         "not_chain_precedence"]

        templates = ["alternate_precedence", "alternate_response", "chain_precedence", "chain_response",
                     "responded_existence", "response", "precedence"]

        inp_templates = templates + not_templates

        # play around with thresholds
        # Extract unique activities from log
        events_set = extract_unique_events_transformed(train_log)

        # Brute force all possible candidates
        candidates = [(event,) for event in events_set] + [(e1, e2) for e1 in events_set for e2 in events_set if
                                                           e1 != e2]

        # Count by class
        normal_count, deviant_count = count_classes(train_log)
        print("{} deviant and {} normal traces in train set".format(deviant_count, normal_count))
        ev_support_norm = int(normal_count * candidate_threshold)
        ev_support_dev = int(deviant_count * candidate_threshold)

        print("Filtering candidates by support")
        candidates = filter_candidates_by_support(candidates, train_log, ev_support_norm, ev_support_dev)
        print("Support filtered candidates:", len(candidates))

        constraint_support_dev = int(deviant_count * constraint_threshold)
        constraint_support_norm = int(normal_count * constraint_threshold)

        train_results = generate_train_candidate_constraints(candidates, inp_templates, train_log, constraint_support_norm,
                                                             constraint_support_dev, filter_t=True)

        test_results = generate_test_candidate_constraints(candidates, inp_templates, test_log, train_results)
        print("Candidate constraints generated")

        ## Given selected constraints, find fulfillments and violations for each of the constraint.
        ## In this manner build positive and negative samples for data

        X_train, y_train, feature_names, train_trace_names = transform_results_to_numpy(train_results, train_log)
        X_test, y_test, _, _ = transform_results_to_numpy(test_results, test_log)

        perm = np.random.permutation(len(y_train))
        X_train = X_train[perm]
        train_trace_names = train_trace_names[perm]
        y_train = y_train[perm]

        # Turn to pandas df
        train_df_orig = pd.DataFrame(X_train, columns=feature_names, index=train_trace_names)
        del X_train
        del X_test
        del train_trace_names
        del train_results

        train_df_orig = train_df_orig.transpose().drop_duplicates().transpose()

        # remove no-variance, constants
        train_df_orig = train_df_orig.loc[:, (train_df_orig != train_df_orig.iloc[0]).any()]

        # Perform selection by Fisher
        #scores = fisher_calculation(train_df_orig, y_train) train_df_orig.values
        #selected_ranks = fisher_score.feature_ranking(scores)
        print("fscore init ...")
        #pdb.set_trace()
        selected_ranks = fisher_score.fisher_score(train_df_orig.values[:10000], y_train[:10000], mode='rank')
        print("fscore finished")
        #selected_ranks = fisher_score.fisher_score(train_df_orig.values, y_train, mode='rank')

        threshold = 15
        #chosen = 500

        real_selected_ranks = []
        # Start selecting from selected_ranks until every trace is covered N times
        trace_remaining = dict()
        for i, trace_name in enumerate(train_df_orig.index.values):
            trace_remaining[i] = threshold

        chosen = 0
        # Go from higher to lower
        for rank in selected_ranks:
            if len(trace_remaining) == 0:
                break
            chosen += 1
            # Get column
            marked_for_deletion = set()
            added = False
            for k in trace_remaining.keys():
                if train_df_orig.iloc[k, rank] > 0:
                    if not added:
                        added = True
                        real_selected_ranks.append(rank)

                    trace_remaining[k] -= 1
                    if trace_remaining[k] <= 0:
                        marked_for_deletion.add(k)

            for k in marked_for_deletion:
                del trace_remaining[k]

        print("Constraints chosen {}".format(len(real_selected_ranks)))

        feature_names = train_df_orig.columns[real_selected_ranks]

        print("Considered template count:", len(feature_names))
        train_df = train_df_orig[feature_names]

        new_train_feature_names = []
        new_train_features = []

        new_test_feature_names = []
        new_test_features = []

        count=0

        for (template, candidate) in train_df.columns:
            count += 1
            print("Testing now: "+str(template)+" && "+str(candidate))
            # Go over all and find with data
            #template = key[0]
            #candidate = key[1]

            # First have to find all locations of fulfillments
            outp_train = find_fulfillments_violations(candidate, template, train_log)
            outp_test = find_fulfillments_violations(candidate, template, test_log)

            # Take data snapshots on all fulfilled indices - positives samples
            # Take data snapshots on all unfulfilled indices - negative samples
            # Build a decision tree with fulfilled and unfulfilled samples
            train_positive_samples = []
            train_negative_samples = []

            test_positive_samples = []
            test_negative_samples = []

            for i, trace in enumerate(outp_train):
                fulfilled = trace[1]
                violated = trace[2]
                positive, negative = get_data_snapshots(train_log[i], fulfilled, violated)
                label = train_log[i]["label"]
                for s in positive:
                    train_positive_samples.append((s, label, i))
                for s in negative:
                    train_negative_samples.append((s, label, i))


            for i, trace in enumerate(outp_test):
                fulfilled = trace[1]
                violated = trace[2]
                positive, negative = get_data_snapshots(test_log[i], fulfilled, violated)
                label = train_log[i]["label"]

                for s in positive:
                    test_positive_samples.append((s, label, i))

                for s in negative:
                    test_negative_samples.append((s, label, i))

            if (len(test_positive_samples) == 0) and (len(test_negative_samples) == 0):
                continue # Skip if I cannot (later on) test the configuration

            # Get all where fulfilled only. Train on train_positive_samples vs Label of log
            ignored_features = set(ignored) # set([('Diagnose', 'literal')])

            collected_features = set()
            #Optimizing the code, so that scanning and filtering is performed only once
            for pos_act, _, __ in train_positive_samples:
                for key2, val in pos_act.items():
                    if (key2[1] in {"boolean", "continuous", "discrete", "literal"}) and (key2[0] not in ignored_features):
                        collected_features.add(key2)
            for neg_act, _, __ in train_negative_samples:
                for key2, val in neg_act.items():
                    if (key2[1] in {"boolean", "continuous", "discrete", "literal"}) and (key2[0] not in ignored_features):
                        collected_features.add(key2)
            features = list(collected_features)
            del collected_features

            features_label = ["id"] + features + ["Label"]

            feature_train_df = None
            if True:
                d = dict()
                d = self.init_d_dictionary(d, features, "id", "Label")
                d = self.create_sample2(d, map(lambda sample: (sample[2], sample[0]), train_positive_samples), features, 1, "id", "Label")
                d = self.create_sample2(d, map(lambda sample: (sample[2], sample[0]), train_negative_samples), features, 0, "id", "Label")
                d = self.finalize_map(d, features, missing_literal)
                feature_train_df = pd.DataFrame(d, columns=features_label)
            train_ids = feature_train_df.pop("id")

            train_df  = None
            if True:
                d = dict()
                d = self.init_d_dictionary(d, features, "id", "Label")
                d = self.create_sample2(d, map(lambda sample: (sample[2], sample[0]) , filter(lambda sample : sample[1] == 1, train_positive_samples)), features, 1, "id", "Label")
                d = self.create_sample2(d, map(lambda sample: (sample[2], sample[0]) , filter(lambda sample : sample[1] == 0, train_positive_samples)), features, 0, "id", "Label")
                d = self.finalize_map(d, features, missing_literal)
                train_df = pd.DataFrame(d, columns=features_label)
                train_df.pop("id")

            # one-hot encode literal features
            # Extract positive test samples, where fulfillments where fulfilled
            test_df = None
            if True:
                d = dict()
                d = self.init_d_dictionary(d, features, "id", "Label")
                d = self.create_sample2(d, map(lambda sample: (sample[2], sample[0]), test_positive_samples), features, 1, "id", "Label")
                d = self.create_sample2(d, map(lambda sample: (sample[2], sample[0]), test_negative_samples), features, 0, "id", "Label")
                d = self.finalize_map(d, features, missing_literal)
                test_df = pd.DataFrame(d, columns=features_label)
            test_ids = test_df.pop("id")

            # Possible values for each literal value is those in train_df or missing
            if True:
                for selection in filter(lambda feature: feature[1]=="literal", features):
                    train_df[selection] = pd.Categorical(train_df[selection])
                    test_df[selection] = pd.Categorical(test_df[selection])
                    feature_train_df[selection] = pd.Categorical(feature_train_df[selection])
                    le = LabelEncoder()

                    le.fit(list(test_df[selection]) + list(feature_train_df[selection]))
                    classes = le.classes_
                    train_df[selection] = le.transform(train_df[selection])
                    test_df[selection] = le.transform(test_df[selection])
                    feature_train_df[selection] = le.transform(feature_train_df[selection])

                    ohe = OneHotEncoder(categories="auto") # Remove this for server.
                    ohe.fit(np.concatenate((test_df[selection].values.reshape(-1, 1),
                                            feature_train_df[selection].values.reshape(-1, 1)), axis=0),)

                    test_transformed = None
                    train_transformed = ohe.transform(train_df[selection].values.reshape(-1, 1)).toarray()
                    if (len(test_df.index) > 0):
                        test_transformed = ohe.transform(test_df[selection].values.reshape(-1, 1)).toarray()
                    feature_train_transformed = ohe.transform(feature_train_df[selection].values.reshape(-1, 1)).toarray()

                    dfOneHot = pd.DataFrame(train_transformed,
                                            columns=[(selection[0] + "_" + classes[i], selection[1]) for i in
                                                     range(train_transformed.shape[1])], dtype=pd.SparseDtype("int", 0))
                    train_df = pd.concat([train_df, dfOneHot], axis=1)
                    train_df.pop(selection)
                    if (len(test_df.index) > 0):
                        dfOneHot = pd.DataFrame(test_transformed,
                                            columns=[(selection[0] + "_" + classes[i], selection[1]) for i in
                                                     range(train_transformed.shape[1])], dtype=pd.SparseDtype("int", 0))
                        test_df = pd.concat([test_df, dfOneHot], axis=1)
                        test_df.pop(selection)

                    dfOneHot = pd.DataFrame(feature_train_transformed,
                                            columns=[(selection[0] + "_" + classes[i], selection[1]) for i in
                                                     range(train_transformed.shape[1])], dtype=pd.SparseDtype("int", 0))
                    feature_train_df = pd.concat([feature_train_df, dfOneHot], axis=1)
                    feature_train_df.pop(selection)

            data_dt = DecisionTreeClassifier(max_depth=3)
            y_train = train_df.pop("Label")

            y_test = test_df.pop("Label")
            data_dt.fit(train_df, y_train)

            y_train_new = feature_train_df.pop("Label")

            train_predictions = data_dt.predict(feature_train_df)
            test_predictions = data_dt.predict(test_df)

            # Go through all traces again
            # Save decision trees here. For later interpretation
            feature_train_df["id"] = train_ids
            test_df["id"] = test_ids

            feature_train_df["prediction"] = train_predictions
            test_df["prediction"] = test_predictions

            # Check for which activations the data condition holds. Filter everything else out.

            feature_train_df["Label"] = y_train_new
            test_df["Label"] = y_test

            count_fulfilled_train = False
            new_train_feature = []
            for i, trace in enumerate(outp_train):
                # Get from train_df by number
                trace_id = i
                freq = trace[0]

                # Find all related to the id

                if freq == 0:
                    # vacuous case, no activations, will be same here.
                    new_train_feature.append(0)
                else:
                    # Previous violation case
                    # Find samples related to trace
                    samples = feature_train_df.loc[(feature_train_df.id == trace_id) & (feature_train_df.prediction == 1), "Label"].values
                    positive = samples.sum()
                    negative = samples.size - positive
                    if negative > 0:
                        new_train_feature.append(-1)
                    else:
                        count_fulfilled_train = True
                        new_train_feature.append(positive)
            del outp_train
            new_train_feature = pd.array(new_train_feature, dtype=pd.SparseDtype("int", 0))

            count_fulfilled_test = False
            new_test_feature = []
            for i, trace in enumerate(outp_test):
                # Get from train_df by number
                trace_id = i
                freq = trace[0]
                # Find all related to the id
                if freq == 0:
                    # vacuous case, no activations, will be same here.
                    new_test_feature.append(0)
                else:
                    # Previous violation case
                    # Find samples related to trace
                    samples = test_df.loc[(test_df.id == trace_id) & (test_df.prediction == 1), "Label"].values
                    positive = samples.sum()
                    negative = samples.size - positive
                    if negative > 0:
                        new_test_feature.append(-1)
                    else:
                        count_fulfilled_test = True
                        new_test_feature.append(positive)
            del outp_test
            new_test_feature = pd.array(new_test_feature, dtype=pd.SparseDtype("int", 0))
            # Find all activations

            if count_fulfilled_train and count_fulfilled_test:
                # only then add new feature..
                new_train_features.append(new_train_feature)
                new_train_feature_names.append(template + ":({},{}):Data".format(candidate[0], candidate[1]))

                new_test_features.append(new_test_feature)
                new_test_feature_names.append(template + ":({},{}):Data".format(candidate[0], candidate[1]))

        return new_train_feature_names, new_train_features, new_test_feature_names, new_test_features


def declare_data_aware_embedding(ignored, inp_folder, train_log, test_log, missing_literal, self, constraint_threshold = 0.1, candidate_threshold = 0.1):
    drc = DRC()
    doStoreSecondFile = not (len(test_log) == 0)
    if not doStoreSecondFile:
        test_log = train_log.copy()
    # print(train_log[0])
    train_case_ids = [tr["name"] for tr in train_log]
    test_case_ids = [tr["name"] for tr in test_log]
    train_names, train_features, test_names, test_features = drc.create_data_aware_features(train_log, test_log, ignored, missing_literal, constraint_threshold=constraint_threshold, candidate_threshold=candidate_threshold)
    train_dict = {}
    test_dict = {}
    for i, tf in enumerate(train_features):
        train_dict[train_names[i]] = tf
    if doStoreSecondFile:
        for i, tf in enumerate(test_features):
            test_dict[test_names[i]] = tf
    train_df = pd.DataFrame.from_dict(train_dict)
    if doStoreSecondFile:
        test_df = pd.DataFrame.from_dict(test_dict)
    else:
        test_df = pd.DataFrame()

    train_df["Case_ID"] = train_case_ids
    if doStoreSecondFile:
        test_df["Case_ID"] = test_case_ids
        test_df = extendDataFrameWithLabels(test_df, propositionalized_trace_to_label_map(test_log))

    train_df = extendDataFrameWithLabels(train_df, propositionalized_trace_to_label_map(train_log))

    j =  genericDump(inp_folder, train_df, test_df, "dwd_train.csv", "dwd_test.csv")
    dump_in_primary_memory_as_table_csv(self, "dwd", train_df, test_df)
    return j
    # PandaExpress.serialize(train_df, os.path.join(inp_folder, "dwd_train.csv"))
    # if doStoreSecondFile:
    #     PandaExpress.serialize(test_df, os.path.join(inp_folder, "dwd_test.csv"))
    # return PandaExpress.ExportDFRowNamesAsSets(test_df, train_df)

