#!/bin/bash

# Example: Run viral phylogenetic pipeline on RSV type A dataset
# All genomes are stored in a single FASTA files.
# Nextflow will use SLURM executor to manage process execution.

bash nf_pipeline_viral_phylo.sh -i data/example_data/rsv \
	                        -m data/example_data/rsv/rsv_a_metadata.tsv \
			       	-g rsv \
				-p test_rsv \
				-d . \
				-x slurm
