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

    


def Build_OT_index(tree):

    def Phase_1(tree):
        # Processing leaf and internal nodes, building OSHR tree, and collect reference internal nodes
        setattr(tree, "number_leaf_nodes", 0)
        setattr(tree, "number_internal_nodes", 0)
        setattr(tree, "M", [-1] * len(tree.word))  # List M as mentioned in the paper
        setattr(tree.root, "height", 0)
        
        maximum_h_values = 0
        sum_h_values = 0
        count_nodes_with_max_h_values = 0

        # (node, visited flag)
        nodes_stack = [(tree.root, False)]

        while nodes_stack:
            current_node, visited = nodes_stack.pop()

            if not visited:
                # Before visiting children (entry)
                nodes_stack.append((current_node, True))  # mark to process after children

                for child_node in current_node.transition_links.values():
                    nodes_stack.append((child_node, False))
                    
                    if not child_node.is_leaf():
                        setattr(child_node, "height", current_node.height + 1)
                    
            else:
                # After visiting children (exit)
                if current_node.is_leaf():
                    tree.number_leaf_nodes += 1
                    tree.M[current_node.idx] = current_node
                    
                    # compute h values
                    h = current_node.parent.height
                    sum_h_values += h                    
                    if h > maximum_h_values:
                        maximum_h_values = h
                   
                else:
                    setattr(current_node, "OT_indexes", [])
                    tree.number_internal_nodes += 1
                    
                    # build SLS
                    if current_node._suffix_link is not None and current_node != tree.root:
                        temp = current_node._suffix_link
                        if not hasattr(temp, "SLS"):
                            setattr(temp, "SLS", [])
                        temp.SLS.append(current_node)

                    # build List_of_reference_internal_nodes
                    top_node = current_node.parent._suffix_link
                    bottom_node = current_node._suffix_link.parent
                    if bottom_node != top_node:
                        temp = bottom_node
                        while temp != top_node:
                            if not hasattr(temp, "List_of_reference_internal_nodes"):
                                setattr(temp, "List_of_reference_internal_nodes", [])
                            temp.List_of_reference_internal_nodes.append(current_node)
                            temp = temp.parent



        print("Number of leaf nodes is", "{:,}".format(tree.number_leaf_nodes))
        print("Number of internal nodes is", "{:,}".format(tree.number_internal_nodes))
        print("Number of alphabets in the input data", len(tree.root.transition_links) - 1)
        print ("Maximum h value", maximum_h_values)
        print ("Average h values", int(sum_h_values/tree.number_leaf_nodes))
        print ("Sum of h values", "{:,}".format(sum_h_values))
                
        
    start = time.time()    
    Phase_1(tree)
    print ("***** Phase 1, processing leaf and internal nodes, building OSHR tree, and collect reference internal nodes finished in ", round((time.time() - start), 5), "seconds\n")
    
        
    def Phase_2(tree):
        # Finding base suffixes
        nodes_stack = [(tree.root, False)]

        cost = 0
        number_of_base_suffixes_derived_from_reference_leaf_node = 0
        number_of_base_suffixes_derived_from_reference_internal_node = 0

        while nodes_stack:
            current_node, visited = nodes_stack.pop()

            if not visited:
                # Push node back with visited flag set to True
                nodes_stack.append((current_node, True))

                # Push children in reverse order (so leftmost comes first when popped)
                for child_node in current_node.transition_links.values():
                    nodes_stack.append((child_node, False))
            else:
                # ------ alongside processing after visiting children ------
                if current_node.is_leaf():
                    if current_node.idx + 1 < tree.number_leaf_nodes:
                        # compute base suffixes derived from reference leaf nodes
                        leaf_node_of_next_suffix_index = tree.M[current_node.idx + 1]
                        if leaf_node_of_next_suffix_index.parent != current_node.parent._suffix_link:
                            bottom_node = leaf_node_of_next_suffix_index.parent
                            top_node = current_node.parent._suffix_link

                            while True:
                                if bottom_node == top_node:
                                    if current_node.parent == tree.root:  # special root case
                                        if not hasattr(bottom_node, "List_of_base_suffixes"):
                                            setattr(bottom_node, "List_of_base_suffixes", [])
                                        bottom_node.List_of_base_suffixes.append(leaf_node_of_next_suffix_index.idx + bottom_node.depth)
                                        number_of_base_suffixes_derived_from_reference_leaf_node += 1
                                    break
                                else:
                                    if not hasattr(bottom_node, "List_of_base_suffixes"):
                                        setattr(bottom_node, "List_of_base_suffixes", [])
                                    bottom_node.List_of_base_suffixes.append(leaf_node_of_next_suffix_index.idx + bottom_node.depth)
                                    number_of_base_suffixes_derived_from_reference_leaf_node += 1
                                    bottom_node = bottom_node.parent

                else:
                    # collect base suffixes derived from reference internal nodes if any
                    if hasattr(current_node, "List_of_reference_internal_nodes"):
                        for reference_internal_node in current_node.List_of_reference_internal_nodes:
                            for leaf_node in get_leaf_nodes(tree, reference_internal_node):
                                if not hasattr(current_node, "List_of_base_suffixes"):
                                    setattr(current_node, "List_of_base_suffixes", [])

                                leaf_node_index = leaf_node.idx
                                current_node.List_of_base_suffixes.append(leaf_node_index + 1 + current_node.depth)
                                number_of_base_suffixes_derived_from_reference_internal_node += 1
                                cost += 1

        # compute the case for suffix 0 as there is no previous index for index 0
        bottom_node = tree.M[0].parent
        while bottom_node != tree.root:
            if not hasattr(bottom_node, "List_of_base_suffixes"):
                setattr(bottom_node, "List_of_base_suffixes", [])
            bottom_node.List_of_base_suffixes.append(0 + bottom_node.depth)
            number_of_base_suffixes_derived_from_reference_leaf_node += 1
            cost += 1
            bottom_node = bottom_node.parent

        # special root-case checks
        current_node = tree.root
        for node in current_node.transition_links.values():
            if node.is_leaf():
                if node.idx + 1 < tree.number_leaf_nodes:
                    leaf_node_of_next_suffix_index = tree.M[node.idx + 1]
                    if leaf_node_of_next_suffix_index.parent == tree.root:
                        if not hasattr(current_node, "List_of_base_suffixes"):
                            setattr(current_node, "List_of_base_suffixes", [])
                        current_node.List_of_base_suffixes.append(leaf_node_of_next_suffix_index.idx)
                        cost += 1
            else:
                if node._suffix_link != tree.root:
                    for leaf_node in get_leaf_nodes(tree, node):
                        if not hasattr(current_node, "List_of_base_suffixes"):
                            setattr(current_node, "List_of_base_suffixes", [])
                        leaf_node_index = leaf_node.idx
                        current_node.List_of_base_suffixes.append(leaf_node_index + 1)
                        cost += 1



        print("Finding base suffixes costed", "{:,}".format(cost))
        print("Number_of_base_suffixes_derived_from_reference_leaf_node", "{:,}".format(number_of_base_suffixes_derived_from_reference_leaf_node))
        print("Number_of_base_suffixes_derived_from_reference_internal_node", "{:,}".format(number_of_base_suffixes_derived_from_reference_internal_node))
        print("Total number of base suffixes (except root node)", "{:,}".format(number_of_base_suffixes_derived_from_reference_leaf_node + number_of_base_suffixes_derived_from_reference_internal_node))

    start = time.time()  
    Phase_2(tree)
    print ("***** Phase 2, finding base suffixes, finished in", round((time.time() - start), 5), "seconds\n")


    def Phase_3(tree):
        # OH mapping base paths and building OT index based on base suffixes.
        
        OT_index_counter = 0
        Sum_of_OT_indexes = 0
        minimum_pattern_length = int(sys.argv[2])
        minimum_depth_for_OH_mapping = 0
        
        nodes_stack = [(tree.root, False)]  # (node, visited_flag)
        while nodes_stack:
            current_node, visited = nodes_stack.pop()
            
            if not visited:
                # -------- BEFORE visiting children --------
                current_node.left_OT_index = OT_index_counter

                # Push "after children" marker
                nodes_stack.append((current_node, True))

                # Push children if any
                if hasattr(current_node, "SLS"):
                    for child_node in current_node.SLS:
                        nodes_stack.append((child_node, False))
                
            else:
                # -------- AFTER visiting children --------
                OT_index_counter += 1

                # Process base suffixes
                if current_node != tree.root and hasattr(current_node, "List_of_base_suffixes"):
                    expected_minimum_depth = current_node.depth + minimum_pattern_length
                    temp = defaultdict(int)

                    for base_suffix in current_node.List_of_base_suffixes:
                        if base_suffix >= tree.number_leaf_nodes:
                            continue

                        suffix_idx_of_base_leaf_node = base_suffix - current_node.depth
                        base_leaf_node = tree.M[suffix_idx_of_base_leaf_node]

                        node = base_leaf_node.parent
                        temp[node] += 1

                        while node.depth >= expected_minimum_depth:
                            if temp[node] == len(node.transition_links):
                                temp[node.parent] += 1
                            else:
                                break
                            node = node.parent

                        minimum_depth_for_OH_mapping = node.depth - current_node.depth
                        if minimum_depth_for_OH_mapping < minimum_pattern_length:
                            minimum_depth_for_OH_mapping = minimum_pattern_length - 1

                        # Assign OT indexes upwards
                        last_extent_leaf_node = tree.M[base_suffix]
                        node = last_extent_leaf_node.parent
                        while node.depth > minimum_depth_for_OH_mapping:
                            node.OT_indexes.append((OT_index_counter, base_suffix))
                            OT_index_counter += 1
                            Sum_of_OT_indexes += 1
                            node = node.parent

                    temp.clear()

                # Set right_OT_index at exit
                current_node.right_OT_index = OT_index_counter

        # Reporting
        print("Left and right OT index of root for OSHR nodes:", 
              tree.root.left_OT_index + 1, "{:,}".format(tree.root.right_OT_index))
        print("Sum_of_OT_indexes", "{:,}".format(Sum_of_OT_indexes))



        
    start = time.time()
    Phase_3(tree)
    print ("***** Phase 3, OH mapping base paths, finished in", round((time.time() - start), 5), "seconds\n")

    

   
