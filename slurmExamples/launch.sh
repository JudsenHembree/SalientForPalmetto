#!/bin/bash
#PBS -N ana
#PBS -l select=1:ncpus=1:mem=125gb:ngpus=2:gpu_model=a100,walltime=8:00:00
#PBS -j oe

cd $PBS_O_WORKDIR
cat $PBS_NODEFILE

module load anaconda3/2022.05-gcc/9.5.0
module load cuda/11.6.2-gcc/9.5.0

source activate salient

echo here > temp.txt

cd SALIENT

./examples/example_Satori_interactive.sh
