import yaml
import csv
import argparse
from yaml.loader import SafeLoader
import pdb
import numpy as np
import pandas as pd
import os

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--clf', type=str, default="dt")
args = parser.parse_args()
dict_args = vars(args)
clf = dict_args['clf']

# Open the file and load the file
with open('config.yaml') as f:
    config = yaml.load(f, Loader=SafeLoader)

csv_header = ["Dataset"] + [config['feature_encoding_map'][encoding] for encoding in config['feature_encoding_list']]
metrics_for_CD = [f"F1_fold{k}" for k in range(config['fold_cross_val'])]
results_table = []
for dataset in config['dataset_list']:
    results_df = pd.read_csv(f"results/{clf}_{dataset}.csv")
    for labeling in config['labelling_list'][dataset]:
        results_table.append([f"{dataset}_{labeling}"])
        for encoding in config['feature_encoding_list']:
            tmp_df = results_df.loc[(results_df['Labelling'] == labeling) & (results_df['Encoding'] == encoding)]
            # results_table[-1].append(tmp_df.iloc[0, 5:].mean())
            # pdb.set_trace()
            results_table[-1].append(np.mean(tmp_df[metrics_for_CD].values))

with open(os.path.join(config['results_folder'], f"{clf}_table_CD.csv"), 'w') as f:
    writer = csv.writer(f)
    writer.writerow(csv_header)
    for row in results_table:
        writer.writerow(row)

# TODO sii sicuro che tmp_df abbia solo una riga!