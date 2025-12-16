process treetime {
    // This module is nearly identical to one from bacteria, however,
    // viral pipeine is using params.organism not params.genus
    // default clockrates are provided for viral species
    // adjusting branches length to match temporal singal was pushed to a separate module
    tag "Adding temporal data to tree for segment: ${segmentId}"
    container  = params.main_image
    publishDir "${params.results_dir}/${params.results_prefix}/", mode: 'copy', pattern: "${segmentId}_timetree.nwk"
    // publishDir "${params.results_dir}/${params.results_prefix}/subschemas", mode: 'copy', pattern: "${segmentId}_chronogram_data.json"
    cpus 1
    memory "30 GB"
    time "4h"
    input:
    tuple val(segmentId), path(alignment), path(tree)
    path(metadata)

    output:
    tuple val(segmentId), path("${segmentId}_tree3_timetree.nwk"), path("${segmentId}_branch_lengths.json"), path("${segmentId}_traits.json"), path(metadata), emit: to_auspice
    tuple val(segmentId), path("${segmentId}_tree3_timetree.nwk"), path("${segmentId}_branch_lengths.json"), emit: to_microreact
    tuple val(segmentId), path("${segmentId}_chronogram_data.json"), emit: json
    script:
    """

    run_augur() {
       local CR="\${1}"
       augur refine --tree ${tree} \\
                    --alignment ${alignment} \\
                     --metadata ${metadata} \\
                     --output-tree ${segmentId}_tree3_timetree.nwk \\
                     --output-node-data ${segmentId}_branch_lengths.json \\
                     --timetree \\
                     --coalescent opt \\
                     --date-confidence \\
                     --date-inference marginal \\
                     --precision 3 \\
                     --max-iter 10  \\
                     --keep-polytomies \\
                     --clock-rate \${CR}

   }

    if [ -n "${params.clockrate}"  ]; then
       # use user provided clockrate for treetime it overwrites all safeguards
       run_augur ${params.clockrate}

       CORRELATION="-1"
       CLOCK=${params.clockrate}

    else

      # Estimate clock rate if correlation is poor use predefined values for a provided genus ... better than nothing i guess
      cat $metadata | tr "\\t" "," >> metadata.csv
      /usr/local/bin/treetime clock --tree $tree --aln $alignment --dates metadata.csv >> log 2>&1
      CORRELATION=`cat log  | grep "r^2" | awk '{print \$2}'`
      CLOCK=`cat log  | grep -w "\\-\\-rate"  | awk '{print \$2}'`
      if awk "BEGIN {if (\${CORRELATION} < 0.5) exit 0; else exit 1}"; then
        # We have poor fitness of our data we provide treetime with own set of parameters ...
        if [ ${params.organism}  == 'sars-cov-2' ]; then
          clockrate="1.12e-3"
          CLOCK=\${clockrate}
        elif [ ${params.organism}  == 'influenza' ]; then
          clockrate="2e-5"
          CLOCK=\${clockrate}
        elif [ ${params.organism} == 'rsv' ]; then
          clockrate="1.12e-3"
          CLOCK=\${clockrate}
          ### THIS NEED TO BE FIXED W+ONCE DEFAULT FOR RSV IS FOUND ###
        fi
        run_augur \${clockrate}
      else


        augur refine --tree ${tree} \\
                    --alignment ${alignment} \\
                    --metadata ${metadata} \\
                    --output-tree ${segmentId}_tree3_timetree.nwk  \\
                    --output-node-data ${segmentId}_branch_lengths.json  \\
                    --timetree \\
                    --coalescent opt \\
                    --date-confidence \\
                    --date-inference marginal \\
                    --precision 3 \\
                    --max-iter 10  \\
                    --keep-polytomies
      fi  # End for CORRELATION estimation

    fi # End for user provided clockrate

    # reconstruct ancestral features

    augur traits --tree  ${segmentId}_tree3_timetree.nwk  \\
                 --metadata ${metadata} \\
                 --output-node-data ${segmentId}_traits.json \\
                 --columns "country city" \\
                 --confidence



    ### Section for json ###
    AUGUR_VERSION=`augur version | awk '{print \$2}'`
    TREETIME_VERSION=`treetime version |awk '{print \$2}'`
    ID=`grep ">" ${alignment} | sed s'|>||g' | tr "\\n" ","`

    echo "{'${segmentId}' :
        {'id_chronogram':'\${ID}',
        'augur_version':'\${AUGUR_VERSION}',
        'treetime_version' : '\${TREETIME_VERSION}',
        'clockrate_value' : \${CLOCK},
        'clockrate_correlation' : \${CORRELATION}}
        }" >> ${segmentId}_chronogram_data.json

    cat ${segmentId}_chronogram_data.json |  tr "\\'" "\\"" > tmp
    mv tmp ${segmentId}_chronogram_data.json

    """
}
