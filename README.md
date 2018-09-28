# large-scale GCAM Simulations on UMASS super Computer

This python script Replaces the values for any number of renewable technologies in GCAM’s CSV files with your values and then converts those CSVs into XML input files. In addition, this script creates the appropriate configuration file based on what values you replaced in the CSV. 


All-Samples: The samples that will be placed on the cluster. Paste the entire folder onto the cluster
The code automatically create the all sample files. These are GCAM input files.

Original Copy: These are unmodified GCAM files that are kept as a reference, before modification.

folders in Original Copy: These are modied files from original copy that has just the technologies that you want to run



Gsimulation.sh is a bash script used to run 1000 separate Simulations of GCAM in parallel on the UMASS cluster.

More about this reserach can be found in the powerpoint presentation located in this repo.

