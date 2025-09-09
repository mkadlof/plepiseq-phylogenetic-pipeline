#!/bin/bash

bash nf_pipeline_viral_phylo.sh -i ./data/example_data/sars-cov-2/sars-cov-2.fasta \
	                        -m ./data/example_data/sars-cov-2/sars-cov-2_metadata.tsv \
				-g sars-cov-2 \
				-p test_sars \
				-d `pwd` \
				-x local

