import networkx as nx
import matplotlib.pyplot as plt
import qctools
import os
from datetime import datetime


####################
# Helper Functions #
####################

def get_n_away_neighbors(G, node_name, n):
    if node_name not in G:
        raise ValueError(f"The node '{node_name}' is not found in the graph.")

    nodes_n_away = nx.single_source_shortest_path_length(G, node_name, cutoff=n)
    result = {node: G.nodes[node] for node in nodes_n_away.keys()}
    return result

##########################
# Deconvolution Function #
##########################


# Deconv function
def deconv(secret_string, shots, max_iterations, counts, dirname, save_figs=True, print_figs=False, tolerance=1e-4):
    neighbor_dist = len(secret_string)
    increment = max_iterations // 10
    n = len(secret_string)

    # create the graph
    G = nx.Graph()

    def get_rank(u_graph, secret_string):
        u = {key: data['prob'] for key, data in u_graph.nodes(data=True)}
        sorted_items = sorted(u.items(), key=lambda x: x[1], reverse=True)
        rank_dict = {key: rank + 1 for rank, (key, _) in enumerate(sorted_items)}
        return rank_dict.get(secret_string, None)
    
    # add all the nodes (vertices) first
    for key, value in counts.items():
        # each key is the result string, each value is the counts
        # so each node ID is can be the result string (key) and attribute can be the counts (value)
        G.add_node(key, prob=value) # /shots
        
    # loop through all vertices to add edges to those with a hamming distance of 1
    for result_string in G.nodes():
        # now loop through all other nodes
        for other_result_string in G.nodes():
            # connect the two if they have a hamming distance of 1
            dist = qctools.hamming_dist(result_string, other_result_string)
            if (dist == 1):
                G.add_edge(result_string, other_result_string)
    
    # initialize d
    d_graph = nx.Graph(G, deepcopy=True)
    
    # initialize u as a graph
    u_graph = nx.Graph(G, deepcopy=True)
    u_init = nx.Graph(G, deepcopy=True)

    initial_rank = get_rank(u_graph, secret_string)

    
    # Track the probability distributions for each iteration
    probability_history = []
        
    def graph(u, save_figs, iteration=1, log=False, directory=None):
        nonzero_u = {key: data['prob'] for key, data in u.nodes(data=True) if data['prob'] > 0.0001}
        sorted_keys = sorted(nonzero_u.keys())
        sorted_counts = [nonzero_u[key] for key in sorted_keys]
        colors = ['red' if key == secret_string else 'blue' for key in sorted_keys]
        plt.bar(sorted_keys, sorted_counts, color=colors)
        plt.xlabel('Binary String')
        plt.xticks(rotation=90)
        plt.ylabel('Probability')
        if log:
            plt.yscale('log')
        plt.title('Proabability Distribution for n-bit Binary Strings')
        if save_figs:
            plt.savefig(os.path.join(directory, f'full-{iteration}.png'))
        if print_figs:
            plt.show()
    
    graph(u_graph, False)
    
    def graph_top(u, save_figs, n=10, iteration=1, log=False, directory=None):
        # Filter out nodes with probability greater than 0.0001
        nonzero_u = {key: data['prob'] for key, data in u.nodes(data=True) if data['prob'] > 0.0001}
        
        # Sort by probability in descending order
        sorted_keys = sorted(nonzero_u, key=nonzero_u.get, reverse=True)
        
        # Select the top n elements
        top_keys = sorted_keys[:n]
        top_counts = [nonzero_u[key] for key in top_keys]
        colors = ['red' if key == secret_string else 'blue' for key in top_keys]
        
        # Create the bar plot for top n elements
        plt.figure(figsize=(12, 8))  # Adjust the figure size as needed
        plt.bar(top_keys, top_counts, color=colors)
        plt.xlabel('Binary String')
        plt.ylabel('Probability')
        plt.xticks(rotation=90)
        if log:
            plt.yscale('log')
        plt.title(f'Top {n} Probability Distribution for n-bit Binary Strings')
        if save_figs:
            plt.savefig(os.path.join(directory, f'top{n}-{iteration}.png'))
        if print_figs:
            plt.show()

    if save_figs:
        # Get current date and time for folder naming
        # current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        # Specify the directory for saving the plot
        results_directory = os.path.join(os.getcwd(), f"../outputs/{dirname}")
        directory = os.path.join(results_directory, secret_string)
        # Ensure the directory exists
        os.makedirs(directory, exist_ok=True)
        
    for iteration in range(max_iterations):
        if iteration == 0:
            graph(u_graph, save_figs, iteration, directory=directory)
            graph_top(u_graph, save_figs, 20, iteration, directory=directory)
        
        u_prev_graph = nx.Graph(u_graph, deepcopy=True)
        
        # calculate c. remember that c is dict of all c_i
        c = {format(index, f"0{n}b"): 0 for index in range(2**n)}
        for obs_string in d_graph.nodes:
            # compute the n-distance neighborhood of obs_string and create a new dict
            n_dist_neighbors = get_n_away_neighbors(G, obs_string, neighbor_dist)
            c[obs_string] = sum((1/((qctools.hamming_dist(obs_string, true_string)+1)))*u_graph.nodes[true_string]['prob'] for true_string in n_dist_neighbors)
            
        # these corrections will represent the stuff multiplied by the u_j (t)
        # in our case, the correction variable holds all corrective factors for all j (true strings)
        correction = {key: 0 for key in c} # initialize
        for true_string in d_graph.nodes:
            n_dist_neighbors = get_n_away_neighbors(G, true_string, neighbor_dist)
            correction[true_string] = sum((d_graph.nodes[obs_string]['prob'] / c[obs_string]) * (1/((qctools.hamming_dist(obs_string, true_string)+1))) for obs_string in n_dist_neighbors)
        
        # now actually update u
        for true_string in d_graph.nodes:
            u_graph.nodes[true_string]['prob'] = u_graph.nodes[true_string]['prob'] * correction[true_string]
        # normalize u
        total_probs = 0
        for string, data in u_graph.nodes(data=True):
            total_probs += data['prob']
    
        for string in u_graph.nodes:
            u_graph.nodes[string]['prob'] /= total_probs
        
        if (iteration + 1) % increment == 0:
            percentage = (iteration + 1) / max_iterations * 100
            print(f"{secret_string}: Iteration {iteration + 1} - {percentage:.0f}% complete")
            graph(u_graph, save_figs, iteration, directory=directory)
            graph_top(u_graph, save_figs, 20, iteration, directory=directory)
        
        if max(abs(u_graph.nodes[k]['prob'] - u_prev_graph.nodes[k]['prob']) for k in u_graph.nodes) < tolerance:
            print(f"{secret_string}: Converged.")
            graph(u_graph, save_figs, iteration, directory=directory)
            final_rank = get_rank(u_graph, secret_string)
            break
        
        if iteration == max_iterations-1:
            print(f"{secret_string}: Reached max iterations.")
            graph(u_graph, save_figs, iteration, directory=directory)
            final_rank = get_rank(u_graph, secret_string)
            break
        
        probability_history.append(u_graph)
        plt.close()
    
    rank_diff = final_rank - initial_rank
    with open(f"{results_directory}/{secret_string}/ranks.txt", "w") as file:
        file.write(f"Initial rank: {initial_rank}\n")
        file.write(f"Final rank: {final_rank}\n")
        file.write(f"Rank diff: {rank_diff}\n")

    

    






















