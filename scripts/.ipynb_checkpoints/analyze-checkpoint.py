import os
import sys
from datetime import datetime
import numpy as np

def analyze_rank_differences(directory, remove_first_rankers=False, remove_bad_runs=False):
    rank_diffs = []
    wins = 0
    ties = 0
    losses = 0

    best_example = None
    best_rank_change = 100
    
    # Iterate through each folder in the directory
    for folder in os.listdir(directory):
        folder_path = os.path.join(directory, folder)
        ranks_file = os.path.join(folder_path, "ranks.txt")
        
        if os.path.isdir(folder_path) and os.path.isfile(ranks_file):
            with open(ranks_file, "r") as f:
                lines = f.readlines()
                initial_rank = None
                final_rank = None
                rank_diff = None
                
                
                for line in lines:
                    if "Initial rank:" in line:
                        try:
                            initial_rank = int(line.split(":")[-1].strip())
                        except ValueError:
                            print(f"Warning: Could not parse initial rank in {ranks_file}")
                    if "Final rank:" in line:
                        try:
                            final_rank = int(line.split(":")[-1].strip())
                        except ValueError:
                            print(f"Warning: Could not parse initial rank in {ranks_file}")
                    if "Rank diff:" in line:
                        try:
                            rank_diff = int(line.split(":")[-1].strip())
                        except ValueError:
                            print(f"Warning: Could not parse rank difference in {ranks_file}")
                            
                
                
                if rank_diff is not None and (not remove_bad_runs or (initial_rank is not None and 1 < initial_rank <= 10)):
                    if remove_first_rankers:
                        if initial_rank != 1:
                            rank_diffs.append(rank_diff)
                            if initial_rank < final_rank:
                                losses+=1
                            if initial_rank == final_rank:
                                ties+=1
                            if initial_rank > final_rank:
                                wins+=1
                    else:
                        rank_diffs.append(rank_diff)
                        if initial_rank < final_rank:
                            losses+=1
                        if initial_rank == final_rank:
                            ties+=1
                        if initial_rank > final_rank:
                            wins+=1

                    if rank_diff < best_rank_change:
                        best_rank_change = rank_diff
                        best_example = folder_path

                
    
    if not rank_diffs:
        return "No valid rank differences found."
    
    # Compute statistics
    rank_diffs = np.array(rank_diffs)
    stats = {
        "count": len(rank_diffs),
        "wins": wins,
        "ties": ties,
        "losses": losses,
        "mean": np.mean(rank_diffs),
        "std_dev": np.std(rank_diffs, ddof=1),
        "median": np.median(rank_diffs),
        "min": np.min(rank_diffs),
        "max": np.max(rank_diffs),
        "range": np.max(rank_diffs) - np.min(rank_diffs),
        #"best_example": best_example
    }

    
    
    return stats

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python analyze.py [output_directory]")
    output_directory = sys.argv[1]
    target_dir = f"../outputs/{output_directory}"
    
    print(f"Full results:\n {analyze_rank_differences(target_dir)}")
    # print(f"Removed \"bad\" runs:\n {analyze_rank_differences(remove_bad_runs=True)}")
    print(f"Removed initial first rankers:\n {analyze_rank_differences(target_dir, remove_first_rankers=True)}\n\n")