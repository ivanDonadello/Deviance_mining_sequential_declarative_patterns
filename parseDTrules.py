"""
Parsing of the saved DT rules
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

results = []

for dataset in config['dataset_list']:
    for labeling in config['labelling_list'][dataset]:
        print(f"{dataset} {labeling}")

        # Open the file with the rules
        with open(f"data/experiments/{dataset}_{labeling}_results/rules.txt", "r") as file:
        # Iterate through each line in the file
            for line in file:
			    # Split the line by "::" to get the parts
                parts = line.split("::")
        
                rule_part = parts[-1]
            
                # Split the conditions by 'and'
                conditions = rule_part.split("and")
            
                # Count the number of conditions
                num_conditions = len(conditions)
            
                # Print the number of conditions for this line
                print(f"{parts[:-1]} - Number of conditions: {num_conditions}")
                labeling_encoding = parts[0].split("_")
        
                results.append([labeling_encoding[0], labeling_encoding[1].replace("2", ""), parts[3], num_conditions])

results_df = pd.DataFrame(results, columns=["Dataset", "Labeling", "Encoding", "Average Rule Length"])
print(results_df)

aggregated_df = results_df.groupby(['Labeling', 'Encoding'], as_index=False)['Average Rule Length'].mean()
aggregated_df['Encoding'].replace({'Data+Hybrid': 'Data+H', 'Data+IA+MR': 'Data+MR', 'Data+IA+MRA': 'Data+MRA', 'Data+IA+TR': 'Data+TR', 'Data+IA+TRA': 'Data+TRA', 'Declare Data Aware': 'DeclD', 'Hybrid': 'H', 'Hybrid+Declare Data Aware': 'H+DeclD', 'Hybrid+Payload+Declare Data Aware': 'H+Data+DeclD', 'IA+MR': 'MR', 'IA+MRA': 'MRA', 'IA+TR': 'TR', 'IA+TRA': 'TRA', 'Payload': 'Data', 'Payload+Declare Data Aware': 'Data+DeclD'}, inplace=True)
aggregated_df.to_csv("results_bise/tmp_aggregated_ruleLength_DT.csv")
