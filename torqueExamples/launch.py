from subprocess import Popen, PIPE
from typing import List
from glob import glob
import cProfile, pstats
import time
import shutil
import pandas as pd
import numpy as np
from os import path
from matplotlib import pyplot as plt
import os



def analyze_dmp(myinfilepath, myoutfilepath):
    out_stream = open(myoutfilepath, 'w')
    ps = pstats.Stats(myinfilepath, stream=out_stream)
    sortby = 'cumulative'

    # plink around with this to get the results you need
    ps.strip_dirs().sort_stats(sortby).reverse_order().print_stats()  
    out_stream.close()

def convertToCsv():
    mycols = ['ncalls', 'tottime',  'percall',  'cumtime',  'percall2',
            'filename:lineno(function)']
    logs = glob("profile/*.log")
    for log in logs:
        csv = open(log + '.txt', 'w')
        out_stream = open(log, 'r')
        lines = out_stream.readlines()
        for i in range(len(lines)):
            if lines[i].find('ncalls') != -1:
                del lines[i]
                break
            del lines[i]

        for i in range(len(lines)):
            print(lines[i])
            line = lines[i].split(None, 5)
            print(line)
            lines[i] = ', '.join(line)

        for line in lines:
            csv.write(line)
            csv.write('\n')
        out_stream.close()
        csv.close()
        
        cleancsv = pd.read_csv(log + '.txt', names=mycols)
        cleancsv.to_csv(log + '.csv')

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

def globProfiles() -> List[str]: 
    list = []
    list = glob("profile/*")
    print(list)
    return list

def makeReadable(profs):
    for prof in profs:
        analyze_dmp(prof, prof + ".log")

def clean():
    priors = glob("profile/*.log")
    for prior in priors:
        os.remove(prior)
    priors = glob("profile/*.csv")
    for prior in priors:
        os.remove(prior)
    priors = glob("profile/*.txt")
    for prior in priors:
        os.remove(prior)


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

def graph():
    logs = glob("profile/*.csv")
    for log in logs:
        csv = pd.read_csv(log)
        fig, ax = plt.subplots(figsize=[15,30])
        categories = csv['filename:lineno(function)'].tolist()
        categories10 = categories[-20:]
        cumtime = csv['cumtime'].tolist()
        cumtime10 = cumtime[-20:]
        ax.bar(x=categories10, height=cumtime10);
        ax.plot()
        _, figname = path.split(log)
        plt.xticks(fontsize=8, rotation=90)
        plt.title(figname +'_top_20', fontsize = 20)
        plt.xlabel('Function', fontsize = 20)
        plt.ylabel('Time in Seconds', fontsize = 20)
        fig.tight_layout()
        fig.savefig("figs/"+figname +'_top_20.pdf')
        plt.close(fig)
        
    for log in logs:
        csv = pd.read_csv(log)
        fig, ax = plt.subplots(figsize=[15,30])
        categories = csv['filename:lineno(function)'].tolist()
        categories10 = categories[-16:-6]
        cumtime = csv['cumtime'].tolist()
        cumtime10 = cumtime[-16:-6]
        ax.bar(x=categories10, height=cumtime10);
        ax.plot()
        _, figname = path.split(log)
        plt.xticks(fontsize=8, rotation=70)
        plt.xlabel('Function', fontsize = 20)
        plt.ylabel('Time in Seconds', fontsize = 20)
        plt.title(figname +'_Without_top_6', fontsize = 20)
        fig.tight_layout()
        fig.savefig("figs/"+figname +'_Without_top_6.pdf')
        plt.close(fig)
 
    for log in logs:
        csv = pd.read_csv(log)
        fig, ax = plt.subplots(figsize=[20,15])
        categories = csv['filename:lineno(function)'].tolist()
        categories10 = categories
        cumtime = csv['cumtime'].tolist()
        cumtime10 = cumtime
        ax.bar(x=categories10, height=cumtime10);
        ax.plot()
        _, figname = path.split(log)
        plt.xticks(fontsize=8, rotation=45)
        fig.savefig("figs/"+figname +'all.pdf')
        plt.close(fig)
 
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
