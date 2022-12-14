from typing import List
from glob import glob
import pandas as pd
import pstats
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
    clean()
    profs = globProfiles()
    makeReadable(profs)
    convertToCsv()
    graph()

if __name__ == "__main__":
    main()
