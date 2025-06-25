PZH phylogenetic pipeline
=========================

This project is part of [PleEpiSeq](https://www.pzh.gov.pl/projekty-i-programy/plepiseq/) project. This repository contains a Nextflow pipeline for phylogenetic analysis of viral sequences. The pipeline is designed to be modular and can be easily extended to include additional steps or tools.

Pipeline overview
-----------------
![nf_viral_phylogenetic_pipeline.png](nf_viral_phylogenetic_pipeline.png "Pipeline Overview")

Quick start
-----------

1. Install [Nextflow](https://www.nextflow.io/docs/latest/install.html)
2. Install [Docker](https://docs.docker.com/engine/install/)
3. Clone this repository
4. Build docker image
   ```bash
   docker build -t pzh_pzh-phylogenetic .
   ```
5. Run the pipeline on example data:
   ```bash
   ./run_viral_pipeline.sh
    ```


Related projects
----------------

The pipeline loosely originates from [NextStrain Zika Tutorial](https://github.com/nextstrain/zika-tutorial)

Another project related to PleEpiSeq is [Sequnecing pipline](https://github.com/mkadlof/pzh_pipeline_viral)

To execute bacterial pipeline type

# Bacterial Phylogenetic Pipeline

This pipeline constructs bacterial phylogenies using annotated assemblies or raw FASTA files.

## Prerequisites

Before running the pipeline, ensure the following requirements are met:

### 1. Docker Images

You must have the following Docker images available on your machine:

- [`staphb/prokka:latest`](https://hub.docker.com/r/staphb/prokka):  
  Pull from DockerHub using:
  ```bash
  docker pull staphb/prokka:latest
  ```

- `pzh_pipeline_phylogenetic:latest`:  
  Build locally from the repository:
  ```bash
  docker build -t pzh_pipeline_phylogenetic:latest -f Dockerfile-phylogenetic .
  ```

### 2. Nextflow Configuration

Ensure your `~/.nextflow/config` includes the appropriate executor profiles. You can copy and paste the following configuration.  
**Important**: Update the `--nodelist` value under the `slurm` profile to match the hostname of your cluster.

```
profiles {
    local {
        process.executor = 'local'
        process.errorStrategy = 'retry'
        process.maxRetries = 2
    }

    slurm {
        process.executor = 'slurm'
        process.clusterOptions = '--nodelist=a100-1'
        process.errorStrategy = 'retry'
        process.maxRetries = 2
    }
}

executor {
    $local {
        cpus = 256
        memory = '2000 GB'
    }
    $slurm {
        queueSize = 500
    }
}

docker.enabled = true
```

---

## Minimal Execution

Follow these steps to run the pipeline with minimal setup:

1. Create a working directory where you want to store the results.
2. Copy the `nf_pipeline_bacterial_phylo.sh` script from the repository’s root directory into your working directory.
3. (Optional) Copy a valid metadata file e.g. `metadata_salmonella.txt` file and a `fastas/` directory with uncompressed genome FASTA files into the working directory.  Example files are available in the `data/` directory of the repository. **warning** you must uncompress fasta files in data/fasta directory.

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

---

## Input File Naming

Input files must be provided in either **FASTA** or **GFF** format.

- If FASTA files are used, **Prokka** will be automatically invoked to annotate them to GFF format.
- The `strain` value in the metadata must **exactly match** the filename (excluding extension).

**Example**:  
For a file named `ERRXYZ.fasta`, the corresponding `strain` value in the metadata file must be `ERRXYZ`.

