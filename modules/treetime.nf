process treetime {
    tag "${segmentId}"
    container  = params.main_image
    publishDir "${params.results_dir}/${params.results_prefix}/", mode: 'copy', pattern: "${segmentId}_timetree.nwk"

    cpus 1
    memory "30 GB"
    time "1h"
    input:
    tuple val(segmentId), path(alignment), path(tree)
    path metadata

    output:
    tuple val(segmentId), path("${segmentId}_timetree.nwk"), path("*.node_data.json")

    script:
    """
    augur refine \
        --alignment ${alignment} \
        --tree ${tree} \
        --metadata ${metadata} \
        --output-tree ${segmentId}_timetree.nwk \
        --keep-polytomies \
        --branch-length-inference joint \
        --keep-root \
        --timetree \
        --verbosity 6
    """
}