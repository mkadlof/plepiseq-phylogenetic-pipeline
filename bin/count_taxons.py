#!/usr/bin/env python3

import argparse
from Bio import Phylo

def main():
    parser = argparse.ArgumentParser(description="Count taxa in Newick trees from multiple files (one tree per file).")
    parser.add_argument("files", nargs='+', help="List of Newick files (one tree per file).")
    args = parser.parse_args()

    for filename in args.files:
        with open(filename) as f:
            tree = Phylo.read(f, "newick")
            taxon_count = len(tree.get_terminals())
            print(f"{filename}: {taxon_count} taxa")

if __name__ == '__main__':
    main()