#!/usr/bin/env python3

import click
import json
from pathlib import Path
import os


@click.command()
@click.option('--input_params', help='[INPUT] a json file output with input parameters',
              type=click.Path(), required=True)
@click.option('--sequence_filtering_data', help='[INPUT] a json file output with sequence filtering data ',
              type=click.Path(), required=True)
@click.option('--sequence_clustering_data', help='[INPUT] a json file output with sequence clustering data ',
              type=click.Path(), required=True)
@click.option('--filogram_data', help='[INPUT] a json file output of phylogentic analysis ',
              type=click.Path(), required=True)
@click.option('--chronogram_data', help='[INPUT] a json file output of timetree analysis ',
              type=click.Path(), required=True)
@click.option('--executiondir', help='[INPUT] ExecutionDir ',
              type=str, required=True)
@click.option('--results_prefix', help='[INPUT] results_prefix ',
              type=str, required=True)
def main(input_params, sequence_filtering_data, sequence_clustering_data, filogram_data, chronogram_data,
         executiondir, results_prefix):

    out_dict = {}
    out_dict['output'] = {}
    with open(input_params) as f:
        input_params = json.load(f)

    with open(sequence_filtering_data) as f:
        sequence_filtering_data = json.load(f)

    with open(sequence_clustering_data) as f:
        sequence_clustering_data = json.load(f)

    with open(filogram_data) as f:
        filogram_data = json.load(f)

    with open(chronogram_data) as f:
        chronogram_data = json.load(f)

    out_dict['output']['input_params_data'] = input_params
    out_dict['output']['input_params_data']['input_ids'] = out_dict['output']['input_params_data']['input_ids'] .split(',')[:-1]

    try:
        out_dict['output']['input_params_data']['clockrate'] = round(float(out_dict['output']['input_params_data']['clockrate']), 6)
    except ValueError:
        out_dict['output']['input_params_data']['clockrate'] = out_dict['output']['input_params_data']['clockrate']

    full = out_dict['output']['input_params_data']['results_dir']

    results_dir = os.path.relpath(full, start= executiondir)

    out_dict['output']['chronogram_data'] = chronogram_data
    for segment in  out_dict['output']['chronogram_data'].keys():
        out_dict['output']['chronogram_data'][segment]['id_chronogram'] =  out_dict['output']['chronogram_data'][segment]['id_chronogram'].split(',')[:-1]

    out_dict['output']['sequence_filtering_data'] = sequence_filtering_data
    out_dict['output']['sequence_clustering_data'] = sequence_clustering_data
    out_dict['output']['filogram_data'] = filogram_data
    for segment in  out_dict['output']['filogram_data'].keys():
        out_dict['output']['filogram_data'][segment]['id_filogram'] =  out_dict['output']['filogram_data'][segment]['id_filogram'].split(',')[:-1]


    out_dict['output']['input_params_data'] = input_params

    out_dict['output']['pathogen'] = input_params['pathogen']
    out_dict['output']['ExecutionDir_dir'] = executiondir
    out_dict['output']['pipeline_version'] = input_params['pipeline_version']
    out_dict['output']['status'] = "tak"
    out_dict['output']['title'] = results_prefix
    out_dict['output']['data_uruchomienia'] = input_params['data_uruchomienia']

    if input_params['pathogen'] in ["salmonella", "escherichia", "campylobacter"]:
        out_dict['output']['mst_html'] = {'bacterial_genome':f'{results_dir}/{results_prefix}_MST.html'}
        out_dict['output']['chronogram_nwk'] = {'bacterial_genome' : f'{results_dir}/{results_prefix}_chronogram.nwk' }
        out_dict['output']['microreact_json'] = {'bacterial_genome' : f'{results_dir}/{results_prefix}_microreactproject.microreact'}
        out_dict['output']['filogram_nwk'] = {'bacterial_genome' : f'{results_dir}/{results_prefix}_filogram.nwk'}
    else:
        chronogram_nwk = {}
        microreact_json = {}
        filogram_nwk = {}
        lista_segmentow = sequence_filtering_data.keys()

        for segment in lista_segmentow:
            chronogram_nwk[segment] = f'{results_dir}/{results_prefix}_{segment}_chronogram.nwk'
            microreact_json[segment] = f'{results_dir}/{results_prefix}_{segment}_microreactproject.microreact'
            filogram_nwk[segment] = f'{results_dir}/{results_prefix}_{segment}_filogram.nwk'

        out_dict['output']['chronogram_nwk'] = chronogram_nwk
        out_dict['output']['microreact_json'] = microreact_json
        out_dict['output']['filogram_nwk'] = filogram_nwk


    out = Path(f"{results_prefix}.json")

    with open(out, 'w') as f:
        json.dump(out_dict, f, indent=4)


if __name__ == '__main__':
    main()
