process insert_duplicates_into_tree {
    tag "${segmentId}"
    container  = params.main_image
    publishDir "${params.results_dir}/${params.results_prefix}/", mode: 'copy', pattern: "${segmentId}_consensus_tree.nwk"

    cpus 1
    memory "30 GB"
    time "1h"
    input:
    tuple val(segmentId), path(tree), path(ids)

    output:
    tuple val(segmentId), path("${segmentId}_consensus_tree.nwk")

    script:
    """
    insert_missing_duplicated_sequences_into_tree.py \
        --tree ${tree} \
        --ids ${ids} > ${segmentId}_consensus_tree.nwk
    """
}