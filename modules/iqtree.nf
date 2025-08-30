process iqtree {
    container  = params.main_image
    tag "${segmentId}"
    cpus params.threads
    memory "50 GB"
    time "2h"
    input:
    tuple val(segmentId), path(aln)

    output:
    tuple val(segmentId), path("${aln}.contree"), emit: out

    script:
    """
    # Updated iqtree execution with fo;;owing parameters
    # -bb Performs ultrafast bootstrap (UFBoot2)
    # -alrt Runs the SH-aLRT test to improve branch support calculations
    # -wsr Runs weighted Shimodaira–Hasegawa-like to improve final tree topology
    # -ninit Sets the number of starting trees
    iqtree2 -nt  ${task.cpus} \
        -s ${aln} \
        -m ${params.model} \
        -bb ${params.bootstrap} \
        -alrt ${params.bootstrap} \
        -con \
        -bnni \
        -minsup ${params.min_support} \
        -ninit ${params.starting_trees}
    """
}