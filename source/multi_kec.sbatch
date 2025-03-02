#!/bin/bash
#SBATCH --job-name multi_kec
#SBATCH --output slurm-%x_%j.log
#SBATCH --error slurm-%x_%j.log
#SBATCH --partition=long
#SBATCH --mem-per-cpu=10G   
#SBATCH --cpus-per-task=10

CONDA_ROOT="/shared/software/miniconda/"
source "$CONDA_ROOT/etc/profile.d/conda.sh"

conda activate /shared/home/nponcelet/gbs_blast/envs/multimap

snakemake --jobs 100 \
          --verbose \
          --cluster-config config/cluster.yaml \
          --cluster "sbatch --partition={cluster.partition} --time={cluster.time} --cpus-per-task={cluster.cpus-per-task} --mem-per-cpu={cluster.mem-per-cpu} --output={cluster.output} --error={cluster.error}"