// Variables for processes
def hostname = "hostname".execute().text.trim() // We need that to overwrite a default "container" options from config, used by the alphafold
ExecutionDir = new File('.').absolutePath

// ALL parameters are setup using bash wrapper except enterobase_api_token that MUST be part of nextflow config
// Comments were preserved in the  nf file for a local executor
params.input_dir = ""
params.input_type = ""
params.input_prefix = "" // Used only to 1. create subdirectory in params.results_dir and 2. as a prefix for auspice files. These prefix is used by auspice as part of an address e..g "flu_ha_h1n1_timestamp" or "sarscov2_timestamp" or "salmonella_poland_timestamp"
params.main_image = "" 
params.results_dir = ""
params.prokka_image = ""
params.threads = 1 
params.metadata = "" // Path to a file with metadata
params.model = "GTR+G" // Model for raxml
params.starting_trees = 10 // Number of random initial trees
params.bootstrap = 200 // Number of bootstraps
params.min_support = 70 // Minimum support for a branch to keep it in a tree
params.genus = "" // We will supplement pipeline with clock rates for relevant genus if temporal signal in the alignment is week
params.clockrate = "" // User can still override any built-in and estimated values fron the alignment
params.gen_per_year = ""

// Visualization
params.map_detail = "" // Czy próbce przypisujemy koordynaty kraju czy miasta pochodzenia. Wymagane dla microreact'a.

// User must use our config that has two profiles slurm and local, nextflow must be initialized with one of them

if ( params.genus != 'Salmonella' && params.genus != 'Escherichia' && params.genus != 'Campylobacter' ) {
    println("The program will not execute unless the provided genus is Salmonella, Escherichia, or Campylobacter.")
    System.exit(1)
} else {
    println("Running pipeline for genus: ${params.genus}")
}


if ( !workflow.profile || ( workflow.profile != "slurm" && workflow.profile != "local") ) {
   println("Nextflow run must be executed with -profile option. The specified profile must be either \"local\" or \"slurm\".")
   System.exit(1)
}

// QC params
params.threshold_Ns = 100
params.threshold_ambiguities = 100


// Processes 


process run_prokka {
  container  = params.prokka_image
  tag "Predicting genes for sample $x"
  cpus { params.threads > 25 ? 25 : params.threads }
  memory "10 GB"
  time "20m"
  input:
  tuple val(x), path(fasta)
  output:
  path("${x}.gff")
  script:
  """
    fasta="${fasta}"
    # If the input is gzipped fasta file we need to unzip it
    if [[ "${fasta}" == *.gz ]]; then
        new_name="${fasta.getName().replace('.gz', '')}"
        gunzip -c ${fasta} > \${new_name}
        fasta="\${new_name}"
    fi

    prokka --metagenome --cpus ${task.cpus} --outdir prokka_out --prefix prokka_out --compliant --kingdom Bacteria \${fasta}
    echo -e "{\\"status\\": \\"tak\\", \
              \\"prokka_gff\\": \\"${params.results_dir}/${x}/${x}_prokka.gff\\", \
              \\"prokka_ffn\\": \\"${params.results_dir}/${x}/${x}_prokka.ffn\\"}" >> prokka.json
    # Following files are useful for phylogenetic analysis
    mv prokka_out/prokka_out.gff ${x}.gff
    mv prokka_out/prokka_out.ffn ${x}.ffn
  """
}

process run_roary {
  container  = params.main_image
  tag "Predicting pangenome with roary"
  cpus { params.threads > 25 ? 25 : params.threads }
  memory "30 GB"
  time "1h"
  input:
  path(gff)
  output:
  tuple path("core_genes_alignment.fasta"), path("core_genes_alignment.embl")
  script:
  """
  # -f to nazwa katalogu z wynikiem
  # -e create a multiFASTA alignment
  # -n fast core gene alignment with MAFFT, use with -e
  # -v verbose
  # -p liczba rdzeni
  # -i minimum percentage identity for blastp [95]
  # -cd FLOAT percentage of isolates a gene must be in to be core [99]
  roary -p ${task.cpus} -i 95 -cd 95  -f ./roary_output -e -n *.gff
  cp roary_output/core_gene_alignment.aln core_genes_alignment.fasta
  cp roary_output/core_alignment_header.embl core_genes_alignment.embl
  """
}

