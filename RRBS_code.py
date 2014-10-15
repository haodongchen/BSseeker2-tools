#!/usr/bin/env python
# Copyright (c) 2014 UCLA
# Authors: Haodong Chen and Thomas M. Vondriska
#
# This software is distributable under the terms of the GNU General
# Public License (GPL) v2, the text of which can be found at
# http://www.gnu.org/copyleft/gpl.html. Installing, importing or
# otherwise using this module constitutes acceptance of the terms of
# this License.
#
# Disclaimer
# 
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# Comments and/or additions are welcome (send e-mail to:
# hdchen@ucla.edu).

import subprocess, os, sys, datetime, math
import threading
MY_LOCK = threading.Lock()
# When output into log files, use this lock
from time import sleep
global Params
Params={}

def Check_jobs(joblist):
    """This code will check if certain jobs are still in queue or running in
cluster. A list of job-IDs is needed."""
    # Check if any jobs are in waiting list
    MY_LOCK.acquire()
    process = subprocess.Popen("qstat -s p -u %s | grep ^[0-9]"%os.getenv("USER"), shell=True, \
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    MY_LOCK.release()
    if len(out):
        wait_list = [int(x.split()[0]) for x in out.rstrip("\n").split("\n")]
        for jobid in joblist:
            if jobid in wait_list: return False, None

    # Check if any jobs are running
    MY_LOCK.acquire()
    process = subprocess.Popen("qstat -s r -u %s | grep ^[0-9]"%os.getenv("USER"), shell=True, \
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    MY_LOCK.release()
    if len(out):
        run_list = [int(x.split()[0]) for x in out.rstrip("\n").split("\n")]
        for jobid in joblist:
            if jobid in run_list: return True, False
    return True, True

def Job_wait(joblist, waittime):
    """Keep checking jobs to see if they finish"""
    MINWAIT = 300 if waittime > 300 else 60 # minimum waiting time: 5min or 1 min
    while(True):
        a,b = Check_jobs(joblist)
        if not a:
            sleep(waittime)
        elif a and not b:
            sleep(waittime)
            waittime = max(waittime/2,MINWAIT)
        else:
            break
    return True


def Submit_to_hoffman2(time, memory, command, outputdir=os.getcwd(), messaging="complete"):
    """This function submit job to hoffman2 and get the job-ID"""
    cmd = "job.q -t %s -d %s -k -o %s -m %s %s"%(str(time), str(memory), outputdir, messaging, command)
    MY_LOCK.acquire()
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    MY_LOCK.release()
    out=out.split("\n")
    for line in out:
        if line.startswith("Your job"):
            jobid = line.split()[2]
            break
    else:
        print >> sys.stderr, 'ERROR: Job %s submission failed.'%cmd
        exit(1)
    return int(jobid)

def Submit_to_hoffman2_array(time, memory, command, lower_index=1, higher_index=1, interval=1, outputdir=os.getcwd(), messaging="complete"):
    """This function submit job to hoffman2 and get the job-ID"""
    cmd = "jobarray.q -t %s -d %s -k -o %s -m %s "%(str(time), str(memory), outputdir, messaging)
    cmd += "-jl %s -jh %s -ji %s "%(str(lower_index),str(higher_index),str(interval))
    cmd += command
    MY_LOCK.acquire()
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    MY_LOCK.release()
    out=out.split("\n")
    for line in out:
        if line.startswith("Your job"):
            jobid = line.split()[2].split(".")[0]
            break
    else:
        print >> sys.stderr, 'ERROR: Job %s submission failed.'%cmd
        exit(1)
    return int(jobid)

def Conf_read(conf_path):
    try:
        conf = open(conf_path,'r')
    except:
        print >> sys.stderr, 'ERROR: Cannot open configuration file conf.txt'
        exit(1)
    for line in conf:
        if line[0] != "#":
            line=line.rstrip().replace(" ", "")
            if len(line) == 0: continue
            # Format for conf.txt:
            # variable=value
            variable=line.split("=")[0]
            value=line.split("=")[1]
            Params[variable]=value
    return True

def open_log(fname):
    open_log.logfile = open(fname, 'w', 1)

def logm(message):
    MY_LOCK.acquire()
    log_message = "[%s] %s\n" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message)
    print log_message,
    open_log.logfile.write(log_message)
    MY_LOCK.release()

def close_log():
    open_log.logfile.close()

def job_log(fname):
    job_log.logfile = open(fname,'w',1)

def logj(job_id):
    MY_LOCK.acquire()
    cmd = "qacct -j %s"%(str(job_id))
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    log_message = "%s\n" % (out)
    job_log.logfile.write(log_message)
    MY_LOCK.release()

def job_log_close():
    job_log.logfile.close()

class Worker(threading.Thread):
    """Each Worker handles one Barcoded folder."""
    
    def __init__(self, subfolder, options_folder):
        threading.Thread.__init__(self)
        if subfolder == ".":
            self.folder = options_folder
            self.name = "Job"
        else:
            self.folder = os.path.join(options_folder, subfolder)
            self.name = subfolder
            
    def run(self):
        self.Step2()
        self.Step3()
        self.Step4()

    def Step2(self):
        """Align using bs-seeker2"""
        logm("%s: Alignment starts."%self.name)
        file_list = [x for x in os.listdir(self.folder) if x.endswith("qseq.txt") or x.endswith("qseq.txt.gz")]
        mem = 8192 # 8G mem should be enough for most analysis. Usually 6GB is enough.
        job_id = Submit_to_hoffman2_array(24, mem, "Step2.py -i %s --conf %s"%(self.folder, conf), lower_index=1, higher_index=len(file_list), interval=1, messaging="error"))
        Job_wait([job_id], 60*60) # This part may take up to two hours
        logj(job_id)
        logm("%s: Alignment ends."%self.name)

    def Step3(self):
        """Merge bam files"""
        logm("%s: Merge bam files."%self.name)
        cmd = os.path.join(Params['BSPATH'],"MyBamPostProcess.py")
        p = " -i %s"%self.folder
        cmd += p
        job_idlist = []
        job_idlist.append(Submit_to_hoffman2(8, 2048, cmd, messaging="error"))
        Job_wait(job_idlist, 300)
        logj(job_idlist[0])
        logm("%s: Merging bam files ends."%self.name)

    def Step4(self):
        """Call methylation"""
        # Need to build the folder to reference genome
        logm("%s: Methylation calling starts."%self.name)
        genome_subdir = os.path.join(\
            Params['DBPATH'], '%(GENOME)s_rrbs_%(LOW_BOUND)s_%(UP_BOUND)s_bowtie2' % Params)
        bamlist = [x for x in os.listdir(self.folder) if "merged" in x]
        if len(bamlist) != 1:
            logm("%s: Methylation calling failed. Please check the number of merged bam files."%self.name)
            return True
        p = " -d %s -i %s -r %s --txt True"%(genome_subdir, os.path.join(self.folder, bamlist[0]), Params['READ_NO'])
        cmd = os.path.join(Params['BSPATH'],"bs_seeker2-call_methylation.py")
        cmd += p
        job_idlist = []
        job_idlist.append(Submit_to_hoffman2(16, 2048, cmd, messaging="error"))
        Job_wait(job_idlist, 60*60) # This part may take up to five hours
        logj(job_idlist[0])
        logm("%s: Methylation calling ends."%self.name)

