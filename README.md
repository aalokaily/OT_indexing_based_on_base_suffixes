#A Novel Nonlinear Index for Logarithmic Search Time for Any String under Any Internal Node in Suffix Trees
Suffix trees are key and efficient data structures for solving string problems. A suffix tree is a compressed trie containing all the suffixes of a given string of length $n$, constructed in linear time. In this work, we introduce an algorithm to build a nonlinear index that enables finding any string of any length under any internal node in a suffix tree in $O(\log_2 n)$ time.

------------------------------------------------------------- Prerequisite ---------------------------------------------------------------
* Install bisect library from https://docs.python.org/3/library/bisect.html 

* Install the following library that will be used to build suffix trees:
https://github.com/ptrus/suffix-trees 

Then edit ./suffix_trees/STree.py as the followings:

- comment the following line, line 249, by inserting the character "#" at the beginning of the line. This will allow setting attributes to the suffix tree more freely.
```python
__slots__ = ['_suffix_link', 'transition_links', 'idx', 'depth', 'parent', 'generalized_idxs']
```

- In some procedures, we hashed internal nodes of suffix tree, to optimize this hashing we used only the combination of node index and node depth to identify uniquely an internal node instead of the original identification/naming of the nodes given by the library which is a bit long (shorter identification will use less space and speed up the lookup process for the hashed nodes). So replace the following two lines (which are line 264 and 265) 
```python
return ("SNode: idx:" + str(self.idx) + " depth:" + str(self.depth) +
                " transitons:" + str(list(self.transition_links.keys())))
```
with the line:
```python
return (str(self.idx) + "-" + str(self.depth))
```

------------------------------------------------------------- Preparation ----------------------------------------------------------------

Firstly, you need to convert the genome in fasta format to a one-line genome. This converting removes any non A, C, G, T, and N (case is sensitive) and headers from the FASTA file. This can be done using the script filter_DNA_file_to_4_bases_and_N.py by running the command:

```python
python3 convert_fasta_file_to_one_line_file $file.fasta > converted_fasta_file.oneline
```
----------------------------------------------------------- Running algorithms -----------------------------------------------------------

The input for the tools is the converted fasta file. What strings are searched for is described at ....

Using the walk process:

```python
python3 Search_by_walk.py converted_fasta_file.oneline
```

Sample Output
```python
==============================================
Length of string --------  23
Reading input data took 0.08015 seconds
------------------------------------------------------------------------------------------
Length_threshold --------  0
Building Suffix Tree took 82.86689 seconds
------------------------------------------------------------------------------------------
Number of leaf nodes is 5,690,749
Number of internal nodes is 3,849,880
Number of alphabets in the input data 4
Processing leaf and internal nodes finished in  65.63165 seconds
------------------------------------------------------------------------------------------
Testing index
Found matching node 74855-8
Found matching node 50634-8
Found matching node 132550-8
Found matching node 69-8
Found matching node 2203-8
Found matching node 139-8
Found matching node 93859-8
Found matching node 12214-8
Found matching node 156214-8
Found matching node 95250-8
Found matching node 227973-8
Found matching node 209-8
Found matching node 6011-8
Found matching node 7896-8
Found matching node 12407-8
```

Using OT index:
```python
python3 Search_using_OT_index_based_on_base_suffixes_trivial.py converted_fasta_file.oneline MPA
```

