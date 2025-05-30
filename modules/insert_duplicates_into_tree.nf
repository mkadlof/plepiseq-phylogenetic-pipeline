process insert_duplicates_into_tree {
    tag "${segmentId}"

    publishDir "${params.results_dir}/${params.input_prefix}/", mode: 'copy', pattern: "consensus_tree.nwk"

    cpus 1
    memory "30 GB"
    time "1h"
    input:
    tuple val(segmentId), path(tree), path(ids)

    output:
    tuple val(segmentId), path("consensus_tree.nwk")

    script:
    """
    insert_missing_duplicated_sequences_into_tree.py \
        --tree ${tree} \
        --ids ${ids} > consensus_tree.nwk
    """
}