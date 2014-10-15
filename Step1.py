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

import os, sys, subprocess
from optparse import OptionParser
global Params
Params={}

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

def Step1():
    # Demultiplex
    parser = OptionParser()
    parser.add_option("-i", "--input", type="string", dest="folder", \
                  help="Input file folder", default=os.getcwd() )
    parser.add_option("--conf", type="string", dest="CONFPATH")
    (options, args) = parser.parse_args()
    Conf_read(options.CONFPATH)
    if Params['MULTIPLEX'] != "False":
        Params['BARCODES'] = ','.join([str(int(x)) for x in Params['BARCODES'].split(",")])
        file_list_1 = [x for x in options.folder if \
                       (x.endswith("_qseq.txt") or x.endswith("_qseq.txt.gz")) \
                       and x.split("_")[-3] == "1"]
        file_list_1.sort()
        f1 = file_list_1[int(os.environ["$SGE_TASK_ID"]) - 1]
        f1name = f1.split("_")
        f1name[-3] = "2"
        f2 = "_".join(f1name)
        p = '-I %s -s %s -b %s -l %s -m %s'%(os.getcwd(), f1, f2, Params['BARCODES'], Params['BCMISMATCH'])
        cmd = [os.path.join(Params['BSPATH'],"MyDemultiplex.py")]
        cmd.extend(p.split(" "))
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        print >> sys.stdout, out

if __name__ == "__main__":
    Step1()
