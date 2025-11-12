#!/usr/bin/env python3
import argparse
import os
import json
from collections import defaultdict
from typing import List, Tuple, Dict
from Bio import SeqIO
from Bio.Align import PairwiseAligner
from pathlib import Path


def seq_identity(a: str, b: str) -> float:
    aligner = PairwiseAligner()
    a = a.upper();
    b = b.upper()

    # skip calculations for identical sequences
    if a == b or (not a and not b):
        return 1.0

    aln = aligner.align(a, b)[0]

    matches = float(aln.score)
    return matches / max(len(a), len(b))


def find_identical_sequences(fasta_file: str) -> List[List[str]]:
    """Fast path for threshold == 1.0."""
    seq_dict = defaultdict(set)
    for record in SeqIO.parse(fasta_file, "fasta"):
        seq_str = str(record.seq).upper()
        seq_dict[seq_str].add(record.id)
    identical_groups = [sorted(list(ids)) for ids in seq_dict.values() if len(ids) > 1]
    return identical_groups


def cluster_by_threshold(fasta_file: str, threshold: float) -> List[List[str]]:
    """
    Greedy clustering by representative:
    - Iterate sequences in FASTA order
    - Assign to the first cluster whose representative has identity >= threshold
    - Otherwise start a new cluster with this sequence as representative
    Returns: list of clusters as lists of IDs (first ID is the representative).
    """
    records = list(SeqIO.parse(fasta_file, "fasta"))
    if not records:
        return []
    reps: List[Tuple[str, str]] = []  # (rep_id, rep_seq)
    clusters: List[List[str]] = []

    for rec in records:
        sid = rec.id
        s = str(rec.seq).upper()
        placed = False
        for idx, (rep_id, rep_seq) in enumerate(reps):
            if seq_identity(s, rep_seq) >= threshold:
                clusters[idx].append(sid)
                placed = True
                break
        if not placed:
            reps.append((sid, s))
            clusters.append([sid])  # representative is first element

    return clusters

def write_identical_sequences(identical_groups: List[List[str]], basename: Path, file_prefix:str):
    output_file = basename / f"{file_prefix}_ident_seq.csv"

    with open(output_file, 'w') as f:
        for group in identical_groups:
            if len(group) > 1:
                f.write(",".join(group) + "\n")


def write_unique_fasta(clusters: List[List[str]], input_fasta: str, basename: Path, file_prefix:str):
    """
    Write one representative per cluster to FASTA. The representative
    is the first ID in each cluster (deterministic: FASTA order).
    """
    unique_file = basename  / f"{file_prefix}_unique.fasta"

    rep_ids = {group[0] for group in clusters if group}
    with open(unique_file, 'w') as f:
        for record in SeqIO.parse(input_fasta, "fasta"):
            if record.id in rep_ids:
                SeqIO.write(record, f, "fasta")
                rep_ids.remove(record.id)  # write each rep once

def write_clusters_json(clusters: List[List[str]], segment_name: str, file_prefix: str, basename: Path, threshold:float):

    out_json = {
        segment_name: {
            "threshold": threshold,
            "clusters": {}
        }
    }

    unique_file = basename  / f"{file_prefix}_sequence_clustering_data.json"

    for group in clusters:
        if not group:
            continue
        rep_id = group[0]
        out_json[segment_name]['clusters'][rep_id] = group[:]  # full member list
    with open(unique_file, "w", encoding="utf-8") as f:
        json.dump(out_json, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Identify identical sequences under certain threshold')
    parser.add_argument("-i", "--input", required=True, help="Plik wejściowy w formacie FASTA")
    parser.add_argument("-o", "--output_dir", default="results", help="Katalog wyjściowy na wyniki")
    parser.add_argument("--output_prefix", default="wyniki", help="Prefix added to all files created by this script")
    parser.add_argument(
        "-t", "--threshold", type=float, default=1.0,
        help="Próg identyczności w [0,1]"
    )
    parser.add_argument(
        "--segment_name", type=str, default='bacterial_genome',
        help="Segment name used to generate json output."
    )

    args = parser.parse_args()

    # double check threshold is betwen 0 and 1
    if not (0.0 <= args.threshold <= 1.0):
        raise SystemExit("ERROR: --threshold must be between 0.0 and 1.0")

    basename = Path(args.output_dir)
    basename.mkdir(parents=True, exist_ok=True)

    # Cluster
    if args.threshold == 1.0:

        groups = find_identical_sequences(args.input)

        all_ids = [rec.id for rec in SeqIO.parse(args.input, "fasta")]
        id_in_group = {x for g in groups for x in g}
        clusters = [g for g in groups]
        clusters.extend([[sid] for sid in all_ids if sid not in id_in_group])
    else:
        clusters = cluster_by_threshold(args.input, args.threshold)

    # CSV only cluster > 1 are written down
    write_identical_sequences(clusters, basename, args.output_prefix)

    # Unique representatives FASTA
    write_unique_fasta(clusters, args.input, basename,  args.output_prefix)

    # json output

    write_clusters_json(clusters = clusters,
                        segment_name = args.segment_name,
                        file_prefix=  args.output_prefix,
                        basename = basename,
                        threshold = args.threshold)

if __name__ == "__main__":
    main()
