#!/bin/bash
#BSUB -J "Gcam-[1-1000]"
#BSUB -n 1
#BSUB -W 8:00
#BSUB -R rusage[mem=21504]
#BSUB -q long
#BSUB -R "span[hosts=1]"
./gcam.exe -C/home/user/gcam/4.4/gcam-core/input/All-Samples/Sample-$LSB_JOBINDEX/configuration.xml
