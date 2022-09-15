"""
Mia pipeline di classification dai dataset prodotti da codice Giacomo
"""

import pandas as pd
import os
import pdb
import math
import wittgenstein as lw
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import mutual_info_classif
from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn import metrics
from sklearn.metrics import precision_recall_fscore_support
import yaml
import csv
import argparse
from yaml.loader import SafeLoader
from datetime import datetime


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


feature_strategy_list = [math.sqrt, 0.2, 0.3]

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--dataset', type=str, default="sepsis")
args = parser.parse_args()
dict_args = vars(args)


dataset_name = dict_args['dataset']

# Open the file and load the file
with open('config.yaml') as f:
    config = yaml.load(f, Loader=SafeLoader)

config['dataset_list'] = [dataset_name]

skf_grd_search = StratifiedKFold(n_splits=config['fold_grd_search'], random_state=0, shuffle=True)
skf_cross_val = StratifiedKFold(n_splits=config['fold_cross_val'], random_state=42, shuffle=True)

results = []
results_header = []
for fold_id in range(config['fold_cross_val']):
    results_header.append(f"Prec_fold{fold_id}")
    results_header.append(f"Rec_fold{fold_id}")
    results_header.append(f"F1_fold{fold_id}")
    results_header.append(f"AUC_fold{fold_id}")
results_header = ["timestamp", "Classifier", "Dataset", "Labelling", "Encoding"] + results_header

for clf_name in config['classifiers_list']:
    for dataset in config['dataset_list']:
        for labelling in config['labelling_list'][dataset]:
            for encoding in config['feature_encoding_list']:
                tmp_results = [clf_name, dataset, labelling, encoding]
                print(f"{bcolors.OKGREEN}Loading data for {clf_name}, {dataset}, {labelling}, {encoding} ...{bcolors.ENDC}")

                dataset_path = os.path.join(config['data_folder'], config['exp_folder'],
                                            f"{dataset}_{labelling}_results", "split1", encoding, "dataset.csv")

                if not os.path.exists(dataset_path):
                    test_path = os.path.join(config['data_folder'], config['exp_folder'], f"{dataset}_{labelling}_results", "split1", encoding, f"{encoding}_test.csv")
                    train_path = os.path.join(config['data_folder'], config['exp_folder'], f"{dataset}_{labelling}_results", "split1", encoding, f"{encoding}_train.csv")
                    test_df = pd.read_csv(test_path)
                    train_df = pd.read_csv(train_path)

                    X = pd.concat([train_df, test_df])
                    y = X['Label'].values
                    X.to_csv(os.path.join(config['data_folder'], config['exp_folder'], f"{dataset}_{labelling}_results", "split1", encoding, 'dataset.csv'), index=False)
                    X = X.drop(columns=['Case_ID', 'Label'])
                else:
                    dataset_df = pd.read_csv(dataset_path)
                    y = dataset_df['Label'].values
                    X = dataset_df.drop(columns=['Case_ID', 'Label'])
                    pdb.set_trace()
                    X.fillna(0, inplace=True)

                if clf_name == 'dt':
                    clf = DecisionTreeClassifier()
                    clf_parameters = config['parameters_dt']
                elif clf_name == 'ripperK':
                    clf = lw.RIPPER(random_state=10, verbosity=0, k=10)
                    clf_parameters = config['parameters_ripperK']
                else:
                    raise Exception(f"{clf_name} classifier not supported")

                print(f"Processing {clf_name}, {dataset}, {labelling}, {encoding} ...")
                for train_index, test_index in skf_cross_val.split(X, y):
                    X_train, X_test = X.iloc[train_index], X.iloc[test_index]
                    y_train, y_test = y[train_index], y[test_index]

                    feature_strategy_res = {}
                    best_feature_strategy = None
                    best_model = None
                    best_feat = None
                    best_f1 = 0.0
                    for feature_strategy in feature_strategy_list:
                        num_features = X_train.shape[1]
                        if callable(feature_strategy):
                            num_new_features = round(feature_strategy(num_features))
                        elif isinstance(feature_strategy, float):
                            num_new_features = round(feature_strategy*num_features)
                        else:
                            raise Exception("Feature selection strategy not implemented")

                        num_new_features = 1 if num_new_features < 1 else num_new_features
                        selector = SelectKBest(mutual_info_classif, k=num_new_features)
                        selector.fit_transform(X_train, y_train)
                        cols = selector.get_support(indices=True)
                        X_train_new_features = X_train.iloc[:, cols]
                        gsCV = GridSearchCV(clf, clf_parameters, n_jobs=-1, cv=skf_grd_search, scoring='f1')
                        gsCV.fit(X_train_new_features, y_train)

                        if gsCV.best_score_ > best_f1:
                            best_model = gsCV.best_estimator_
                            best_f1 = gsCV.best_score_
                            best_feat = cols
                            best_feature_strategy = feature_strategy

                    print(f"Best feat strategy {best_feature_strategy}")
                    X_test_new_features = X_test.iloc[:, best_feat]
                    y_test_pred = best_model.predict(X_test_new_features)
                    # keep probabilities for the positive outcome only
                    y_test_pred_score = best_model.predict_proba(X_test_new_features)[:, 1]
                    prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_test_pred, average='binary')
                    fpr, tpr, _ = metrics.roc_curve(y_test, y_test_pred_score)
                    auc = metrics.auc(fpr, tpr)
                    tmp_results.append(prec)
                    tmp_results.append(rec)
                    tmp_results.append(f1)
                    tmp_results.append(auc)
                print(tmp_results)
                results.append([str(datetime.now())] + tmp_results)

#with open(config['results_file'], 'a') as f:
with open(os.path.join(config['results_folder'], f"rk_{dataset_name}.csv"), 'w') as f:
    writer = csv.writer(f)
    writer.writerow(results_header)
    for row in results:
        writer.writerow(row)
