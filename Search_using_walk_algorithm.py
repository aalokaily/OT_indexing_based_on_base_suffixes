from suffix_trees import STree 
from collections import defaultdict
import time
import math 
import sys
import bisect
 
def Build_suffix_tree(): 
    global tree
    
    input_file = sys.argv[1]    
    text = ""
    with open(input_file) as file_in:        
        for line in file_in:
            if line[0] != ">":
                text += line.strip()
    
    tree = STree.STree(text)

    
    
def process_leaf_and_internal_nodes(tree):    
      
    setattr(tree, "number_leaf_nodes", 0)
    setattr(tree, "number_internal_nodes", 0)
    setattr(tree, "M", [-1] * len(tree.word)) # List M in the paper
        
    nodes_stack = [(tree.root, False)]

    while nodes_stack:
        current_node, visited = nodes_stack.pop()

        if not visited:
            # Before visiting children (entry)
            nodes_stack.append((current_node, True))  # mark to process after children
            for child_node in current_node.transition_links.values():
                nodes_stack.append((child_node, False))
                                      
        else:
            setattr(current_node, "OT_indexes", [])
            # alongside processing
            if current_node.is_leaf():
                # Assigning leaf nodes unique keys
                current_node.index_of_leaf_in_ST = tree.number_leaf_nodes                     
                tree.number_leaf_nodes += 1
                
                # creating auxiliary lists 
                tree.M[current_node.idx] = current_node
                
                if not hasattr(current_node.parent, "index_of_leftmost_leaf_in_ST"):
                    setattr(current_node.parent, "index_of_leftmost_leaf_in_ST", current_node.index_of_leaf_in_ST)
                elif current_node.index_of_leaf_in_ST < current_node.parent.index_of_leftmost_leaf_in_ST:
                    current_node.parent.index_of_leftmost_leaf_in_ST = current_node.index_of_leaf_in_ST
                if not hasattr(current_node.parent, "index_of_rightmost_leaf_in_ST"):
                    setattr(current_node.parent, "index_of_rightmost_leaf_in_ST", current_node.index_of_leaf_in_ST)
                elif current_node.index_of_leaf_in_ST > current_node.parent.index_of_rightmost_leaf_in_ST:
                    current_node.parent.index_of_rightmost_leaf_in_ST = current_node.index_of_leaf_in_ST
                    
                    
            else:
                tree.number_internal_nodes += 1
                if not hasattr(current_node.parent, "index_of_leftmost_leaf_in_ST"):
                    setattr(current_node.parent, "index_of_leftmost_leaf_in_ST", current_node.index_of_leftmost_leaf_in_ST)
                elif current_node.index_of_leftmost_leaf_in_ST < current_node.parent.index_of_leftmost_leaf_in_ST:
                    current_node.parent.index_of_leftmost_leaf_in_ST = current_node.index_of_leftmost_leaf_in_ST
                if not hasattr(current_node.parent, "index_of_rightmost_leaf_in_ST"):
                    setattr(current_node.parent, "index_of_rightmost_leaf_in_ST", current_node.index_of_rightmost_leaf_in_ST)
                elif current_node.index_of_rightmost_leaf_in_ST > current_node.parent.index_of_rightmost_leaf_in_ST:
                    current_node.parent.index_of_rightmost_leaf_in_ST = current_node.index_of_rightmost_leaf_in_ST
            
            
            
    print ("Number of leaf nodes is", "{:,}".format(tree.number_leaf_nodes))
    print ("Number of internal nodes is", "{:,}".format(tree.number_internal_nodes))
    print ("Number of alphabets in the input data", len(tree.root.transition_links) - 1)
    

    
    
  
######################################################################################## Searching code ##############################################################################################################
   
def find_end_node_of_exact_path_of_string_starting_from_a_node(tree, string, starting_node, suffix_end_node):          
    current_node = starting_node
    end_node = starting_node
    i = 0
    l = len(string)
    d = starting_node.depth
    f = True
    
    while f:
        if i <= l - 1:
            if string[i] in current_node.transition_links:
                end_node = current_node.transition_links[string[i]]
                if end_node.is_leaf():
                    suffix_number_under_node = tree.M[end_node.idx + starting_node.depth]
                    if suffix_end_node.index_of_leftmost_leaf_in_ST <= suffix_number_under_node.index_of_leaf_in_ST <= suffix_number_under_node.index_of_leaf_in_ST <= suffix_end_node.index_of_rightmost_leaf_in_ST:
                            return end_node
                    else:
                        return end_node.parent
                            
                else:
                    if end_node.depth - current_node.depth == 1:
                        current_node = end_node
                        i += 1
                    else:
                        if end_node.depth >= d + l:
                            edge_label = tree.word[end_node.idx + current_node.depth:end_node.idx + l + d]
                        else:
                            edge_label = tree.word[end_node.idx + current_node.depth:end_node.idx + end_node.depth]
                        
                        current_node = end_node
                        for char in edge_label:
                            if string[i] == char:
                                i += 1
                            else:
                                f = False
                                break
            else:
                f = False
                break
        else:
            f = False
            break
            
    
    if i == l:
        return end_node
    else:#i must be then less than l
        if end_node.depth - starting_node.depth == i:     
            return end_node
        else:
            return end_node.parent
    
    
