import pandas as pd
import os
import csv
import pdb
import numpy as np

res_dir = 'data/experiments'
dataset_list = ['bpi12', 'bpi15B', 'bpi15C', 'bpi15E', 'bpi15D', 'sepsis']
encoding_list = ['decl', 'mr_tr', 'mra_tra', 'payload']
strategy_list = ['IA', 'Declare', 'IA+MR', 'IA+TR', 'IA+TRA', 'IA+MRA', 'Hybrid', 'Payload', 'Data+IA', 'Data+Declare',
                 'Data+IA+MR', 'Data+IA+TR', 'Data+IA+TRA', 'Data+IA+MRA', 'Data+Hybrid', 'Declare Data Aware',
                 'Payload+Declare Data Aware', 'Hybrid+Declare Data Aware', 'Hybrid+Payload+Declare Data Aware']
metrics = ['precision', 'recall', 'f1', 'auc']

res_dict = {}
for encoding in encoding_list:
    res_dict[encoding] = {}
    for strategy in strategy_list:
        res_dict[encoding][strategy] = {}
        for metric in metrics:
            res_dict[encoding][strategy][metric] = []

for encoding in encoding_list:
    for dataset_name in dataset_list:
        for dir in os.listdir(res_dir):
            if dir.startswith(f'{dataset_name}_{encoding}') and dir.endswith('results'):
                res_df = pd.read_csv(os.path.join(res_dir, dir, 'benchmarks.csv'))
                #if encoding == 'decl':
                    #print(dir)
                for strategy in strategy_list:
                    tmpA_df = res_df[res_df['strategy'] == strategy]
                    tmp_res_per_dt_depth = {m: [] for m in metrics}
                    for dt_depth in tmpA_df['confvalue'].unique():
                        tmpB_df = tmpA_df[tmpA_df['confvalue'] == dt_depth]
                        for metric in metrics:
                            tmp_res_per_dt_depth[metric].append(tmpB_df[tmpB_df['metrictype'] == metric]['metricvalue'].mean())

                    for metric in metrics:
                        res_dict[encoding][strategy][metric].append(np.max(tmp_res_per_dt_depth[metric]))
                #print(dir)
#pdb.set_trace()
print("df")
with open('results_ivan.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['encoding', 'strategy', 'precision', 'recall', 'f1', 'auc'])
    for encoding in encoding_list:
        for strategy in strategy_list:
            tmp_list = []
            for metric in metrics:
                tmp_list.append(np.mean(res_dict[encoding][strategy][metric]))

            writer.writerow([encoding, strategy] + tmp_list)