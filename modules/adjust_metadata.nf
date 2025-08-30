process adjust_metadata {
    container  = params.main_image
    tag "Executing adjust_metadata script"
    cpus 1
    memory "30 GB"
    time "1h"
    input:
    path metadata

    output:
    path "influenza_metadata_adjusted.tsv", emit: adjusted_metadata

    script:
    """
    adjust_metadata.py ${metadata}
    """
}