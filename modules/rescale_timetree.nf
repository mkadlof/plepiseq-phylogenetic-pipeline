process rescale_timetree {
    tag "${segmentId}"
    cpus 1
    memory "20 GB"
    time "5h"

    input:
    tuple val(segmentId), path(timetree), path(node_data)

    output:
    tuple val(segmentId), path("tree_rescaled.nwk")

    script:
    """
    # modify timetree.nwk by replacing branches length with "time distance" predicted for each leaf and internal node with timetree
    convert_nwk_to_timetree.py --tree ${timetree} --branches ${node_data} --output tree_rescaled.nwk
    """
}