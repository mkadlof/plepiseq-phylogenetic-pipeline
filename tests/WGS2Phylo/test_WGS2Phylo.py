import json
from pathlib import Path
from WGS2Phylo import get_fastqc_stats, get_contaminations_bacteria, get_sequencing_summary_bacteria, get_amr_bacteria

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
        "test_get_contaminations_bacteria" : {
            'kraken2_species_main' : 'Campylobacter coli',
            'kraken2_species_secondary' : 'Campylobacter jejuni',
            'kraken2_species_main_value' : 72.7,
            'kraken2_species_secondary_value' : 2.04,

            'metaphlan_species_main': 'Campylobacter coli',
            'metaphlan_species_secondary': 'None',
            'metaphlan_species_main_value': 100.0,
            'metaphlan_species_secondary_value': 0,

            'kmerfinder_species_main': 'Campylobacter coli',
            'kmerfinder_species_secondary': 'Campylobacter jejuni',
            'kmerfinder_species_main_value': 80.78,
            'kmerfinder_species_secondary_value': 16.59,

        },
        "test_get_sequencing_summary_bacteria" : {
            'genome_length':  1744267,
            'contigs_number': 33,
            'average_coverage': 57.53,
            'N50' : 232219,
            'L50' : 3,
            'Ns_value' : 257

        },
        "test_get_amr_bacteria" : {'Azithromycin' : {'opornos' : 'oporny',
                                                     'czynnik_typ': 'mutacja_punktowa',
                                                     'czynnik_nazwa': '23S',
                                                     'czynnik_mutacja': 'r.2075A>G' },
                                   'Ciprofloxacin' : {'opornos' : 'oporny',
                                                     'czynnik_typ': 'mutacja_punktowa',
                                                     'czynnik_nazwa': 'gyrA',
                                                     'czynnik_mutacja': 'p.T86I' } ,
                                   'Clindamycin' : {'opornos' : 'oporny',
                                                     'czynnik_typ': 'mutacja_punktowa',
                                                     'czynnik_nazwa': '23S',
                                                     'czynnik_mutacja': 'r.2075A>G' },
                                   'Erythromycin' : {'opornos' : 'oporny',
                                                     'czynnik_typ': 'mutacja_punktowa',
                                                     'czynnik_nazwa': '23S',
                                                     'czynnik_mutacja': 'r.2075A>G' },
                                   'Chloramphenicol': {'opornos' : 'wrazliw',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' },
                                   'Tetracycline' : {'opornos' : 'oporny',
                                                     'czynnik_typ': 'gen',
                                                     'czynnik_nazwa': 'tet(O/32/O)',
                                                     'czynnik_mutacja': 'brak' },
                                   'Gentamicin' : {'opornos' : 'oporny',
                                                     'czynnik_typ': 'gen',
                                                     'czynnik_nazwa': "aph(2'')-Ib",
                                                     'czynnik_mutacja': 'brak' },
                                   'Nalidixic Acid' : {'opornos' : 'oporny',
                                                     'czynnik_typ': 'mutacja_punktowa',
                                                     'czynnik_nazwa': 'gyrA',
                                                     'czynnik_mutacja': 'p.T86I' }
        }

    },
    'campylo_nanopore.json': {
        'test_get_fastqc_stats': {
            'number_of_reads': 57088,
            'number_of_bases': 159600000,
            'reads_median_quality': 38.0,
            'reads_median_length': 2000.0,
        },
        "test_get_contaminations_bacteria" : {
            'kraken2_species_main' : 'Campylobacter coli',
            'kraken2_species_secondary' : 'Photobacterium leiognathi',
            'kraken2_species_main_value' : 81.29,
            'kraken2_species_secondary_value' : 11.05,


            'kmerfinder_species_main': 'Campylobacter coli',
            'kmerfinder_species_secondary': 'Campylobacter jejuni',
            'kmerfinder_species_main_value': 36.42,
            'kmerfinder_species_secondary_value': 10.7,

        },
        "test_get_sequencing_summary_bacteria" : {
            'genome_length':  1756767,
            'contigs_number': 3,
            'average_coverage': 36.91,
            'N50' : 1751062,
            'L50' : 1,
            'Ns_value' : 0

        },
        "test_get_amr_bacteria" : {'Azithromycin' : {'opornos' : 'oporny',
                                                     'czynnik_typ': 'mutacja_punktowa',
                                                     'czynnik_nazwa': '23S',
                                                     'czynnik_mutacja': 'r.2075A>G' },
                                   'Ciprofloxacin' : {'opornos' : 'wrazliw',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' } ,
                                   'Clindamycin' : {'opornos' : 'oporny',
                                                     'czynnik_typ': 'mutacja_punktowa',
                                                     'czynnik_nazwa': '23S',
                                                     'czynnik_mutacja': 'r.2075A>G' },
                                   'Erythromycin' : {'opornos' : 'oporny',
                                                     'czynnik_typ': 'mutacja_punktowa',
                                                     'czynnik_nazwa': '23S',
                                                     'czynnik_mutacja': 'r.2075A>G' },
                                   'Chloramphenicol': {'opornos' : 'wrazliw',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' },
                                   'Tetracycline' : {'opornos' : 'oporny',
                                                     'czynnik_typ': 'gen',
                                                     'czynnik_nazwa': 'tet(O)',
                                                     'czynnik_mutacja': 'brak' },
                                   'Gentamicin' : {'opornos' : 'wrazliw',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' },
                                   'Nalidixic Acid' : {'opornos' : 'wrazliw',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' }
        }
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
        "test_get_contaminations_bacteria" : {
            'kraken2_species_main' : 'Escherichia coli',
            'kraken2_species_secondary' : 'Escherichia albertii',
            'kraken2_species_main_value' : 11.73,
            'kraken2_species_secondary_value' : 0.14,

            'metaphlan_species_main': 'Escherichia coli',
            'metaphlan_species_secondary': 'None',
            'metaphlan_species_main_value': 100.0,
            'metaphlan_species_secondary_value': 0,

            'kmerfinder_species_main': 'Escherichia coli',
            'kmerfinder_species_secondary': 'None',
            'kmerfinder_species_main_value': 0.18,
            'kmerfinder_species_secondary_value': 0,

        },
        "test_get_sequencing_summary_bacteria" : {
            'genome_length':  5104809,
            'contigs_number': 238,
            'average_coverage': 44.98,
            'N50' : 96543,
            'L50' : 19,
            'Ns_value' : 241

        },
        "test_get_amr_bacteria" : {'Azithromycin' : {'opornos' : 'wrazliw',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' },
                                   'Ciprofloxacin' : {'opornos' : 'oporny',
                                                     'czynnik_typ': 'mutacja_punktowa',
                                                     'czynnik_nazwa': 'gyrA',
                                                     'czynnik_mutacja': 'p.S83A' } ,
                                   'Clindamycin' : {'opornos' : 'wrazliw',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' },
                                   'Erythromycin' : {'opornos' : 'wrazliw',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' },
                                   'Chloramphenicol': {'opornos' : 'wrazliw',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' },
                                   'Tetracycline' : {'opornos' : 'wrazliw',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' },
                                   'Gentamicin' : {'opornos' : 'wrazliw',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' },
                                   'Nalidixic Acid' : {'opornos' : 'oporny',
                                                     'czynnik_typ': 'mutacja_punktowa',
                                                     'czynnik_nazwa': 'gyrA',
                                                     'czynnik_mutacja': 'p.S83A' }
        }
    },
    'ecoli_nanopore.json': {
        'test_get_fastqc_stats': {
            'number_of_reads': 208819,
            'number_of_bases': 498500000,
            'reads_median_quality': 41.0,
            'reads_median_length': 0.0,
        },
        "test_get_contaminations_bacteria" : {
            'kraken2_species_main' : 'Escherichia coli',
            'kraken2_species_secondary' : 'Photobacterium leiognathi',
            'kraken2_species_main_value' : 55.3,
            'kraken2_species_secondary_value' : 8.76,


            'kmerfinder_species_main': 'Escherichia marmotae',
            'kmerfinder_species_secondary': 'Escherichia albertii',
            'kmerfinder_species_main_value': 18.49,
            'kmerfinder_species_secondary_value': 17.29,

        },
        "test_get_sequencing_summary_bacteria" : {
            'genome_length':  5267401,
            'contigs_number': 5,
            'average_coverage': 95.67,
            'N50' : 2017328,
            'L50' : 2,
            'Ns_value' : 0

        },
        "test_get_amr_bacteria" : {'Azithromycin' : {'opornos' : 'wrazliw',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' },
                                   'Ciprofloxacin' : {'opornos' : 'oporny',
                                                     'czynnik_typ': 'mutacja_punktowa',
                                                     'czynnik_nazwa': 'gyrA',
                                                     'czynnik_mutacja': 'p.S83A' } ,
                                   'Clindamycin' : {'opornos' : 'wrazliw',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' },
                                   'Erythromycin' : {'opornos' : 'wrazliw',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' },
                                   'Chloramphenicol': {'opornos' : 'wrazliw',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' },
                                   'Tetracycline' : {'opornos' : 'wrazliw',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' },
                                   'Gentamicin' : {'opornos' : 'wrazliw',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' },
                                   'Nalidixic Acid' : {'opornos' : 'oporny',
                                                     'czynnik_typ': 'mutacja_punktowa',
                                                     'czynnik_nazwa': 'gyrA',
                                                     'czynnik_mutacja': 'p.S83A' }
        }
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
        "test_get_contaminations_bacteria" : {
            'kraken2_species_main' : 'Salmonella enterica',
            'kraken2_species_secondary' : 'Escherichia coli',
            'kraken2_species_main_value' : 5.4,
            'kraken2_species_secondary_value' : 0.22,

            'metaphlan_species_main': 'Salmonella enterica',
            'metaphlan_species_secondary': 'None',
            'metaphlan_species_main_value': 100.0,
            'metaphlan_species_secondary_value': 0,

            'kmerfinder_species_main': 'Salmonella enterica',
            'kmerfinder_species_secondary': 'Escherichia coli',
            'kmerfinder_species_main_value': 93.96,
            'kmerfinder_species_secondary_value': 5.4,

        },
        "test_get_sequencing_summary_bacteria" : {
            'genome_length':  5004068,
            'contigs_number': 78,
            'average_coverage': 55.41,
            'N50' : 225224,
            'L50' : 7,
            'Ns_value' : 840

        },
        "test_get_amr_bacteria" : {'Azithromycin' : {'opornos' : 'wrazliw',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' },
                                   'Ciprofloxacin' : {'opornos' : 'wrazliw',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' } ,
                                   'Clindamycin' : {'opornos' : 'wrazliw',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' },
                                   'Erythromycin' : {'opornos' : 'wrazliw',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' },
                                   'Chloramphenicol': {'opornos' : 'wrazliw',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' },
                                   'Tetracycline' : {'opornos' : 'oporny',
                                                     'czynnik_typ': 'gen',
                                                     'czynnik_nazwa': 'tet(B)',
                                                     'czynnik_mutacja': 'brak' },
                                   'Gentamicin' : {'opornos' : 'wrazliw',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' },
                                   'Nalidixic Acid' : {'opornos' : 'wrazliw',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' }
        }
    },
    'salmonella_nanopore.json': {
        'test_get_fastqc_stats': {
            'number_of_reads': 39514,
            'number_of_bases': 88900000,
            'reads_median_quality': 40.0,
            'reads_median_length': 0.0,
        },
        "test_get_contaminations_bacteria" : {
            'kraken2_species_main' : 'brak',
            'kraken2_species_secondary' : 'brak',
            'kraken2_species_main_value' : -1,
            'kraken2_species_secondary_value' : -1,


            'kmerfinder_species_main': 'brak',
            'kmerfinder_species_secondary': 'brak',
            'kmerfinder_species_main_value': -1,
            'kmerfinder_species_secondary_value': -1,

        },
        "test_get_sequencing_summary_bacteria" : {
            'genome_length':  -1,
            'contigs_number': -1,
            'average_coverage': -1,
            'N50' : -1,
            'L50' : -1,
            'Ns_value' : -1

        },
        "test_get_amr_bacteria" : {'Azithromycin' : {'opornos' : 'brak_danych',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' },
                                   'Ciprofloxacin' : {'opornos' : 'brak_danych',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' } ,
                                   'Clindamycin' : {'opornos' : 'brak_danych',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' },
                                   'Erythromycin' : {'opornos' : 'brak_danych',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' },
                                   'Chloramphenicol': {'opornos' : 'brak_danych',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' },
                                   'Tetracycline' : {'opornos' : 'brak_danych',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' },
                                   'Gentamicin' : {'opornos' : 'brak_danych',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' },
                                   'Nalidixic Acid' : {'opornos' : 'brak_danych',
                                                     'czynnik_typ': 'brak',
                                                     'czynnik_nazwa': 'brak',
                                                     'czynnik_mutacja': 'brak' }
        }

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

def test_get_contaminations_bacteria(json_file):
    content = load_json_content(json_file)
    result = get_contaminations_bacteria(content)

    expected = GOLDENS[json_file.name]['test_get_contaminations_bacteria']

    assert result == expected, f"{json_file.name}: Contamination analysis output mismatch"

def test_get_sequencing_summary_bacteria(json_file):
    content = load_json_content(json_file)
    result = get_sequencing_summary_bacteria(content)

    expected = GOLDENS[json_file.name]['test_get_sequencing_summary_bacteria']

    assert result == expected, f"{json_file.name}: Sequencing summary analysis output mismatch"

def test_get_amr_bacteria(json_file):
    content = load_json_content(json_file)
    result = get_amr_bacteria(content)

    expected = GOLDENS[json_file.name]['test_get_amr_bacteria']

    assert result == expected, f"{json_file.name}: Sequencing summary analysis output mismatch"