Sample Output
```python
==============================================
Length of string --------  23
Reading input data took 0.03905 seconds
------------------------------------------------------------------------------------------
Length_threshold --------  0
Building Suffix Tree took 85.04601 seconds
------------------------------------------------------------------------------------------
Number of leaf nodes is 5,690,749
Number of internal nodes is 3,849,880
Number of alphabets in the input data 4
Leftmost and rightmost keys of leaf nodes in ST of root node (0, '5,690,748')
Processing leaf and internal nodes finished in  94.42541 seconds

------------------------------------------------------------------------------------------
Finding base suffixes took time of 1,564,169
Number_of_base_suffixes_derived_from_reference_leaf_node 4,126,593
Number_of_base_suffixes_derived_from_reference_internal_node 1,564,156
Total number of base suffixes 5,690,749
***** Phase 1 finished in 37.27152 seconds

Number of OSHR leaf_nodes is 1,353,289
Number of OSHR internal nodes is 2,496,591
Number of base nodes for Hanadi nodes 1,083,373
Number of base nodes for Srivastava nodes 318,211

min_size_of_List_of_base_suffixes_derived_from_reference_leaf_nodes 1
max_size_of_List_of_base_suffixes_derived_from_reference_leaf_nodes 4
total_size_of_List_of_base_suffixes_derived_from_reference_leaf_nodes 4,126,593

min_size_of_List_of_base_suffixes_derived_from_reference_internal_nodes 1
max_size_of_List_of_base_suffixes_derived_from_reference_internal_nodes 100
total_size_of_List_of_base_suffixes_derived_from_reference_internal_nodes 1,564,156

sum_of_unique_inbetween_nodes_between_internal_nodes 0
min_length_of_List_of_reference_internal_nodess 1
max_length_of_List_of_reference_internal_nodess 4

Number of OSHR internal nodes with empty List_of_base_suffixes_derived_from_reference_leaf_nodes and empty List_of_base_suffixes_derived_from_reference_internal_nodes (must be covered earlier by one of the three indexes) 1,225,538
Number of OSHR internal nodes with empty List_of_base_suffixes_derived_from_reference_leaf_nodes and unempty List_of_base_suffixes_derived_from_reference_internal_nodes (covered by indexing the label between the refrence-internal-node (of this node) and the parent of the reference node) 180,437
Number of OSHR internal nodes with unempty List_of_base_suffixes_derived_from_reference_leaf_nodes and empty List_of_base_suffixes_derived_from_reference_internal_nodes (Hanadi node) 934,580
Number of OSHR internal nodes with unempty List_of_base_suffixes_derived_from_reference_leaf_nodes and unempty List_of_base_suffixes_derived_from_reference_internal_nodes (Hanadi node) 156,036

Number of OSHR leaf nodes with empty List_of_base_suffixes_derived_from_reference_leaf_nodes and empty List_of_base_suffixes_derived_from_reference_internal_nodes (bottom_base_node of base path) 0
Number of OSHR leaf nodes with empty List_of_base_suffixes_derived_from_reference_leaf_nodes and unempty List_of_base_suffixes_derived_from_reference_internal_nodes (covered by indexing the label between the refrence-internal-node (of this node) and the parent of the reference node) 10,106
Number of OSHR leaf nodes with unempty List_of_base_suffixes_derived_from_reference_leaf_nodes and empty List_of_base_suffixes_derived_from_reference_internal_nodes (bottom_base_node of base path) 1,093,710
Number of OSHR leaf nodes with unempty List_of_base_suffixes_derived_from_reference_leaf_nodes and unempty List_of_base_suffixes_derived_from_reference_internal_nodes (Srivastava node) 249,473
***** Phase 2 finished in 70.12932 seconds

Number of OSHR leaf bottom base nodes for OSHR internal top base nodes 15,331,333
Number of OSHR internal bottom base nodes for OSHR internal top base nodes 394,686
Number of OSHR leaf bottom base nodes for OSHR leaf top base nodes 190,644
Number of OSHR internal bottom base nodes for OSHR leaf top base nodes 361,299

Left and right OT index of root for OSHR nodes 0 20,937,405
Time_cost_for_collecting_base_paths 23,707,915
Number_of_collected_base_paths 13,237,646
Time_cost_for_collecting_paths_using_for_Hanadi_nodes 28,257,418
Number_of_collected_paths_using_Hanadi_nodes 15,987,028
Time_cost_for_collecting_paths_using_for_Srivatava_nodes 7,591,521
Number_of_collected_paths_using_Srivastava_nodes 3,910,693
***** Phase 3 finished in 502.91064 seconds

Number of OSHR leaf bottom base nodes for OSHR internal top base nodes 15,331,333
Number of OSHR internal bottom base nodes for OSHR internal top base nodes 394,686
Number of OSHR leaf bottom base nodes for OSHR leaf top base nodes 190,644
Number of OSHR internal bottom base nodes for OSHR leaf top base nodes 361,299

Left and right OT index of root for OSHR nodes 0 20,937,405
Time_cost_for_collecting_base_paths 23,707,915
Number_of_collected_base_paths 13,237,646
Time_cost_for_collecting_paths_using_for_Hanadi_nodes 28,257,418
Number_of_collected_paths_using_Hanadi_nodes 15,987,028
Time_cost_for_collecting_paths_using_for_Srivatava_nodes 7,591,521
Number_of_collected_paths_using_Srivastava_nodes 3,910,693
***** Phase 3 finished in 494.43741 seconds

Sum_of_base_paths_indexes 20,757,070
Sum_of_Hanadi_nodes_indexes 16,959,305
Sum_of_Srivastava_nodes_indexes 4,539,219
*** Total sum of mapping OT indexes of all three indexes to the last extent path (the one starting from root node) 42,255,594
***** Phase 4 finished in 274.16973 seconds

***** Phase 5 finished in 62.9721 seconds

Building OT index using base paths took 1441.89089 seconds
------------------------------------------------------------------------------------------
Testing index
Found matching node 74855-8
Found matching node 50634-8
Found matching node 132550-8
Found matching node 69-8
Found matching node 2203-8
Found matching node 139-8
Found matching node 93859-8
Found matching node 12214-8
Found matching node 156214-8
Found matching node 95250-8
Found matching node 227973-8
Found matching node 209-8
Found matching node 6011-8
```
