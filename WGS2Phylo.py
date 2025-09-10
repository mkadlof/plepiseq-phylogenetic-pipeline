import os
import json
import csv
import click

@click.command()
@click.option('--json-dir', required=True, type=click.Path(exists=True, file_okay=False),
              help="Directory containing sample subdirectories with JSON outputs.")
@click.option('--supplemental-file', type=click.Path(exists=True, readable=True), default=None,
              help="Optional TSV/CSV file with extra metadata (columns: date, region, country, division, city).")
@click.option('--id-column', default='id', show_default=True,
              help="Column name in the supplemental file that identifies the sample ID.")
@click.option('--output-prefix', default='metadata/metadata', show_default=True,
              help="Prefix for output files (aggregated will be <prefix>.tsv, per-sample will be <Sample>.<prefix>.tsv).")
@click.option('--extra-fields', multiple=True, default=[],
              help="Additional JSON fields to include as columns. NOT YET IMPLEMENTED")
def generate_metadata(json_dir, supplemental_file, id_column, output_prefix, extra_fields):
    """
    Generate a phylogenetic metadata TSV from pipeline JSON outputs.
    """
    # Define possible optional fields from supplemental file
    optional_fields = ["date", "region", "country", "division", "city"]
    optional_fields_present = []
    sup_data = {}

    # Read supplemental file if provided
    if supplemental_file:
        # Determine delimiter (infer from file extension or content)
        sup_ext = os.path.splitext(supplemental_file)[1].lower()
        if sup_ext in ('.tsv', '.tab'):
            delim = '\t'
        elif sup_ext == '.csv':
            delim = ','
        else:
            # Fallback: sniff by content
            with open(supplemental_file, 'r') as sf:
                first_line = sf.readline()
            delim = '\t' if first_line.count('\t') > first_line.count(',') else ','

        with open(supplemental_file, 'r') as sf:
            reader = csv.DictReader(sf, delimiter=delim)
            # Determine which of the optional fields are present (case-insensitive match)
            if reader.fieldnames:
                lower_fields = [h.lower().strip() for h in reader.fieldnames]
                for field in optional_fields:
                    if field in lower_fields:
                        optional_fields_present.append(field)
                    else:
                        # check case variants
                        for lf in lower_fields:
                            if lf == field:
                                optional_fields_present.append(field)
                                break
                # Preserve the order defined in optional_fields
                optional_fields_present = [f for f in optional_fields if f in optional_fields_present]
            # Build a dict mapping sample ID to that sample's metadata (for the fields present)
            for row in reader:
                # Identify sample ID using the specified id_column
                sample_id = row.get(id_column) or row.get(id_column.capitalize()) or row.get(id_column.lower())
                if not sample_id:
                    continue
                sample_id = str(sample_id)
                sup_data[sample_id] = {}
                for field in optional_fields_present:
                    # find the actual value from the row (case-insensitive key)
                    val = None
                    for col, value in row.items():
                        if col.lower() == field:
                            val = value.strip() if isinstance(value, str) else value
                            break
                    # Use None for empty values
                    sup_data[sample_id][field] = val if val not in ['', None] else None

    # Prepare output directory (if output_prefix includes a path, create dirs as needed)
    out_dir = os.path.dirname(output_prefix)
    base_name = os.path.basename(output_prefix)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    # Open drop log file
    drop_log_path = os.path.join(out_dir, "metadata_drop.txt") if out_dir else "metadata_drop.txt"
    drop_log = open(drop_log_path, 'w')

    # Prepare aggregated output file
    agg_path = os.path.join(out_dir, f"{base_name}.tsv") if out_dir else f"{base_name}.tsv"
    agg_file = open(agg_path, 'w', newline='')
    writer = csv.writer(agg_file, delimiter='\t')

    # Construct header: required + optional + extra fields
    header = ["strain", "Serovar", "MLST", "cgMLST", "HC5", "HC10"]
    header += optional_fields_present
    header += list(extra_fields)
    writer.writerow(header)

    # Iterate through sample subdirectories
    for sample in os.listdir(json_dir):
        sample_dir = os.path.join(json_dir, sample)
        if not os.path.isdir(sample_dir):
            continue
        sample_id = sample
        json_file = os.path.join(sample_dir, f"{sample}.json")
        if not os.path.isfile(json_file):
            drop_log.write(f"{sample_id} - JSON file not found\n")
            continue

        # Load JSON data
        try:
            with open(json_file, 'r') as jf:
                data = json.load(jf)
        except Exception as e:
            drop_log.write(f"{sample_id} - JSON parse error: {e}\n")
            continue

        output = data.get("output", data)  # if "output" is a top-level key, use it

        reasons = []  # accumulate drop reasons

        # Determine Serovar based on genus
        genus = output.get("pathogen_predicted_genus", "")
        species = output.get("pathogen_predicted_species", "")
        serovar = None
        if genus.lower() == "campylobacter":
            # Use genus + species as serovar if available
            if species:
                serovar = species
                if not serovar.lower().startswith(genus.lower()):
                    serovar = f"{genus}_{species}"
            else:
                reasons.append("Species not found for Campylobacter")
        elif genus.lower() == "escherichia":
            ser = None
            for entry in output.get("antigenic_data", []):
                if entry.get("program_name") == "ectyper":
                    if entry.get("status") and entry.get("status").lower() == "tak":
                        ser = entry.get("serotype_name")
                    break
            if ser:
                serovar = ser
            else:
                reasons.append("E. coli serotype (ECTyper) not found")
        elif genus.lower() == "salmonella":
            ser = None
            for entry in output.get("antigenic_data", []):
                if entry.get("program_name") == "seqsero": # sistr can be used as an alternative source of serowvar info
                    if entry.get("status") and entry.get("status").lower() == "tak":
                        ser = entry.get("serotype_name")
                    break
            if ser:
                serovar = ser
            else:
                reasons.append("Salmonella serotype (SeqSero) not found")
        else:
            reasons.append(f"Unsupported genus {genus}")

        # Extract MLST and cgMLST entries
        mlst_id = None
        cgmlst_id = None
        hc5 = None
        hc10 = None
        mlst_data = output.get("mlst_data")
        if not mlst_data:
            reasons.append("MLST data missing")
        else:
            # Ensure mlst_data is iterable (could be list or single dict)
            entries = mlst_data if isinstance(mlst_data, list) else [mlst_data]
            mlst_entry = None
            cgmlst_entry = None
            for entry in entries:
                scheme = str(entry.get("scheme_name", "")).lower()
                if scheme.startswith("cgmlst"):
                    cgmlst_entry = entry
                elif scheme.startswith("mlst"):
                    mlst_entry = entry
            # Classical MLST
            if not mlst_entry:
                reasons.append("MLST result not found")
            else:
                if mlst_entry.get("status") and mlst_entry["status"].lower() != "tak":
                    reasons.append("MLST incomplete")
                else:
                    mlst_id_val = mlst_entry.get("profile_id")
                    if mlst_id_val in [None, "", "null"]:
                        reasons.append("MLST profile_id missing")
                    else:
                        mlst_id = str(mlst_id_val)
            # cgMLST
            if not cgmlst_entry:
                reasons.append("cgMLST result not found")
            else:
                if cgmlst_entry.get("status") and cgmlst_entry["status"].lower() != "tak":
                    reasons.append("cgMLST incomplete")
                else:
                    cg_id_val = cgmlst_entry.get("profile_id")
                    if cg_id_val in [None, "", "null"]:
                        reasons.append("cgMLST profile_id missing")
                    else:
                        cgmlst_id = str(cg_id_val)
                    # Get HierCC clusters
                    clusters = cgmlst_entry.get("hiercc_clustering_external_data", [])
                    hc5_val = hc10_val = None
                    for cluster in clusters:
                        if str(cluster.get("level")) == "5":
                            hc5_val = cluster.get("group_id")
                        elif str(cluster.get("level")) == "10":
                            hc10_val = cluster.get("group_id")
                    if hc5_val is None or hc10_val is None:
                        # If classification using Enterobase failed try using local classification maintained by PZH
                        clusters_int = cgmlst_entry.get("hiercc_clustering_internal_data", [])
                        for cluster in clusters_int:
                            if str(cluster.get("level")) == "5" and hc5_val is None:
                                hc5_val = cluster.get("group_id")
                            if str(cluster.get("level")) == "10" and hc10_val is None:
                                hc10_val = cluster.get("group_id")
                    if hc5_val is None or hc10_val is None:
                        reasons.append("HC5/HC10 cluster IDs missing")
                    else:
                        hc5 = str(hc5_val)
                        hc10 = str(hc10_val)

        # If any required data is missing or invalid, skip this sample
        if reasons:
            drop_log.write(f"{sample_id} - {'; '.join(reasons)}\n")
            continue

        # Assemble row data for this sample
        row = {
            "strain": sample_id,
            "Serovar": serovar,
            "MLST": mlst_id,
            "cgMLST": cgmlst_id,
            "HC5": hc5,
            "HC10": hc10
        }
        # Add supplemental fields if available
        for field in optional_fields_present:
            val = sup_data.get(sample_id, {}).get(field)
            row[field] = "" if val is None else str(val)
        # Add extra JSON fields if requested
        for field in extra_fields:
            value = output.get(field)
            # If not found in "output", check top-level (in case field is at root)
            if value is None and "output" in data:
                value = data.get(field)
            if value is None:
                row[field] = ""
            elif isinstance(value, (dict, list)):
                # Convert complex types to JSON string for safe TSV output
                row[field] = json.dumps(value, separators=(',', ':'))
            else:
                row[field] = str(value)

        # Write to aggregated TSV
        writer.writerow([row.get(col, "") for col in header])
        # Write individual sample TSV
        sample_out = os.path.join(out_dir, f"{sample_id}.{base_name}.tsv") if out_dir else f"{sample_id}.{base_name}.tsv"
        with open(sample_out, 'w', newline='') as sf:
            sw = csv.writer(sf, delimiter='\t')
            sw.writerow(header)
            sw.writerow([row.get(col, "") for col in header])

    # Close files
    agg_file.close()
    drop_log.close()

if __name__ == '__main__':
    generate_metadata()


