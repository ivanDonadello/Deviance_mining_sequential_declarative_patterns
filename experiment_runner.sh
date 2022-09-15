#!/usr/bin/env bash

log_names=("traffic" "bpi11" "bpi12" "bpi15A" "bpi15B" "bpi15C" "bpi15D" "bpi15E")

for log_name in ${log_names[*]}; do
    python run_experiments.py --dataset=$log_name &
done