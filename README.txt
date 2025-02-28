############
Installation
############

Clone the repo into a good directory:
git clone https://github.com/jakescally/hammr-l.git

Navigate into the repository. Create a conda (or mamba) environment from environment.yml:
conda env create -f environment.yml

Activate it:
conda activate hammrl

Install the pip requirements:
pip install -r requirements.txt

#####
Usage
#####

This project contains two user-runnable scripts that (a) run the actual deconvolution (b) provide some analysis of the results.

Located inside the /scripts/ folder, "deconvolve_dataset.py" is the script that performs the deconvolution and can be called like this:
python deconvolve_dataset.py [dataset_name.pkl] [output_dir_name] [max_iterations] [core_count]

The dataset name for the included dataset is "6-ones_9qubitBV.pkl". The name of the output directory can be whatever you want. Max iterations dictates
how many iterations of R-L the algorithm will do on a specific circuit's output before giving up. Note that there is also a tolerance (1e-4 by default)
that can be adjusted by modifying the algorithm.py file that dictates the threshold for convergence. As this is made to be run on relatively large datasets,
the algorithm is fully multiprocessed, so specify the number of cores/threads you are willing to dedicate to processing the data.

After outputs are generated to the folder name you specified, you can get some brief statistics using the analyze script:
python analyze.py [output_dir_name]
which will give the rank difference statistics. Note that a negative rank difference indicates an improvement in rank (i.e. going from 4->1, rank_diff=-3)

##############
File Structure
##############

/outputs/: directory where processed data (including plots) are outputted
/datasets/: directory where dataset pickle files are stored
/scripts/: directory containing scripts that perform the deconvolution


##############
Dataset format
##############

Datasets are stored as pickle'd up dicts that look like this:
{secret_string: counts, secret_string2: counts, ...}
Take for example the included 9-qubit Bernstein Vazirani dataset containing all BV circuits where the secret string has exactly 6 ones, in any order. This looks like:
{"111111000": {"111111010": 23, "111010110": 123, ...etc}, "111110001": [counts for this circuit], ...etc}