def find_end_node_of_exact_match_starting_from_root_node(tree, string):          
    current_node = tree.root
    end_node = tree.root
    i = 0
    l = len(string)
    f = True
    
    while f:
        if i <= l - 1:
            if string[i] in current_node.transition_links:
                end_node = current_node.transition_links[string[i]]
                if end_node.depth >= l:
                    edge_label = tree.word[end_node.idx + current_node.depth:end_node.idx + l]
                else:
                    edge_label = tree.word[end_node.idx + current_node.depth:end_node.idx + end_node.depth]
                
                current_node = end_node
                for char in edge_label:
                    if string[i] == char:
                        i += 1
                    else:
                        f = False
                        break
            else:
                f = False
                break
        else:
            f = False
            break
            
    
    if i == l:
        return end_node
    else:#i must be then less than l
        if end_node.depth == i:     
            return end_node
        else:
            return end_node.parent
            
 
 
def get_internal_nodes(tree, node, depth):
    # Each stack entry: (node, visited_flag)
    nodes_stack = [(node, False)]

    while nodes_stack:
        current_node, visited = nodes_stack.pop()

        if not visited:
            # Push node back as visited
            nodes_stack.append((current_node, True))

            # Push children in arbitrary order (no sorting)
            for child_node in current_node.transition_links.values():
                nodes_stack.append((child_node, False))
        else:
            # After all children are processed
            if not current_node.is_leaf() and current_node.depth <= depth:
                tree.nodes_by_depth_dict[current_node.depth].append(current_node)





def start():
    
    print ("------------------------------------------------------------------------------------------")
    start = time.time()   
    Build_suffix_tree()
    print ("Building suffix tree took", round((time.time() - start), 5), "seconds")   
    
    
    print ("------------------------------------------------------------------------------------------")
    start = time.time()
    process_leaf_and_internal_nodes(tree)
    print ("Processing leaf and internal nodes took", round((time.time() - start), 5), "seconds")
    
    
    
    
    print ("--------------------------------------------------------------------------------------------------------------------")    
    print ("Benchmarking process")
    print ("--------------------------------------------------------------------------------------------------------------------")
    
    setattr(tree, "nodes_by_depth_dict", defaultdict(list))
    max_depth_of_tested_nodes = 20      
    get_internal_nodes(tree, tree.root, max_depth_of_tested_nodes)
    
    patterns_dict = defaultdict(list)
    number_of_patterns_ends_at_internal_node = 0
    for pattern_length in [7, 10, 12, 15, 20, 25, 30, 35, 40, 50]:
        number_of_patterns = 0
        i = 0
        while True:
            i += 1
            nn = i * pattern_length
            if nn + pattern_length >= tree.number_leaf_nodes:
                break
            else:
                t = tree.word[nn:nn + pattern_length]
                end_node_of_pattern_from_root = find_end_node_of_exact_match_starting_from_root_node(tree, t)
                if end_node_of_pattern_from_root.is_leaf():
                    continue
                else:
                    number_of_patterns_ends_at_internal_node += 1
                    patterns_dict[pattern_length].append((t, end_node_of_pattern_from_root))
                    number_of_patterns += 1
                    if number_of_patterns == 1000:
                        break
    
    for depth in range(1, max_depth_of_tested_nodes + 1):
        start_time_for_searching_all_patterns_of_all_lengths = time.time()
        list_of_starting_nodes = tree.nodes_by_depth_dict[depth][-1000:]
        Number_of_starting_nodes = len(list_of_starting_nodes)
        
                           
        
        for pattern_length in sorted(patterns_dict.keys()):
            patterns = patterns_dict[pattern_length]
            start = time.time()
            for dat in patterns:
                pattern = dat[0]
                end_node_of_pattern_from_root = dat[1]
                
                for starting_node in list_of_starting_nodes: # the last node is the root node so it was excluded
                    if pattern[0] in starting_node.transition_links:
                        matching_node = find_end_node_of_exact_path_of_string_starting_from_a_node(tree, pattern, starting_node, end_node_of_pattern_from_root)
                        if matching_node.depth >= starting_node.depth + pattern_length:
                            print ("Found matching node", starting_node, matching_node)
                        else:
                            print ("No matching node found") 
                    else:
                        print ("No matching node found") 
                
                            

            print ("Total time for searching for", len(patterns), "patterns of length", pattern_length, "starting from", Number_of_starting_nodes, "nodes out of ", len(tree.nodes_by_depth_dict[depth]), "nodes at depth", depth, "is", round((time.time() - start), 5), "seconds") 
                
        print ("Total time for searching for", number_of_patterns_ends_at_internal_node, "of all lengths starting from", Number_of_starting_nodes, "nodes out of ", len(tree.nodes_by_depth_dict[depth]), "nodes at depth", depth, "is", round(time.time() - start_time_for_searching_all_patterns_of_all_lengths, 5), "seconds")
        print ()
           
start()