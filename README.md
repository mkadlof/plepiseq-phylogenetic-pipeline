PZH phylogenetic pipeline
=========================

This project is part of [PleEpiSeq](https://www.pzh.gov.pl/projekty-i-programy/plepiseq/) project, co-funded by the European Union.

This repository contains a Nextflow pipeline for phylogenetic analysis of viral sequences. The pipeline is designed to be modular and can be easily extended to include additional steps or tools.

Pipeline overview
-----------------
Following links provide to PNG files with DAG overview of the pipeline:
- [Sars pipeline](dag_png/nf_sars_phylogenetic_pipeline.png)
- [Influenza pipeline](dag_png/nf_influenza_phylogenetic_pipeline.png)
- [Bacterial pipeline](dag_png/nf_bacterial_phylogenetic_pipeline.png)

Quick start
-----------

1. Install [Nextflow](https://www.nextflow.io/docs/latest/install.html)
2. Install [Docker](https://docs.docker.com/engine/install/)
3. Clone this repository
4. Build docker pipeline images:
   ```bash
   docker build -t pzh_pipeline-phylo -f Dockerfiles/Dockerfile .
   ```
5. Pull [staphb/prokka image](https://hub.docker.com/r/staphb/prokka) image from DockerHub using:
   ```bash
   docker pull staphb/prokka:latest
   ```
6. Set up your Nextflow configuration file. Recommended way is to copy the example configuration file in the repository root.
   ```bash
   cp nextflow.config.template nextflow.config
   ```
   **Important**: adjust the content of this file to you particular environment and needs.
7. [Optional] Run one or more example scripts to test the pipeline:
   ```bash
   ./run_example_sars-cov-2.sh
   ./run_example_influenza.sh
   ./run_example_salmonella.sh
    ```

Related projects
----------------

The pipeline loosely originates from [NextStrain Zika Tutorial](https://github.com/nextstrain/zika-tutorial)

Another project related to PleEpiSeq is [Sequnecing pipline](https://github.com/mkadlof/pzh_pipeline_viral)

To execute bacterial pipeline type

-----------------------------------------------------------------

# Viral Phylogenetic Pipeline

This pipeline constructs viral phylogenies using raw FASTA files only.

## Minimal Execution

See the `run_example_[VIRUS].sh` scripts in the repository root for examples of how to run the pipeline with minimal setup. One may also use the bash wrapper script `nf_pipeline_viral_phylo.sh` directly, as shown below.

```bash

./nf_pipeline_viral_phylo.sh -i data/example_data/sars-cov-2/sars-cov-2.fasta \
                             -m data/example_data/sars-cov-2/sars-cov-2_metadata.tsv \
                             --organism sars-cov-2
```

## Metadata Format

The metadata file must be a tab-separated file with the following required columns:

- `strain` – Sample identifier (must match the filename, excluding extension)
- `virus` - Virus name (sars-cov-2, influenza, or rsv)
- `date` – Collection date in `YYYY-MM-DD` format
- `country` – Country name (e.g., `France`)
- `city` – City name (e.g., `Paris`)

Other columns are optional and can be used for additional metadata.

-----------------------------------------------------------------

# Bacterial Phylogenetic Pipeline

This pipeline constructs bacterial phylogenies using annotated assemblies or raw FASTA files.

## Minimal Execution

Follow these steps to run the pipeline with minimal setup:

1. Create a working directory where you want to store the results.
2. Copy the `nf_pipeline_bacterial_phylo.sh` script from the repository’s root directory into your working directory.
3. (Optional) Copy a valid metadata file e.g. `metadata_salmonella.txt` file and a `fastas/` directory with uncompressed genome FASTA files into the working directory.  Example files are available in the `data/example_data/salmonella` directory of the repository.

Assuming your working directory contains `metadata_salmonella.txt` and a `fastas/` directory, and you’ve built/pulled the required Docker images as described above, run:

```bash
bash nf_pipeline_bacterial_phylo.sh -m metadata_salmonella.txt \
                                    -i fastas/ \
                                    -t fasta \
                                    -g Salmonella \
                                    -p Salmonella_dummy \
                                    -d PATH_TO_CLONED_REPO \
                                    --threads 48
```

Replace `PATH_TO_CLONED_REPO` with the absolute path to your cloned copy of this repository.

To see all available options and customize your run, use:

```bash
bash nf_pipeline_bacterial_phylo.sh -h
```

One can also provide paths to metadata and directory with fasta files. There is no need to copy them to working directory.

---

## Metadata Format

The metadata file must be a tab-separated file with the following required columns:

- `strain` – Sample identifier (must match the filename, excluding extension)
- `date` – Collection date in `YYYY-MM-DD` format
- `region` – Continent (e.g., `Europe`)
- `country` – Country name (e.g., `France`)
- `division` – Sub-national region (e.g., `Ohio`)
- `city` – City name (e.g., `Paris`)
- `Serovar` – Serovar designation (e.g., `Enteritidis`)
- `MLST` – MLST ID (e.g., `11`)
- `cgMLST` – cgMLST ID (e.g., `110234`)
- `HC5` – HierCC cluster ID at threshold 5 (e.g., `13`)
- `HC10` – HierCC cluster ID at threshold 10 (e.g., `13`)

The pipeline includes strict safeguards to ensure homogeneity of input data. The pipeline will not execute if:

- Different **serotypes** (`Serovar` column in the metadata file) are provided together.

---

## Input File Naming

Input files must be provided in either **FASTA** or **GFF** format.

- If FASTA files are used, **Prokka** will be automatically invoked to annotate them to GFF format.
- The `strain` value in the metadata must **exactly match** the filename (excluding extension).

**Example**:  
For a file named `ERRXYZ.fasta`, the corresponding `strain` value in the metadata file must be `ERRXYZ`.

