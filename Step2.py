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
from utils import *

def Step2():
    """Align using bs-seeker2"""
    parser = OptionParser()
    parser.add_option("-i", "--input", type="string", dest="folder", \
                  help="Input file folder", default=os.getcwd() )
    parser.add_option("--conf", type="string", dest="CONFPATH")
    (options, args) = parser.parse_args()
    Params = Conf_read(options.CONFPATH)
    file_list = [x for x in os.listdir(options.folder) \
                 if x.endswith("qseq.txt") or x.endswith("qseq.txt.gz")]
    file_list.sort()
    f = file_list[int(os.environ["SGE_TASK_ID"]) - 1]
    cmd = os.path.join(Params['BSPATH'],"bs_seeker2-align.py")
    p = [cmd]
    p.extend( ("-i %s --bt-p 1"%os.path.join(options.folder, f)).split(" "))
    p.extend( ("-L %s -U %s -m %s"%(Params['LOW_BOUND'], Params['UP_BOUND'], Params['NO_MISMATCHES'])).split(" ") )
    p.extend( ("-g %s -d %s -p %s"%(Params['GENOME'], Params['DBPATH'], Params['ALIGNER_PATH'])).split(" "))
    p.extend( ["-r", "-a", os.path.join(Params['BSPATH'], "adapter.txt"), "--aligner", "bowtie2", "--bt2--end-to-end"])
    process = subprocess.Popen(" ".join(p), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    print >> sys.stdout, out

if __name__ == "__main__":
    Step2()
