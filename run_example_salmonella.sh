#!/bin/bash

# Example: Run phylogentic pipline on Salmonella samples
# All genomes are stored in a single directory in distinct FASTA files.
# Nextflow will use LOCAL to manage process execution.
# Warning path to external databases /NOT part of this repo/ MUST be set manually

PATH_TO_EXTERNAL_DATABASES="/mnt/raid/external_databases"

bash nf_pipeline_bacterial_phylo.sh --metadata data/example_data/salmonella/metadata_salmonella.txt \
                                    --inputDir data/example_data/salmonella/fastas \
				    --genus Salmonella \
				    --inputType fasta \
				    --projectDir `pwd` \
				    -x "local" \
				    --db "${PATH_TO_EXTERNAL_DATABASES}" \
				    --results_prefix test_salmonella \
				    --results_dir results