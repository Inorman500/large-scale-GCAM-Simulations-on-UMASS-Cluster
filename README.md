# large-scale GCAM Simulations on UMASS super Computer
This python script replaces the values for any number of renewable technologies in GCAM’s CSV files with your values and then converts those CSVs into XML input files. In addition, this script creates the appropriate configuration file based on what values you replaced in the CSV. 

The code works in 5 Steps:
1. The input Excel File with the necessary energy technologies and storage cost is loaded.
2. The program ask the user which energy technologies should be replaced and how many samples to produces.
3. The code than removes all other energy technologies that the user didn't want from GCAM's Csv's
4. The program replaces the values for each chosen technology in GCAM CSVs, for each sample.
5. The program creates  N amount of input folders, where N is the number of samples the user chooses

All-Samples: The folder that will hold all the input files created for each sample value

Original Copy: These are unmodified GCAM files that are kept as a reference, before modification.

folders in Original Copy: These are modified files from original copy that has just the technologies that you want to run.


Gsimulation.sh is a bash script used to run 1000 separate Simulations of GCAM in parallel on the UMass cluster(MGHPCC).


More about this research can be found in the PowerPoint presentation located in this repo.

