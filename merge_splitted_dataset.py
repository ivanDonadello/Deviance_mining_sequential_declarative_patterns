"""
Fa il merge dei dataset prodotti da codice di Giacomo secondo i vari fold/split
"""

import pandas as pd
import os
import pdb
import yaml
from yaml.loader import SafeLoader


# Open the file and load the file
with open('config.yaml') as f:
    config = yaml.load(f, Loader=SafeLoader)

for dataset in config['dataset_list']:
    for labelling in config['labelling_list'][dataset]:

        for encoding in config['feature_encoding_list']:

            dataset_path = os.path.join(config['data_folder'], config['exp_folder'],
                                        f"{dataset}_{labelling}_results", "split1", encoding, "dataset.csv")

            if not os.path.exists(dataset_path):
                print(f"Merging {dataset}, {labelling}, {encoding}")
                X = pd.DataFrame()
                test_path = os.path.join(config['data_folder'], config['exp_folder'], f"{dataset}_{labelling}_results",
                                         "split1", encoding, f"{encoding}_test.csv")
                train_path = os.path.join(config['data_folder'], config['exp_folder'], f"{dataset}_{labelling}_results",
                                          "split1", encoding, f"{encoding}_train.csv")

                test_df = pd.read_csv(test_path)
                train_df = pd.read_csv(train_path)
                X = pd.concat([X, train_df, test_df])

                total_cases = len(X)
                pos_cases = X['Label'].sum()
                neg_cases = total_cases - pos_cases
                print(f"\tTotal cases {total_cases}, pos cases {pos_cases} ({100*pos_cases/total_cases:.2f}%), "
                      f"neg cases {neg_cases} ({100*neg_cases/total_cases:.2f}%)")
                X.to_csv(dataset_path, index=False)
            else:
                print(f"Pass {dataset}, {labelling}, {encoding} ...")