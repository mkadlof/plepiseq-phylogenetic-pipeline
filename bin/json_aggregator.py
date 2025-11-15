#!/usr/bin/env python3

import click
import json
from pathlib import Path


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
@click.option('--results_dir', help='[INPUT] directory where results are store relatively to execution dir ',
              type=str, required=True)
def main(input_params, sequence_filtering_data, sequence_clustering_data, filogram_data, chronogram_data,
         executiondir, results_prefix, results_dir):

    out_dict = {}
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

    out_dict['input_params_data'] = input_params
    out_dict['chronogram_data'] = chronogram_data
    out_dict['sequence_filtering_data'] = sequence_filtering_data
    out_dict['sequence_clustering_data'] = sequence_clustering_data
    out_dict['filogram_data'] = filogram_data
    out_dict['input_params_data'] = input_params

    out_dict['pathogen'] = input_params['pathogen']
    out_dict['ExecutionDir_dir'] = executiondir
    out_dict['pipeline_version'] = input_params['pipeline_version']
    out_dict['status'] = "tak"
    out_dict['title'] = results_prefix

    if input_params['pathogen'] in ["Salmonella", "Escherichia", "Campylobacter"]:
        out_dict['mst_html'] = f"{results_dir}/${results_prefix}_MST.html"
        out_dict['chronogram_nwk'] = {'bacterial_genome' : '/some/path'}
        out_dict['microreact_json'] = {'bacterial_genome' : 'some/path'}
        out_dict['filogram_nwk'] = {'bacterial_genome' : '/some/path'}
    else:
        chronogram_nwk = {}
        microreact_json = {}
        filogram_nwk = {}
        lista_segmentow = sequence_filtering_data.keys()

        for segment in lista_segmentow:
            chronogram_nwk[segment] = '/some/path'
            microreact_json[segment] = '/some/path'
            filogram_nwk[segment] = '/some/path'

        out_dict['chronogram_nwk'] = chronogram_nwk
        out_dict['microreact_json'] = microreact_json
        out_dict['filogram_nwk'] = filogram_nwk

    out = Path(f"{results_prefix}.json")

    with open(out, 'w') as f:
        json.dump(out_dict, f, indent=4)


if __name__ == '__main__':
    main()