######################################################################################## Searching code ##############################################################################################################
    
def get_leaf_nodes(tree, node):
    results = []
    nodes_stack = [(node, False)]  # (node, visited_flag)

    while nodes_stack:
        current_node, visited = nodes_stack.pop()

        if not visited:
            # Push the node again, marked as visited (after children)
            nodes_stack.append((current_node, True))

            # Push children in reverse sorted order to process left → right

            for child_node in current_node.transition_links.values():
                nodes_stack.append((child_node, False))
        else:
            # After children: collect leaf nodes
            if current_node.is_leaf():
                results.append(current_node)

    return results
 


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




    
    
    
def find_end_node_of_exact_match_starting_from_root_node(tree, string):          
    current_visited_node = tree.root
    end_node = tree.root
    i = 0
    l = len(string)
    f = True
    
    while f:
        if i <= l - 1:
            if string[i] in current_visited_node.transition_links:
                end_node = current_visited_node.transition_links[string[i]]
                if end_node.depth >= l:
                    edge_label = tree.word[end_node.idx + current_visited_node.depth:end_node.idx + l]
                else:
                    edge_label = tree.word[end_node.idx + current_visited_node.depth:end_node.idx + end_node.depth]
                
                current_visited_node = end_node
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
            


def start():
    
    print ("------------------------------------------------------------------------------------------")
    start = time.time()   
    Build_suffix_tree()
    print ("Building suffix tree took", round((time.time() - start), 5), "seconds")   
    
    
    print ("------------------------------------------------------------------------------------------")
    start = time.time()
    Build_OT_index(tree)
    print ("Building OT index using base suffixes took", round((time.time() - start), 5), "seconds")
    
    
    
    
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
                        pos = bisect.bisect(end_node_of_pattern_from_root.OT_indexes, (starting_node.left_OT_index, ""))
                        if pos < len(end_node_of_pattern_from_root.OT_indexes):
                            if end_node_of_pattern_from_root.OT_indexes[pos][0] < starting_node.right_OT_index:
                                matching_node = tree.M[end_node_of_pattern_from_root.OT_indexes[pos][1] - starting_node.depth]
                                required_depth = starting_node.depth + end_node_of_pattern_from_root.depth
                                while matching_node.parent.depth >= required_depth: 
                                    matching_node = matching_node.parent
                                print ("Found matching node", starting_node, matching_node) #print ("Found matching node", matching_node, "for", pattern, "under node", starting_node)
                            else:
                                print ("No matching node found") 
                        else:
                            print ("No matching node found") 
                    else:       
                        print ("No matching node found") 
                
                            

            print ("Total time for searching for", len(patterns), "patterns of length", pattern_length, "starting from", Number_of_starting_nodes, "nodes out of ", len(tree.nodes_by_depth_dict[depth]), "nodes at depth", depth, "is", round((time.time() - start), 5), "seconds") 
                
        print ("Total time for searching for", number_of_patterns_ends_at_internal_node, "of all lengths starting from", Number_of_starting_nodes, "nodes out of ", len(tree.nodes_by_depth_dict[depth]), "nodes at depth", depth, "is", round(time.time() - start_time_for_searching_all_patterns_of_all_lengths, 5), "seconds")
        print ()
           
start()
