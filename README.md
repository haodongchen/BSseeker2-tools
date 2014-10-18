BSseeker2-tools
===============

Tools to run BSseeker2 on Hoffman2 cluster. 

To submit jobs,

* Move into data folder
* Copy conf.txt into data folder
* Change conf.txt accordingly
* Type:

    job.q -t 96 -d 2048 -o $(pwd) -k /folder/to/BSseeker2_tools/RRBS_submit.py -i $(pwd)
