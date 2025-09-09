#!/bin/bash

# Example: Run viral phylogenetic pipeline on influenza dataset
# All genomes are stored in a single directory in distinct FASTA files.
# Nextflow will use SLURM to manage process execution.


bash nf_pipeline_viral_phylo.sh -i ./data/example_data/influenza/ \
                                -m ~/git/pzh-phylogenetic-pipeline/data/example_data/influenza/influenza_metadata.tsv \ 
				-g influenza \
			       	-p test_influenza \
				-d . \
				-x slurm 

