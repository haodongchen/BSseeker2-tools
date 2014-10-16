import datetime, subprocess, sys

def open_log(fname):
    open_log.logfile = open(fname, 'w', 1)

def logm(message):
    log_message = "[%s] %s\n" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message)
    print log_message,
    open_log.logfile.write(log_message)

def close_log():
    open_log.logfile.close()

def job_log(fname):
    job_log.logfile = open(fname,'w',1)

def logj(job_id):
    #MY_LOCK.acquire()
    cmd = "qacct -j %s"%(str(job_id))
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    log_message = "%s\n" % (out)
    job_log.logfile.write(log_message)
    #MY_LOCK.release()

def job_log_close():
    job_log.logfile.close()

def Conf_read(conf_path):
    Params = {}
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
    return Params

