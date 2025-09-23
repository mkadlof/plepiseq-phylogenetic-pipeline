import json
from pathlib import Path
from WGS2Phylo import get_fastqc_stats

GOLDENS = {
    'campylo_illumina.json': {
        'test_get_fastqc_stats': {
            'number_of_reads_forward': 375448,
            'number_of_bases_forward': 55200000,
            'reads_median_quality_forward': 37.0,
            'reads_median_length_forward': 150.0,
            'number_of_reads_reverse': 375448,
            'number_of_bases_reverse': 55200000,
            'reads_median_quality_reverse': 37.0,
            'reads_median_length_reverse': 150.0,
        },
    },
    'campylo_nanopore.json': {
        'test_get_fastqc_stats': {
            'number_of_reads': 57088,
            'number_of_bases': 159600000,
            'reads_median_quality': 38.0,
            'reads_median_length': 2000.0,
        },
    },
    'ecoli_illumina.json': {
        'test_get_fastqc_stats': {
            'number_of_reads_forward': 832529,
            'number_of_bases_forward': 120100000,
            'reads_median_quality_forward': 37.0,
            'reads_median_length_forward': 150.0,
            'number_of_reads_reverse': 832529,
            'number_of_bases_reverse': 120200000,
            'reads_median_quality_reverse': 36.0,
            'reads_median_length_reverse': 150.0,
        },
    },
    'ecoli_nanopore.json': {
        'test_get_fastqc_stats': {
            'number_of_reads': 208819,
            'number_of_bases': 498500000,
            'reads_median_quality': 41.0,
            'reads_median_length': 0.0,
        },
    },
    'salmonella_illumina.json': {
        'test_get_fastqc_stats': {
            'number_of_reads_forward': 1059384,
            'number_of_bases_forward': 155000000,
            'reads_median_quality_forward': 37.0,
            'reads_median_length_forward': 150.0,
            'number_of_reads_reverse': 1059384,
            'number_of_bases_reverse': 155000000,
            'reads_median_quality_reverse': 36.0,
            'reads_median_length_reverse': 150.0,
        },
    },
    'salmonella_nanopore.json': {
        'test_get_fastqc_stats': {
            'number_of_reads': 39514,
            'number_of_bases': 88900000,
            'reads_median_quality': 40.0,
            'reads_median_length': 0.0,
        },
    }


}

def load_json_content(json_path: Path):
    with open(json_path, 'r') as f:
        return json.load(f)

def test_get_fastqc_stats(json_file):
    content = load_json_content(json_file)

    result = {}
    if 'illumina' in str(json_file):
        result.update(get_fastqc_stats(content, "forward"))
        result.update(get_fastqc_stats(content, "reverse"))
    else:
        result.update(get_fastqc_stats(content, "forward"))

    expected = GOLDENS[json_file.name]['test_get_fastqc_stats']
    assert result == expected, f"{json_file.name}: FastQC stats output mismatch"
