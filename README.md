BSseeker2-tools
===============

Tools to run BSseeker2 on Hoffman2 cluster.

Before running this program, make sure:

* You have BSSeeker2 installed correctly
* Genome pre-processed

To submit jobs,

* Move into data folder
* Copy conf.txt into data folder
* Change conf.txt accordingly
* Type


    job.q -t 96 -d 2048 -o $(pwd) -k /folder/to/your/BSseeker2-tools/RRBS_submit -i $(pwd)
