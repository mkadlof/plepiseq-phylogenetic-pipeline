process consensus_tree {
    publishDir "${params.results_dir}/${params.input_prefix}/", mode: 'copy', pattern: "consensus.contree"

    cpus 1
    memory "30 GB"
    time "1h"

    input:
//    val tree_paths
//    tuple val(segment), path(tree_file)
    path('*_consensus_tree.nwk')

    output:
    path("consensus.contree")

    script:
    """
    # Rename symlinks to the base names of the target files
    for link in \$(find . -maxdepth 1 -type l); do
        target=\$(readlink "\$link")
        base_target=\$(basename "\$target")
        mv "\$link" "\$base_target"
    done

    echo "Creating consensus tree from segments: ${params.segments_to_consensus}"

    # Put all the trees for selected segments in a single file
    for segment in \$(echo ${params.segments_to_consensus}|tr ',' ' '); do
        echo "Processing segment: \$segment"
        cat "\${segment}_consensus_tree.nwk" >> all_trees.nwk
    done

    count_taxons.py *_consensus_tree.nwk

    # Remove segment symbol from the taxa names, so they contain only the samples IDs
    sed -E 's/chr[^|]+\\|//g' all_trees.nwk > all_trees_clean.nwk

    # Build the consensus tree
    iqtree2 -con -t all_trees_clean.nwk -minsup ${params.consensus_tree_threshold} --prefix consensus
    """
}