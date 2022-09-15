# Exploring Business Process Deviance with Sequential and Declarative Patterns

This reposotory contains the source code for the paper "Exploring Business Process Deviance with Sequential and Declarative Patterns".

## Setup  Guide

- install the requirements for the project by using `pip3 install -r requirements.txt`.
- create the folder `data/experiments` and download and unzip the datasets from [here](https://scientificnet-my.sharepoint.com/:f:/g/personal/idonadello_unibz_it/Euyx29QOy_JGjT1TBYQHT9ABiQp0eNC8vVB2urErX0979Q?e=E9Jv4t).
- create the folder `results`.

## Running the experiments
- The command `./experiment_runner.sh` will run all the experiments in a Linux environment;
- The command `python run_experiments.py --dataset=LOG_NAME` will run the experiments for a single log. The names of the logs are `traffic`, `bpi11`, `bpi12`, `bpi15A`, `bpi15B`, `bpi15C`, `bpi15D`, `bpi15E`;
- The command `gather_results.py` will aggregate the results.