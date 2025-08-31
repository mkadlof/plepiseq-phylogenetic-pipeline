process prepare_microreact_json {
    tag "${segmentId}"
    container  = params.main_image
    publishDir "${params.results_dir}/${params.results_prefix}/", mode: 'copy', pattern: "${segmentId}_project.microreact"

    cpus 1
    memory "20 GB"
    time "1h"

    input:
    path(microreact_metadata)
    tuple val(segmentId), path(tree_regular), path(tree_rescaled)

    output:
    path("${segmentId}_project.microreact")

    script:
    """
    prepare_json_for_microreact.py --input_json /opt/docker/config/microreact_config_bacteria.microreact \
                                   --classical_tree ${tree_regular} \
                                   --rescaled_tree ${tree_rescaled} \
                                   --metadata ${microreact_metadata} \
                                   --project_name ${params.results_prefix} \
                                   --output ${segmentId}_project.microreact
    """
}
