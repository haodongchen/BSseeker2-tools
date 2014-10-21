BSseeker2-tools
===============

Tools to run BSseeker2 on Hoffman2 cluster.

Before running this program, make sure:

* You have BSSeeker2 installed correctly
* Genome pre-processed
* Establish a link named RRBS_submit in your ~/bin/ folder to RRBS_submit.py (You can do so by typing "ln -s /path/to/BSSeeker2-tools/RRBS_submit.py RRBS_submit", and then move RRBS_submit into ~/bin/)

To submit jobs,

* Move into data folder
* Copy conf.txt into data folder
* Change conf.txt accordingly
* Type

    job.q -t 96 -d 2048 -o $(pwd) -k RRBS_submit -i $(pwd)
