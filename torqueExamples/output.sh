#!/bin/bash
#
#PBS -N example_Satori_batch_2_nodes
#PBS -l select=1:ncpus=2:mem=250gb:ngpus=2:gpu_model=a100,walltime=8:00:00
#PBS -J 1-14
#PBS -j oe

# Script to run examples in the batch mode on Satori (2 nodes). READ
# ALL INSTRUCTIONS!!
#
# Submit the job using
#
# $ sbatch SALIENT/examples/example_Satori_batch_2_nodes.slurm
#
# Watch the job using
#
# $ squeue

# Activate environment
HOME2=/scratch1/$(whoami)
PYTHON_VIRTUAL_ENVIRONMENT=salient
source activate $PYTHON_VIRTUAL_ENVIRONMENT

# Get JOB_NAME (set at the beginning of this script)
JOB_NAME=$PBS_JOBNAME

# The current program hardcodes using the environment variable
# SLURMD_NODENAME to distinguish machines. On Satori, the scheduler
# will set this variable.

# Set SALIENT root and PYTHONPATH
SALIENT_ROOT=$HOME/SALIENT
export PYTHONPATH=$SALIENT_ROOT

# Set the data paths
DATASET_ROOT=$HOME/dataset
OUTPUT_ROOT=$SALIENT_ROOT/job_output

# Speficy directory for --ddp_dir. It must be an empty dir. For
# example, it is not wise to use $OUTPUT_ROOT/$JOB_NAME, if prior
# results are there
DDP_DIR=~/SALIENT/job_output/JudTest/ddp/14/
# Jud ----> SALIENT/example_Satori_batch_2_nodes/ddp
#
# MANUALLY CREATE DDP_DIR IF NOT EXISTENT, OR CLEAR ALL CONTENTS
# INSIDE IF EXISTENT!! CANNOT DO SO IN THIS SCRIPT, BECAUSE MULTIPLE
# NODES WILL TRY TO CREATE/CLEAR, INTERFERING WITH THE NEXT TOUCH.
#
# Then, under the dir, create one empty file for each node, where the
# file name is the node name
touch $DDP_DIR/`hostname`

# Run examples. For the full list of options, see driver/parser.py
#
# Turn on --verbose to see timing statistics
#
# 2 node, 2 GPUs/node, must do ddp
python -m driver.main ogbn-arxiv $JOB_NAME \
       --dataset_root $DATASET_ROOT --output_root $OUTPUT_ROOT \
       --trials 2 --epochs 3 --test_epoch_frequency 2 \
       --model_name SAGE --test_type batchwise \
       --overwrite_job_dir \
       --num_workers 30 --max_num_devices_per_node 2 --total_num_nodes 14 \
       --ddp_dir $DDP_DIR \
