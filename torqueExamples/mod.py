import getopt, sys, os, shutil

def toFile(list):
    f = open("output.sh", "w")
    f.writelines(list)

def help():
    print("help")

def main():
    num = 0
    numFound = False
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["help", "num="])
    except getopt.GetoptError as err:
        print(err) 
        sys.exit(2)
    for o, a in opts:
        if o == "--help":
            help()
        elif o == "--num":
            numFound = True
            if a.isdigit():
                num = a
            else: 
                print("num was not a digit")
                os._exit(-1)
        else:
            assert False, "unhandled option"
    if not numFound:
        print("no num provided exiting")
        os._exit(-1)
    elif int(num)<1:
        print("num too smol")
        os._exit(-1)
    else:
        f = open("more.sh", "r")
        text = f.readlines()
        for i in range(len(text)):
            if text[i].find("#PBS -J") != -1:
                text[i] = "#PBS -J 1-" + str(num) + "\n"
            if text[i].find("--num_workers 30") != -1:
                text[i] = "       --num_workers 30 --max_num_devices_per_node 2 " + \
                        "--total_num_nodes " + str(num) + " \\\n"
            if text[i].find("DDP_DIR=$OUTPUT_ROOT/$JOB_NAME/ddp") != -1:
                text[i] = "DDP_DIR=~/SALIENT/job_output/ddp/" + str(num) + "/\n"
                if not os.path.isdir("/home/jhembre/SALIENT/job_output/ddp/" +
                        str(num) + "/"):
                    os.makedirs("/home/jhembre/SALIENT/job_output/ddp/" +
                        str(num) + "/")
                else:
                    shutil.rmtree("/home/jhembre/SALIENT/job_output/ddp/" +
                        str(num) + "/")
                    os.makedirs("/home/jhembre/SALIENT/job_output/ddp/" +
                        str(num) + "/")

    toFile(text)

if __name__ == "__main__":
    main()