process augur_index_sequences {
    container  = params.main_image
    tag "Indexing sequences with augur"
    cpus 1
    memory "30 GB"
    time "1h"
    
    input:
    tuple path(fasta), path(embl)

    output:
    tuple path(fasta), path(embl), path("index.csv")

    script:
    """
    augur index --sequences ${fasta} --output index.csv
    """
}

process augur_filter_sequences {
    container  = params.main_image
    tag "Filtering out sequences with augur"
    cpus 1
    memory "30 GB"
    time "1h"

    input:
    tuple path(fasta), path(embl), path(index)
    path(metadata)
    output:
    tuple path("valid_sequences.fasta"), path(embl), emit: to_SNPs_alignment
    tuple path("valid_sequences.fasta"), path(metadata), emit: alignment_and_metadata

    script:
    """
    # For NOW we are liberal when it comes to sequences quality
    # the script only checks columns 5 and 6 in $index i.e. Ns and ambiguous
    python /opt/docker/custom_scripts/identify_low_quality_sequences.py --output_dir . \
                                                                        --threshold_Ns ${params.threshold_Ns} \
                                                                        --threshold_ambiguities ${params.threshold_ambiguities} \
                                                                        $index
    # TO DO add a script that can retain only biologically valid entries from a set of sequences
    # This should be based on specific REQUIRED column in metadata file ( our NGS pipeline return this info)
    # Salmonella - predicted serovar level (e.g. only Montevideo)
    # Campylobacter - TO DO 
    # E.coli - serotype 
    # Influenza - subtype level (e.g. only H1N1pdm09)
    # SARS-Cov-2 no filters 
    # RSV type level (only A ot only B) 
    
    # For now we use augur filter to prepare fasta file without invalid_strains.txt prepared with filter_low_quality_sequences script
    # Other useful options --min-length --max-length  --group-by which we do not use for now
    augur filter \
        --sequences ${fasta} \
        --sequence-index ${index} \
        --metadata ${metadata} \
        --exclude invalid_strains.txt \
        --output-sequences valid_sequences.fasta
    """
}

process prepare_SNPs_alignment {
    container  = params.main_image
    tag "Preparing SNPs alignment"
    cpus params.threads
    memory "10 GB"
    time "2h"

    input:
    tuple path(fasta), path(embl)
    output:
    tuple path("alignment_SNPs.fasta"), path("partition.txt")

    script:
    """
    # --max_gap exclude from the analysis genes for which at least one sample missing more than 30% of sequence
    # --merge_genes partition file wont have many entries, one for each gene, but rather a single entry
    # for an entire genome + total number of constant sites observed in the initial alignment
    # this significantly speeds up the calculations by raxml as there are no partitions
    python /opt/docker/custom_scripts/prep_SNPs_alignment_and_partition.py --input_fasta ${fasta} \
                                                                           --input_fasta_annotation ${embl} \
                                                                           --model ${params.model} \
                                                                           --output_fasta alignment_SNPs.fasta \
                                                                           --output_partition partition.txt \
                                                                           --cpus ${task.cpus} \
                                                                           --max_gap 30 \
                                                                           --merge_genes

    """
}

process identify_identical_sequences {
    container  = params.main_image
    tag "Preparing SNPs alignment"
    cpus params.threads
    memory "10 GB"
    time "2h"

    input:
    tuple path(fasta), path(partition)
    output:
    tuple path("alignment_SNPs_unique.fasta"), path(partition),  emit: to_raxml
    path("alignment_SNPs_ident_seq.csv"), emit: identical_sequences_mapping 
    script:
    """
    python /opt/docker/custom_scripts/find_identical_sequences.py -i ${fasta} -o .
    """

}

process run_raxml {
    container  = params.main_image
    tag "Calculating SNPs tree"
    cpus params.threads
    memory "10 GB"
    time "8h"
    input:
    tuple path(fasta), path(partition)
    output:
    path("tree.raxml.support"), emit: tree
    script:
    def ntrees = params.starting_trees
    def nboots = params.bootstrap

    """
    if [ ${task.cpus} -lt 12 ]; then
      WORKERS=1
    else
      WORKERS=\$((${task.cpus} / 12))
    fi

    # Modified precision to get in nwk even small distances 
    raxml-ng --all \\
             --msa ${fasta} \\
             --precision 15 \\
             --threads ${task.cpus} \\
             --model ${partition} \\
             --site-repeats on \\
             --tree pars{${ntrees}} \\
             --bs-trees ${nboots} \\
             --prefix tree \\
             --force \\
             --workers \${WORKERS} \\
             --brlen scaled
    """  
}

