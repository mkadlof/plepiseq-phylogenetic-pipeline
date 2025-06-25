#!/bin/bash

nextflow run nf_bacterial_phylogenetic_pipeline.nf \
             --input_dir data/example_data/salmonella/fastas \
             --metadata data/example_data/salmonella/metadata_salmonella.txt \
             --genus Salmonella \
             --threshold_Ns 1.0 \
             --threshold_ambiguities 1.0 \
             --input_type fasta \
             --main_image pzh_pipeline_bacterial-phylo:latest \
             --prokka_image staphb/prokka:latest \
             -profile local \
             -with-dag dag_png/nf_bacterial_phylogenetic_pipeline.png \
             -with-trace trace.tsv \
             -with-report report.html \
             -resume

# Remove logs from previous runs
rm \.nextflow.log\.*
