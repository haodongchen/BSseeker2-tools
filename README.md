BSseeker2-tools
===============

Tools to run BSseeker2 on Hoffman2 cluster. 

RRBS_submit.py
---------------

The master code that calls MyDemultiplex.py first, and then BS-Seeker2, and then MyBamPostProcess.py. 

Use the following code to queue it in hoffman2.

    job.q -t 96 -d 2048 RRBS_submit.py

conf.txt
---------------

This file contains parameters that will be used by RRBS_submit.py. 

Change this file accordingly before running RRBS_submit.py.

MyDemultiplex.py
---------------

If RRBS reads were multiplexed, this module will be called to de-multiplex the reads.

MyBamPostProcess.py
---------------

After BS-Seeker2 alignment, RRBS_submit.py will use this module to merge all the bam files generated by BS-Seeker2 for each Barcoded sample, and runs BS-Seeker2 to call methylation levels.