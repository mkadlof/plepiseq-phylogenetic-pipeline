#!/bin/bash

nextflow run nf_viral_phylogenetic_pipeline.nf \
             --input_fasta /home/mkadlof/pzh/data/rsv_a/rsv_a_styczne_luty_2025_renamed.fasta \
             --metadata /home/mkadlof/pzh/data/rsv_a/rsv_a_styczne_luty_2025_renamed_metadata.txt \
             --organism sars-cov-2 \
             -with-dag dag_png/nf_rsv_phylogenetic_pipeline.png \
             -with-trace trace.tsv \
             -with-report report.html \
             -resume

# Remove logs from previous runs
rm \.nextflow.log\.*