process restore_identical_sequences {
    // Reroot initial tree, collapse poorly supported nodes
    // Reintroduce identical sequences that were removed prior to tree calculation
    publishDir "${params.results_dir}/${params.input_prefix}/", mode: 'copy', pattern: "${params.input_prefix}_classical_tree.nwk"
    container  = params.main_image
    tag "Refining initial tree"
    cpus 1
    memory "10 GB"
    time "10m"
    input:
    path(tree)
    path(identical_sequences_mapping) 
    output:
    path("tree2_reintroduced_identical_sequences.nwk"), emit: tree
    path("${params.input_prefix}_classical_tree.nwk"), emit: to_publishdir
    script:
    """
    python /opt/docker/custom_scripts/root_collapse_and_add_identical_seq_to_tree.py --input_mapping ${identical_sequences_mapping} \\
                                                                                     --input_tree ${tree} \\
                                                                                     --collapse_value ${params.min_support} \\
                                                                                     --root \\
                                                                                     --collapse \\
                                                                                     --output_prefix tree2
    cp tree2_reintroduced_identical_sequences.nwk ${params.input_prefix}_classical_tree.nwk 
    """
    
}

process add_temporal_data {
    // adjust branch lengths in tree to position tips by their sample date and infer the most likely time of their ancestors
    // augur refine seems to be a wrapper around treetime
    // Be aware that poor data with poor temporal signal might result in an incorrect tree
    container  = params.main_image
    tag "Adding temporal data to tree"
    cpus 1
    memory "20 GB"
    time "5h"
    input:
    path(tree)
    tuple path(alignment), path(metadata)// SNPs alignment would confuse timetree when estimating clock we are using initial full alignment
    output:
    tuple path("tree3_timetree.nwk"), path("branch_lengths.json"), path("traits.json"), emit: to_auspice
    tuple path(tree), path("tree3_rescaled.nwk"), emit: to_microreact 
    script:
    """

    run_augur() {
       local CR="\${1}"
       augur refine --tree ${tree} \\
                    --alignment ${alignment} \\
                     --metadata ${metadata} \\
                     --output-tree tree3_timetree.nwk \\
                     --output-node-data branch_lengths.json \\
                     --timetree \\
                     --coalescent opt \\
                     --date-confidence \\
                     --date-inference marginal \\
                     --precision 3 \\
                     --max-iter 10  \\
                     --gen-per-year 250 \\
                     --keep-polytomies \\
                     --clock-rate \${CR}

   }

    if [ -n "${params.clockrate}"  ]; then
       # use user provided parameters for treetime overwrites all safeguards
       run_augur ${params.clockrate}

    else
     
      # Estimate clock rate if correlation is poor use predefined values for a provided genus ... better than nothing i guess
      cat $metadata | tr "\\t" "," >> metadata.csv
      /usr/local/bin/treetime clock --tree $tree --aln $alignment --dates metadata.csv >> log 2>&1
      CORRELATION=`cat log  | grep "r^2" | awk '{print \$2}'`
      if awk "BEGIN {if (\${CORRELATION} < 0.5) exit 0; else exit 1}"; then
        # We have poor fitness of our data we provide treetime with own set of parameters ...
        if [ ${params.genus}  == 'Salmonella' ]; then
          clockrate="2e-6"
        elif [ ${params.genus}  == 'Escherichia' ]; then
          clockrate="8e-9"
        elif [ ${params.genus} == 'Campylobacter']; then
          clockrate="6e-6"
        fi
        run_augur \${clockrate}
      else
        # we run treetime without specifying clock rate, alignment is ok
         
        augur refine --tree ${tree} \\
                    --alignment ${alignment} \\
                    --metadata ${metadata} \\
                    --output-tree tree3_timetree.nwk \\
                    --output-node-data branch_lengths.json \\
                    --timetree \\
                    --coalescent opt \\
                    --date-confidence \\
                    --date-inference marginal \\
                    --precision 3 \\
                    --max-iter 10  \\
                    --gen-per-year 250 \\
                    --keep-polytomies 
      fi  # End for CORRELATION estimation
    
    fi # End for user provided clockrate

    # reconstruct ancestral features
    
    augur traits --tree  tree3_timetree.nwk \\
                 --metadata ${metadata} \\
                 --output-node-data traits.json \\
                 --columns "country city" \\
                 --confidence
    
    
    # modify tree3_timetree.nwk by replacing branches length with "time distance" predicted for each leaf and internal node with timetree
    python /opt/docker/custom_scripts/convert_nwk_to_timetree.py --tree tree3_timetree.nwk --branches branch_lengths.json --output tree3_rescaled.nwk
    """
}

