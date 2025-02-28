import algorithm
import multiprocessing
import pickle
import sys
from qiskit_ibm_runtime import QiskitRuntimeService

def process_secret_string(args):
    secret_string, counts, shots, max_iterations, dirname = args
    algorithm.deconv(secret_string, shots, max_iterations, counts, dirname)
    print(f"Secret string {secret_string} completed")

if __name__ == "__main__":
    # usage: python3 deconvolve_dataset.py dataset_name.pkl core_count
    if len(sys.argv) < 5:
        sys.exit("Usage: python deconvolve_dataset.py [dataset_name.pkl] [output_dir_name] [max_iterations] [core_count]")
    dataset_name = sys.argv[1]
    output_dir_name = sys.argv[2]
    max_iterations = int(sys.argv[3])
    core_count = int(sys.argv[4])

    # load the pickle'd up dataset
    with open(f"../datasets/{dataset_name}", "rb") as f:
        # the dataset should be a dictionary like this: {secret_string: counts (result[i].data.c.get_counts()), ...}
        dataset = pickle.load(f)

    print(f"Loaded job results. Total Circuits: {len(dataset.keys())}")

    # get the counts from one of the circuits (should be the same for all)
    _, test_set = next(iter(dataset.items()))
    shots = 0
    for string in test_set.keys():
        shots += test_set[string]
    print(f"Shots: {shots}")
    
    with multiprocessing.Pool(core_count) as pool:
        pool.map(process_secret_string, [(k, v, shots, max_iterations, output_dir_name) for k, v in dataset.items()])