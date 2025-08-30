process metadata_for_microreact {
    container  = params.main_image
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
    prep_metadata_for_microreact.py --metadata ${metadata} \
                                    --coordinates ${longlat} \
                                    --output "${params.input_prefix}_metadata_microreact.tsv" \
                                    --level ${params.map_detail}
    """
}