process run_dummy_refine {
    // This process runs augur refine without tree time. It goal is to produce valid branch_lengths.json file for original nwk tree from raxml-ng
    // So it can visualized alongside actual timetree
    container  = params.main_image
    tag "Adding temporal data to tree"
    cpus 1
    memory "20 GB"
    time "5h"
    input:
    path(tree)
    tuple path(alignment), path(metadata)
    output:
    tuple path("tree3_notimetree.nwk"), path("branch_lengths_notime.json")
    script:
    """

    run_augur() {
       augur refine --tree ${tree} \\
                    --alignment ${alignment} \\
                    --metadata ${metadata} \\
                    --output-tree tree3_notimetree.nwk \\
                    --output-node-data branch_lengths_notime.json \\
                    --branch-length-inference input \\
                    --keep-polytomies \\
                    --keep-root

   }

   # Run castrated augur
   run_augur
   
   """
}

process find_country_coordinates {
    // use Open Street Map api to request geographical objects coordinates
    container  = params.main_image
    tag "Preparing geo data for analyzed data"
    cpus 1
    memory "20 GB"
    time "2h"
    input:
    path(metadata)
    output:
    path("longlang.txt")
    script:
    """
    python /opt/docker/custom_scripts/extract_geodata.py  --input_metadata ${metadata} \
                                                          --output_metadata tmp.txt \
                                                          --features country \
                                                          --features city
    # sort file using feature name
    cat tmp.txt | sort -k1 > longlang.txt
    """

}

process generate_colors_for_features {
    container  = params.main_image
    tag "Preparing colors for analyzed data"
    cpus 1
    memory "20 GB"
    time "2h"
    input:
    path("longlang.txt")
    output:
    tuple path("longlang.txt"), path("color_data.txt")
    script:
    """
    cat longlang.txt | cut -f1,2 >> tmp.txt
    python /opt/docker/custom_scripts/generate_colors_for_feature.py  --input_file tmp.txt \
                                                                      --output_file color_data.txt 
    """

}

process visualize_tree_1 {
    container  = params.main_image
    publishDir "${params.results_dir}/${params.input_prefix}/", mode: 'copy', pattern: "${params.input_prefix}_${suffix}.json"
    tag "Visualizing the data"
    cpus 1
    memory "20 GB"
    time "2h"
    input:
    tuple path(tree), path(branch_lengths), path(traits)
    tuple path(longlat), path(colors)
    path(metadata)
    val(suffix) // either timetree or regular tree
    output:
    path("${params.input_prefix}_${suffix}.json")
    script:
    """

    augur export v2 --tree ${tree} \
            --metadata ${metadata} \
            --node-data ${branch_lengths} ${traits} \
            --auspice-config /opt/docker/config/auspice_config_${params.genus}.json \
            --colors ${colors} \
            --lat-longs ${longlat} \
            --output ${params.input_prefix}_${suffix}.json \
            """

}



process visualize_tree_2 {
    container  = params.main_image
    publishDir "${params.results_dir}/${params.input_prefix}/", mode: 'copy', pattern: "${params.input_prefix}_${suffix}.json"
    tag "Visualizing the data"
    cpus 1
    memory "20 GB"                        
    time "2h"
    input:
    tuple path(tree), path(branch_lengths)
    tuple path(longlat), path(colors)
    path(metadata)
    val(suffix) // either timetree or regular tree
    output:
    path("${params.input_prefix}_${suffix}.json")
    script:
    """
    augur export v2 --tree ${tree} \
                     --metadata ${metadata} \
                     --node-data ${branch_lengths} \
                     --auspice-config /opt/docker/config/auspice_config_${params.genus}.json \
                     --colors ${colors} \
                     --lat-longs ${longlat} \
                     --output ${params.input_prefix}_${suffix}.json \
            """

}                                                                                                                                                                                                 
process metadata_for_microreact {
    container  = params.main_image
    publishDir "${params.results_dir}/${params.input_prefix}/", mode: 'copy', pattern: "${params.input_prefix}_metadata_microreact.tsv"
    tag "Preparing metadata for microreact"
    cpus 1
    memory "20 GB"
    time "1h"
    input:
    tuple path(longlat), path(colors)
    path(metadata)      
    output:
    path("${params.input_prefix}_metadata_microreact.tsv")
    script:
    """ 
    python3 /opt/docker/custom_scripts/prep_metadata_for_microreact.py --metadata ${metadata} \
                                                                       --coordinates ${longlat} \
                                                                       --output "${params.input_prefix}_metadata_microreact.tsv" \
                                                                       --level ${params.map_detail}
    """
  
    
}

