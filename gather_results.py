"""
Computazione dei risultati aggregati da i risultati della mia pipeline
"""
import pdb
import pandas as pd
import yaml
import os
import numpy as np
import csv
from yaml.loader import SafeLoader

# Open the file and load the file
with open('config.yaml') as f:
    config = yaml.load(f, Loader=SafeLoader)

results_header1 = ['']
results_header2 = ['Labelling'] + ['Prec', 'Rec', 'F1', 'AUC']*len(config['feature_encoding_list'])
for encoding in config['feature_encoding_list']:
    results_header1 += [config['feature_encoding_map'][encoding]]*4



#config['results_folder'],
input_classifier = 'rk'
results_df = pd.read_csv(os.path.join(config['results_folder'], f"{input_classifier}_{config['dataset_list'][0]}.csv"))


for dataset in config['dataset_list'][1:]:
    tmp_df = pd.read_csv(os.path.join(config['results_folder'], f"{input_classifier}_{dataset}.csv"))
    results_df = pd.concat([results_df, tmp_df], axis=0)

results_dict = {}
with open(os.path.join(config['results_folder'], f"{input_classifier}_{config['aggregated_results_file']}"), 'w') as f:
    writer = csv.writer(f)
    writer.writerow(results_header1)
    writer.writerow(results_header2)

    for labelling in config['standard_labellings']:
        results_dict[labelling] = {}
        metrics_per_encoding = []
        for encoding in config['feature_encoding_list']:
            results_dict[labelling][config['feature_encoding_map'][encoding]] = {}
            metrics_per_dataset = []
            for dataset in config['dataset_list']:

                query_res_df = results_df[(results_df['Dataset'] == dataset) &
                                          (results_df['Labelling'].str.contains(labelling)) &
                                          (results_df['Encoding'] == encoding)]
                query_res_df = query_res_df.mean(axis=0)
                tmp_metrics_res = []  # tmp_metrics_res is a matrix whose cols are the metrics and rows the results for each fold
                for fold_id in range(config['fold_cross_val']):
                    tmp_metrics_res.append([query_res_df[f'Prec_fold{fold_id}'], query_res_df[f'Rec_fold{fold_id}'],
                                            query_res_df[f'F1_fold{fold_id}'], query_res_df[f'AUC_fold{fold_id}']])

                results_dict[labelling][config['feature_encoding_map'][encoding]][dataset] = tmp_metrics_res
                metrics_per_dataset.append(np.mean(tmp_metrics_res, axis=0).tolist())
            metrics_per_encoding += np.around(100*np.mean(metrics_per_dataset, axis=0), 2).tolist()
        writer.writerow([labelling] + metrics_per_encoding)

