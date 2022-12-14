from subprocess import Popen, PIPE
import time
import shutil
import os

def mod(model, nodes, gpus):
    outputLocation = "/home/jhembre/SALIENT/job_output/" + str(model) + "_nodes_" + str(nodes) + "_gpus_" + str(gpus) 
    isExist = os.path.exists(outputLocation)
    if not isExist:
        os.makedirs(outputLocation)
    else:
        shutil.rmtree(outputLocation)
        os.makedirs(outputLocation)


    dirLocation = "/home/jhembre/SALIENT/job_output/ddp/" + str(model) + "/nodes_" + \
            str(nodes) + "/gpus_" + str(gpus)
    isExist = os.path.exists(dirLocation)
    if not isExist:
        os.makedirs(dirLocation)
    else:
        shutil.rmtree(dirLocation)
        os.makedirs(dirLocation)
    lines = [
        "#!/bin/bash",
        "#",
        "#PBS -N " + str(model) + "_nodes_" + str(nodes) + "_gpus_" + str(gpus),
        "#PBS -l select=1:ncpus=2:mem=250gb:ngpus=" + str(gpus) +":gpu_model=a100,walltime=8:00:00",
        "#PBS -J 1-" + str(nodes),
        "#PBS -j oe",
        "# Activate environment",
        "HOME2=/scratch1/$(whoami)",
        "PYTHON_VIRTUAL_ENVIRONMENT=salient",
        "source activate $PYTHON_VIRTUAL_ENVIRONMENT",
        "# Get JOB_NAME (set at the beginning of this script)",
        "JOB_NAME=$PBS_JOBNAME",
        "# Set SALIENT root and PYTHONPATH",
        "SALIENT_ROOT=$HOME/SALIENT",
        "export PYTHONPATH=$SALIENT_ROOT",
        "# Set the data paths",
        "DATASET_ROOT=$HOME/dataset",
        "OUTPUT_ROOT=$SALIENT_ROOT/job_output",
        "# Speficy directory for --ddp_dir. It must be an empty dir. For",
        "# example, it is not wise to use $OUTPUT_ROOT/$JOB_NAME, if prior",
        "# results are there",
        "DDP_DIR=" + str(dirLocation),
        "# file name is the node name",
        "touch $DDP_DIR/`hostname`",
        "# Run examples. For the full list of options, see driver/parser.py",
        "python -m driver.main ogbn-arxiv $JOB_NAME \\",
        "\t--dataset_root $DATASET_ROOT --output_root $OUTPUT_ROOT \\",
        "\t--trials 2 --epochs 3 --test_epoch_frequency 2 \\",
        "\t--model_name " + str(model) +" --test_type batchwise \\",
        "\t--overwrite_job_dir \\",
        "\t--num_workers 30 --max_num_devices_per_node " + str(gpus) + " --total_num_nodes " +
        str(nodes) +" \\",
        "\t--ddp_dir $DDP_DIR \\",
        "\t--verbose"
    ]
    f = open("outputTest.sh", "w")
    for line in lines:
        f.write(line)
        f.write('\n')


def launch():
    models = ["SAGE", "GAT"] # only two that work
    for node in range(2,3):
    #for node in range(2,15):
        for gpu in range(2,3):
        #for gpu in range(2,5):
            for model in models:
                mod(nodes=node, gpus=gpu, model=model)
                cmd = ["qsub outputTest.sh"]
                proc = Popen(cmd, shell=True, stdout=PIPE)
                stdout = proc.communicate()[0]
                readable = stdout.decode('utf-8')
                print(readable)
                ret = proc.returncode
                time.sleep(10)


def main():
    launch()
    """
    clean()
    profs = globProfiles()
    makeReadable(profs)
    convertToCsv()
    graph()
    """

if __name__ == "__main__":
    main()
