PZH phylogenetic pipeline
=========================

This project is part of [PleEpiSeq](https://www.pzh.gov.pl/projekty-i-programy/plepiseq/) project, co-funded by the European Union.

This repository contains a Nextflow pipeline for phylogenetic analysis of viral and bacterial genomes. The pipeline is designed to be modular and can be easily extended to include additional steps or tools.

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

-----------------------------------------------------------------

# Viral Phylogenetic Pipeline

This pipeline constructs viral phylogenies using raw FASTA files only.

## Input

The phylogenetic pipeline requires two types of input:
1. A tab-separated metadata file (see example below).
2. A directory containing full genomic sequences of analyzed samples in FASTA format.  

### Input directory example
Each genome must be stored in a **separate gzipped FASTA file (`.fasta.gz`)**.  
For multi-segment viruses (e.g. *Influenza*), all genomic segments must be included in a **single FASTA file per sample**.

Example directory layout:
```
/some/path/
├── Sample1.fasta.gz
├── Sample2.fasta.gz
└── Sample3.fasta.gz
```

See `data/example_data/` for reference examples.

### FASTA headers
FASTA headers **must** follow the standardized format established in the WGS pipeline:
> Segment_name|Sample_name

Where: 
- `segment_name` – identifier of the genomic segment (e.g., `chr1_PB2`, `MN908947.3`).  
  For single-segment viruses such as *SARS-CoV-2* or *RSV*, this usually corresponds to the reference sequence identifier.
- `sample_name` – unique sample identifier; must also appear in the metadata file under the `strain` column.

For example:
```
>chr4_HA|Influenza_sample2
ATGGAGAAA...
>chr6_NA|Influenza_sample2
ATAAAAGCC
```

### Metadata linkage
The `sample_name` must appear in the metadata file (in the `strain` column).  
Only this portion (after the `|` character) is matched against the metadata.


## Minimal Execution

1. Create a working directory where you want to store the results.
2. Copy the `nf_pipeline_viral_phylo.sh` script from the repository’s root directory into your working directory.
3. (Optional) Copy valid metadata and fasta file from `/data/example_data/SPECIES/` into the working directory. Use data from viral species.

Call the wrapper script

```bash
bash nf_pipeline_viral_phylo.sh -i PATH_TO_FASTA_FILE \ 
                                -m PATH_TO_METADATA_FILE 
                                -g SELECTED_SPECIES 
                                -p MY_AWESOME_PROJECT 
                                -f PATH_TO_REPOSITORY
```

e.g. if one downloaded data from `/data/example_data/sars-cov-2` to a working directory, and cloned this repo to `/home/my_user/plepiseq-phylogenetic-pipeline`, the command would be

```bash
bash nf_pipeline_viral_phylo.sh -i sars-cov-2.fasta \
                                -m sars-cov-2_metadata.tsv \
                                -g sars-cov-2 \
                                -p sars_example \
                                -f /home/my_user/plepiseq-phylogenetic-pipeline
```

To see all available options and customize your run, use:

```bash
bash nf_pipeline_viral_phylo.sh -h
```

## Metadata Format

The metadata file must be a tab-separated file with the following required columns:

- `strain` – Sample identifier (must match the filename, excluding extension). Sample identifier must be a part of a header in FASTA file
- `virus` - Virus name (sars-cov-2, influenza, or rsv)
- `date` – Collection date in `YYYY-MM-DD` format
- `country` – Country name (e.g., `France`)
- `city` – City name (e.g., `Paris`)
- `type` – Additional classification column representing suptype for Influenza (e.g `H1N1` )or type for for RSV (e.g. `A`). For SARS-CoV-2 can be identical with `virus` column

Other columns are optional and can be used for additional metadata.

To ensure homogeneity of input data, the pipeline applies **safeguards**.  
The default safeguard level is **`type`**, meaning that all samples in one run must share the same `type` value.

Depending on the configured safeguard level, the pipeline will not execute if:

- More than one unique **`virus`** is present in the `virus` column.
- More than one unique **`type`** is present in the `type` column (**default safeguard**).

- This prevents accidental mixing of heterogeneous datasets (e.g., different viruses, types, or geographic origins) in a single phylogenetic analysis run.
---

-----------------------------------------------------------------

# Bacterial Phylogenetic Pipeline

This pipeline constructs bacterial phylogenies using annotated assemblies or raw FASTA files.

## Input

Like the viral counterpart the bacterial phylogenetic pipeline also requires two types of input:
1. A tab-separated metadata file (see example below).
2. A directory containing genomic assemblies of analyzed isolates in FASTA format.

### Input directory example
Each isolate must be represented by a **single gzipped FASTA file (`.fasta.gz`)** containing all assembled contigs for that sample.
Example directory layout:

```
/some/path/
├── Sample1.fasta.gz
├── Sample2.fasta.gz
└── Sample3.fasta.gz
```

### FASTA headers
Unlike viral genomes, the **FASTA headers are not relevant** for bacterial input.  
Only the **file names** are used to identify samples and link them to metadata.  
Each `.fasta.gz` file should therefore include all contigs for a single isolate.

> **Tip:** The filenames (without the `.fasta.gz` extension) must match the `strain` column in the metadata file.

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
                                    -z RESULTS_PREFIX
                                    --threads 48
```

Replace `PATH_TO_CLONED_REPO` with the absolute path to your cloned copy of this repository.
Replace `RESULTS_PREFIX` with any string. All pipeline produced files will start with this string

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


-----------

# WGS2phylo

A helper script to prepare metadata file based on the results of our [Sequnecing pipline](https://github.com/mkadlof/plepiseq-wgs-pipeline). 
With `--with-fasta` a phylogenetic pipeline-ready fasta input can also be prepared. The generated FASTA files and metadata are directly compatible with the viral and bacterial phylogenetic pipelines described above.
Use `--without-fasta` to skip fasta file processing.

## Example data 
- [WGS output for bacterial](data/example_data/WGS2phylo/)

## Execution

### Campylobacter 
```
python3 bin/WGS2Phylo.py --output_dir data/example_data/WGS2phylo/results_Campylobacter/ --organism campylobacter --supplemental-file data/example_data/WGS2phylo/metadata_input_Campylobacter.txt --with-fasta --output-prefix metadata_out/metadata_required_Campylobacter

python3 bin/WGS2Phylo.py --output_dir data/example_data/WGS2phylo/results_Campylobacter/ --organism campylobacter --supplemental-file data/example_data/WGS2phylo/metadata_input_Campylobacter.txt --with-fasta --extra-fields --output-prefix metadata_out/metadata_expanded_Campylobacter

```

### RSV

```
python3 bin/WGS2Phylo.py --output_dir data/example_data/WGS2phylo/results_rsv/ --organism rsv --supplemental-file data/example_data/WGS2phylo/metadata_input_rsv.txt --with-fasta --output-prefix metadata_out/metadata_required_rsv

python3 bin/WGS2Phylo.py --output_dir data/example_data/WGS2phylo/results_rsv/ --organism rsv --supplemental-file data/example_data/WGS2phylo/metadata_input_rsv.txt --with-fasta --extra-fields --output-prefix metadata_out/metadata_expanded_rsv
```

## Tests
Go to tests/WGS2Phylo and execute:
```
pytest test_WGS2Phylo.py --data-dir ../../data/example_data/WGS2phylo/unit_tests/ -v
``` 