process prepare_microreact_json {
    container  = params.main_image 
    publishDir "${params.results_dir}/${params.input_prefix}/", mode: 'copy', pattern: "${params.input_prefix}_microreactproject.microreact"
    tag "Preparing .microreact file"
    cpus 1
    memory "20 GB"
    time "1h"
    input:
    path("${params.input_prefix}_metadata_microreact.tsv")
    tuple path(tree_regular), path("tree_rescaled_branches")
    output:
    path("${params.input_prefix}_microreactproject.microreact")
    script:
    """

    python3 /opt/docker/custom_scripts/prepare_json_for_microreact.py --input_json /opt/docker/config/microreact_config_bacteria.microreact \
                                                                      --classical_tree ${tree_regular} \
                                                                      --rescaled_tree ${tree_rescaled_branches} \
                                                                      --metadata ${params.input_prefix}_metadata_microreact.tsv \
                                                                      --project_name ${params.input_prefix} \
                                                                      --output ${params.input_prefix}_microreactproject.microreact

    """

}

process save_input_to_log {
  tag "Dummy process"
  cpus 1
  memory "1 GB"
  time "1m"
  input:
  path(x)
  output:
  stdout
  script:
  """
  echo ${x} >> log
  """
}

// MAIN WORKFLOW //

workflow {
Channel
    .fromPath("${params.metadata}")
    .set {metadata_channel}

// Prepare gff input

if (params.input_type == 'fasta') {
    Channel
        .fromPath("${params.input_dir}/*")
        .map { file -> tuple(file.getName().split("\\.")[0], file) }
        .set { initial_fasta }

    gff_input = run_prokka(initial_fasta).collect()

} else if (params.input_type == 'gff') {
    Channel
        .fromPath("${params.input_dir}/*")
        .collect()
        .set { gff_input }

} else {
    println("--input_type must be either fasta or gff")
    System.exit(1)
}

roary_out = run_roary(gff_input)

find_country_coordinates_out = find_country_coordinates(metadata_channel)
generate_colors_for_features_out = generate_colors_for_features(find_country_coordinates_out)

augur_index_sequences_out = augur_index_sequences(roary_out)

augur_filter_sequences_out = augur_filter_sequences(augur_index_sequences_out, metadata_channel)

prepare_SNPs_alignment_and_partition_out = prepare_SNPs_alignment(augur_filter_sequences_out.to_SNPs_alignment)

identify_identical_sequences_out = identify_identical_sequences(prepare_SNPs_alignment_and_partition_out)

run_raxml_out = run_raxml(identify_identical_sequences_out.to_raxml)

restore_identical_sequences_out = restore_identical_sequences(run_raxml_out.tree, identify_identical_sequences_out.identical_sequences_mapping)

add_temporal_data_out = add_temporal_data(restore_identical_sequences_out.tree, augur_filter_sequences_out.alignment_and_metadata)

add_dummy_data_out = run_dummy_refine(restore_identical_sequences_out.tree, augur_filter_sequences_out.alignment_and_metadata) 


metadata_for_microreact_out = metadata_for_microreact(generate_colors_for_features_out, metadata_channel)

visualize_tree_out_1 = visualize_tree_1(add_temporal_data_out.to_auspice, generate_colors_for_features_out, metadata_channel, "timetree")
visualize_tree_out_2 = visualize_tree_2(add_dummy_data_out, generate_colors_for_features_out, metadata_channel, "regulartree")
// save_input_to_log(gff_input)

prepare_microreact_json_out = prepare_microreact_json(metadata_for_microreact_out, add_temporal_data_out.to_microreact)
}
