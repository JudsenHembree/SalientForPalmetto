#!/bin/bash
#
#PBS -N GAT_nodes_2_gpus_2
#PBS -l select=1:ncpus=2:mem=250gb:ngpus=2:gpu_model=a100,walltime=8:00:00
#PBS -J 1-2
#PBS -j oe
# Activate environment
HOME2=/scratch1/$(whoami)
PYTHON_VIRTUAL_ENVIRONMENT=salient
source activate $PYTHON_VIRTUAL_ENVIRONMENT
# Get JOB_NAME (set at the beginning of this script)
JOB_NAME=$PBS_JOBNAME
# Set SALIENT root and PYTHONPATH
SALIENT_ROOT=$HOME/SALIENT
export PYTHONPATH=$SALIENT_ROOT
# Set the data paths
DATASET_ROOT=$HOME/dataset
OUTPUT_ROOT=$SALIENT_ROOT/job_output
# Speficy directory for --ddp_dir. It must be an empty dir. For
# example, it is not wise to use $OUTPUT_ROOT/$JOB_NAME, if prior
# results are there
DDP_DIR=/home/jhembre/SALIENT/job_output/JudTest/ddp/GAT/nodes_2/gpus_2
# file name is the node name
touch $DDP_DIR/`hostname`
# Run examples. For the full list of options, see driver/parser.py
python -m driver.main ogbn-arxiv $JOB_NAME \
	--dataset_root $DATASET_ROOT --output_root $OUTPUT_ROOT \
	--trials 2 --epochs 3 --test_epoch_frequency 2 \
	--model_name GAT --test_type batchwise \
	--overwrite_job_dir \
	--num_workers 30 --max_num_devices_per_node 2 --total_num_nodes 2 \
	--ddp_dir $DDP_DIR \
	--verbose
