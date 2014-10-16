#!/usr/bin/env python
# Copyright (c) 2014 UCLA
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

import os, sys
import pysam
from optparse import OptionParser
from bs_tools_utils.utils import *

def main():
    parser = OptionParser()
    parser.add_option("-i", dest="inbam", type='string', help="the folder of input bam files")
    (options, args) = parser.parse_args()
    if not options.inbam:
        options.inbam = "."
    open_log(os.path.join(options.inbam, 'MyBamPostProcess.py_log'))
    logm('Program starts!')
    file_list_t = [os.path.join(options.inbam, x) for x in os.listdir(options.inbam) if x.endswith("_qseq.txt_rrbsse.bam")]
    file_list = []
    # Check log file to see if alignment is successful.
    for f in file_list_t:
        try:
            log_file = open(".".join(f.split(".")[:-1])+".bs_seeker2_log")
            for line in log_file:
                pass
            # Go to the last line
            if "END" in line:
                file_list.append(f)
                logm("File %s is included."%f)
            else:
                logm("File %s is excluded."%f)
        except:
            logm("File %s has no alignment log file."%f)
    if len(file_list) == 0:
        print >> sys.stderr, 'ERROR: no bam files available for post process.'
        exit(1)
    sorted_list = []
    # Sort
    for inputsam in file_list:
        sortedsam = inputsam + "_sorted"
        pysam.sort(inputsam, sortedsam)
        sorted_list.append(sortedsam+".bam")
    logm('Individual bam file sorting finished.')
    # Merge
    mergedsam = file_list[0].split("_")
    mergedsam[-3] = "merged"
    mergedsam = "_".join(mergedsam)
    merge_params = [mergedsam] + sorted_list
    pysam.merge(*merge_params)
    logm('Merging finished.')
    # Remove sortedsams
    for f in sorted_list:
        os.remove(f)
    close_log()

if __name__ == '__main__':
    main()