from optparse import OptionParser

def main():
    # Initialization
    parser = OptionParser()
    parser.add_option("-i", "--input", type="string", dest="folder", \
                  help="Input file folder" )
    (options, args) = parser.parse_args()
    
    open_log(os.path.join(options.folder, "%s.LOG"%datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')))
    logm("==================================")
    logm("Program starts.")
    logm("==================================")
    job_log(os.path.join(options.folder, "%s.JOBLOG"%datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')))
    
    if os.path.isfile(os.path.join(options.folder,"conf.txt")):
        conf = os.path.join(folder,"conf.txt")
    elif os.path.isfile(os.path.join(os.getcwd(), "conf.txt")):
        conf = os.path.join(os.getcwd(), "conf.txt")
    else:
        print >> sys.stderr, 'ERROR: Cannot find configuration file conf.txt'
        exit(1)
    Conf_read(conf)
    
    workerlist = []
    if Params['MULTIPLEX'] != "False":
        file_list_1 = [x for x in options.folder if \
                       (x.endswith("_qseq.txt") or x.endswith("_qseq.txt.gz")) \
                       and x.split("_")[-3] == "1"]
        Submit_to_hoffman2_array(1, 1024, "Step1.py -i %s --conf %s"%(options.folder, conf), lower_index=1, higher_index=len(file_list_1), interval=1, outputdir=options.folder, messaging="error"):
        for BC in Params['BARCODES'].split(","):
            workerlist.append(Worker("BC"+BC, options.folder))
            workerlist[-1].start()
    else:
        workerlist.append(Worker(".", options_folder))
        workerlist[-1].start()
    for w in workerlist:
        w.join()
    logm("==================================")
    logm("Program ends.")
    logm("==================================")
    close_log()
    job_log_close()

if __name__ == "__main__":
    main()
