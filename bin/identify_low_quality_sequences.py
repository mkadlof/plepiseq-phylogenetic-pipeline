#!/usr/bin/env python3

import argparse
import csv
import os
from typing import Dict, List, Any
import json
from pathlib import Path




def restricted_float(x):
    """This function is used in argparse to validate the float value to be between 0.0 and 1.0"""
    x = float(x)
    if x < 0.0 or x > 1.0:
        raise argparse.ArgumentTypeError(f"{x} not in range [0.0, 1.0]")
    return x

def validate_Ns_are_below_threshold(row, threshold=0.02):
    n_proportion = int(row['N']) / int(row['length'])
    valid = n_proportion <= threshold
    print(f"{row['strain']} N_proportion: {n_proportion} <= {threshold} Result: {'valid' if valid else 'invalid'}")
    return valid


def validate_ambiguities_are_below_threshold(row, threshold=0):
    ambiguity_proportion = int(row['other_IUPAC']) / int(row['length'])
    valid = ambiguity_proportion <= threshold
    print(f"{row['strain']} Ambiguity_proportion: {ambiguity_proportion} <= {threshold} Result: {'valid' if valid else 'invalid'}")
    return valid

def prepare_json_entry(row:Dict, threshold_Ns, threshold_ambiguities) -> Dict[str, Dict[str, Any]]:
    ambiguity_proportion = int(row['other_IUPAC']) / int(row['length'])
    valid_ambig = ambiguity_proportion <= threshold_ambiguities
    n_proportion = int(row['N']) / int(row['length'])
    valid_n = n_proportion <= threshold_Ns
    out_dict = {}

    if valid_ambig and valid_n:
        out_dict[row['strain']] = {
            "number_of_N": int(row['N']),
            "number_of_ambiguous" : int(row['other_IUPAC']),
            "status" : "tak"
        }

    elif valid_ambig and not valid_n:
        out_dict[row['strain']] = {
            "number_of_N": int(row['N']),
            "number_of_ambiguous" : int(row['other_IUPAC']),
            "status" : "nie",
            "error_message" : f"Number of Ns in a sequence is {int(row['N'])}, with total length os a sequence is {int(row['length'])} that number exceeds threshold of {threshold_Ns}"
        }

    elif not valid_ambig and valid_n:
        out_dict[row['strain']] = {
            "number_of_N": int(row['N']),
            "number_of_ambiguous" : int(row['other_IUPAC']),
            "status" : "nie",
            "error_message" : f"Number of ambiguous characters in a sequence is {int(row['other_IUPAC'])}, with total length os a sequence is {int(row['length'])} that number exceeds threshold of {threshold_ambiguities}"
        }
    else:
        out_dict[row['strain']]= {
            "number_of_N": int(row['N']),
            "number_of_ambiguous" : int(row['other_IUPAC']),
            "status" : "nie",
            "error_message": f"Number of ambiguous characters in a sequence is {int(row['other_IUPAC'])}, with total length os a sequence is {int(row['length'])} that number exceeds threshold of {threshold_ambiguities}" + f", additionally number of ambiguous characters in a sequence is {int(row['other_IUPAC'])}, with total length os a sequence is {int(row['length'])} that number exceeds threshold of {threshold_ambiguities}"
        }

    return out_dict

# def validate_ambiguities_are_below_threshold(row, threshold=0):
#     return int(row['other_IUPAC']) / int(row['length']) <= threshold


def is_valid(row, args):
    return validate_Ns_are_below_threshold(row, args.threshold_Ns) and validate_ambiguities_are_below_threshold(row, args.threshold_ambiguities)


def write_strains(strains: List[Dict[str, str]], output):
    with open(output, 'w') as f:
        f.write('\n'.join(row['strain'] for row in strains))


def main():
    parser = argparse.ArgumentParser(description='Identify low quality sequences')
    parser.add_argument('--input', type=str, help='Input CSV augur index file')
    parser.add_argument('--output_dir', default="results", type=str, help='Output file with valid strains')
    parser.add_argument('--threshold_Ns', default=0.02, type=restricted_float, help='Threshold for Ns validation')
    parser.add_argument('--threshold_ambiguities', default=0, type=restricted_float, help='Threshold for ambiguities validation')
    parser.add_argument('--json_out', default='sequence_filtering_data.json', type=str,
                        help='Output json file summarizing the results')
    parser.add_argument('--segment_name', type=str, required=False, default='bacterial_genome',
                        help='Segment name to appear in json output')
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    valid_strains = []
    invalid_strains = []
    json_data = {}
    json_data[args.segment_name] = {}

    with open(args.input, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        all_strains = 0
        valid = 0
        for row in reader:
            row_data = prepare_json_entry(row = row,
                                          threshold_Ns = args.threshold_Ns,
                                          threshold_ambiguities = args.threshold_ambiguities)
            json_data[args.segment_name] = {**json_data[args.segment_name], **row_data}

            all_strains += 1
            if is_valid(row, args):
                valid += 1
                valid_strains.append(row)
            else:
                invalid_strains.append(row)
    write_strains(valid_strains, os.path.join(args.output_dir, 'valid_strains.txt'))
    write_strains(invalid_strains, os.path.join(args.output_dir, 'invalid_strains.txt'))


    # print(f"Sequence quality validation:\n"
    #       f"Valid strains: {valid}, Dropped strains: {all_strains - valid}")
    output_path = Path(args.json_out)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
