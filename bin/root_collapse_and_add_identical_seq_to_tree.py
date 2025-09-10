import click
from typing import Dict, List
from ete3 import Tree

def read_input_mapping(plik:str) -> Dict[str, List[str]]:
    out_dict = {}
    with open(plik) as f:
        for line in f:
            line = line.strip().split(",")
            out_dict[line[0]] = line[1:]
    return out_dict


def root_tree(tree_file:str, prefix:str) -> str:
    """Roots a tree at its midpoint and writes the result to a new file."""
    tree = Tree(tree_file, format=2)  # fromat 2 is important to read proper support values
    tree.set_outgroup(tree.get_midpoint_outgroup())
    out_file = prefix + '_rooted.nwk'
    tree.write(outfile=out_file, format=2)
    return out_file

def collapse_weak_nodes(tree_file:str, prefix:str, support_threshold=70) -> str:
    """Collapses two nodes into single node if their support is belowe threshold"""
    tree = Tree(tree_file, format=2)

    for node in tree.traverse("postorder"):
        if node.is_leaf():
            continue
        # If support is below threshold collapse nodes
        if node.support < support_threshold:
            node.delete(prevent_nondicotomic=False)
    out_file = prefix + "_collapsed.nwk"
    tree.write(outfile=out_file, format=2)
    return out_file



def reintroduce_identical_sequences(tree_file: str, input_mapping:str, prefix:str) -> str:
    """Reintroduce identical sequences that were not used during tree calculation"""
    identical_sequences = read_input_mapping(input_mapping)
    tree = Tree(tree_file, format=2)

    for klucz, sequences in identical_sequences.items():
        target_node = tree.search_nodes(name=klucz)
        if not target_node:
            print(f"Warning: Node '{klucz}' not found in tree.")
            continue
        target_node = target_node[0]
        parent = target_node.up

        if not parent:
            print(f"Warning: Node '{klucz}' has no parent (might be root)")
            continue

        for sequence in sequences:
            new_leaf = parent.add_child(name=sequence)
            new_leaf.dist = target_node.dist
            new_leaf.support = target_node.support


    out_file = prefix + "_reintroduced_identical_sequences.nwk"
    tree.write(outfile=out_file, format=2)
    return out_file

def reintroduce_identical_sequences_leaf_to_node(tree_file: str, input_mapping: str, prefix: str) -> str:
    """Reintroduce identical sequences as children of a new zero-length node replacing the original leaf."""
    identical_sequences = read_input_mapping(input_mapping)
    tree = Tree(tree_file, format=2)

    for main_id, identicals in identical_sequences.items():
        target_nodes = tree.search_nodes(name=main_id)
        if not target_nodes:
            print(f"Warning: Node '{main_id}' not found in tree.")
            continue

        target = target_nodes[0]
        parent = target.up

        if not parent:
            print(f"Warning: Node '{main_id}' has no parent (might be root)")
            continue

        # Create a new intermediate node to replace the original target
        new_internal = Tree()
        new_internal.dist = target.dist
        new_internal.support = 100 # hardoced

        # Create zero-distance leaves for all sequences
        all_ids = [main_id] + identicals
        for seq_id in all_ids:
            child = new_internal.add_child(name=seq_id)
            child.dist = 0.0 # make distance to node 0

        # Replace original node with new internal node
        new_internal.name = ""  # optional: give it no name
        parent.remove_child(target)
        parent.add_child(new_internal)

    out_file = prefix + "_reintroduced_identical_sequences.nwk"
    tree.write(outfile=out_file, format=2)
    return out_file


@click.command()
@click.option('--input_mapping', help='[INPUT] output of find_identical_seqences.py, each row represents'
                                      'group of identical sequences, first entry is kept and should be on a tree',
              type=click.Path(), required=True)
@click.option('--input_tree', help='[INPUT] a tree in newick format',
              type=click.Path(), required=True)
@click.option('--collapse_value', help='[INPUT] a support value below which two nodes are collapsed, only '
                                       'valid with --collapse',type=int, required=False, default=70)
@click.option('--root', help='[INPUT] apply midpoint re-rooting',is_flag=True)
@click.option('--collapse', help='[INPUT] Collapse nodes with poor branch support',is_flag=True)
@click.option('--output_prefix', help='[OUTPUT] a prefix for all the files generated with this script',
              type=str, required=True)

def main_function(input_mapping, input_tree, collapse ,collapse_value, root, output_prefix):
    if root:
        input_tree = root_tree(tree_file=input_tree,
                                  prefix=output_prefix)
    if collapse:
        input_tree = collapse_weak_nodes(tree_file=input_tree,
                                         prefix=output_prefix,
                                         support_threshold=collapse_value)

    reintroduce_identical_sequences_leaf_to_node(tree_file=input_tree,
                                                 input_mapping=input_mapping,
                                                 prefix=output_prefix)
    
    #reintroduce_identical_sequences(tree_file=input_tree,
    #                                input_mapping=input_mapping,
    #                                prefix=output_prefix)
    return True

if __name__ == "__main__":
    main_function()
