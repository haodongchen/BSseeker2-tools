BSseeker2-tools
===============

Tools to run BSseeker2 on Hoffman2 cluster. 

To submit jobs, move into data folder, change conf.txt accordingly, and type:
  job.q -t 96 -d 2048 -o $(pwd) -k /folder/to/BSseeker2_tools/RRBS_submit.py -i $(pwd)
