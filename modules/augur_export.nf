process augur_export {
    tag "${segmentId}"

    publishDir "${params.results_dir}/${params.input_prefix}/", mode: 'copy', pattern: "auspice_${segmentId}.json"

    cpus 1
    memory "30 GB"
    time "1h"

    input:
    tuple val(segmentId), path(tree), path(node_data)
    path metadata

    output:
    path "auspice_${segmentId}.json", emit: out

    script:
    """
    augur export v2 \
        --tree ${tree} \
        --metadata ${metadata} \
        --auspice-config /etc/auspice/auspice_config.json \
        --title "PZH viral phylogenetic pipeline" \
        --node-data ${node_data} \
        --output auspice_${segmentId}.json
    """
}