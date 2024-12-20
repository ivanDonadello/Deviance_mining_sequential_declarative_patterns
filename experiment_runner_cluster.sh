#!/bin/bash


#SBATCH --ntasks=24
#SBATCH --mem=120G
#SBATCH --partition=cpu
#SBATCH --account=ml4prom
#SBATCH --time=07:00:00
#SBATCH --output=tst-%j.out
#SBATCH --error=tst-%j.err

cd ~/Deviance_mining_sequential_declarative_patterns-master
module load python/3.10.8-gcc-12.1.0-linux-ubuntu22.04-x86_64
source ml4prom/bin/activate


log_names=("sepsis" "traffic" "bpi11" "bpi12" "bpi15A" "bpi15B" "bpi15C" "bpi15D" "bpi15E")

for log_name in ${log_names[@]}; do
    echo Processing $log_name
    python run_experiments.py --dataset=$log_name &
done
wait
echo "All combinations have been executed."
