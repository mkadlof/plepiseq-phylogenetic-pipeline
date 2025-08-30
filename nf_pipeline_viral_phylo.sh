#!/bin/bash



# A function used to determine which column in metadatafile has a specific header
get_col_idx() {
    local col_name=$1
    local header_line=$2
    echo "$header_line" | awk -v name="$col_name" -F'\t' '{
        for (i=1; i<=NF; i++) {
            if ($i == name) {
                print i;
                exit
            }
        }
    }'
}



# required to run .nf script + "modules" should be a subdirectory

# docker images required to execute this pipeline
main_image="pzh_pipeline-phylo:latest" # main image used by phylogenetic pipeline

# Path to local copy of the repository, required to get path to modules
projectDir=""


## Nextflow executor (local or slurm)
profile="local"

# location of input data - USER-provided no defaults
input_fasta=""
metadata=""
organism="" # analyzed genus only Salmonella Escherichia and Campylobacter are currently supported

# output - localization of output + prefix added to all results
# as we aggregate multiple files we cannot "guess" it as e.g. we do for NGS pipeline
results_dir="./results"
results_prefix=""

# Pipeline-specific parameters with defaults
# Defaults are hardcoded in this script NOT in the .nf file
threshold_Ns=0.02 # Maksymalny odsetek N w genomie (liczba zmiennoprzecinkowa z przedziału [0, 1])
threshold_ambiguities=0 # Maksymalny odsetek symboli niejednoznacznych w genomie (liczba zmiennoprzecinkowa z przedziału [0, 1])
# Visualization
map_detail="city"  #  poziom hierarchii na mapie przypisany próbce. Możliwe wartości to country lub city.

# IQtree parameters (originally hardocded in iqtree.nf module)
model="GTR+G" # Model for raxml
bootstrap=1000 # Number of bootstraps for iqtree
min_support=75 # Minimum support for a branch to keep it in a tree
starting_trees=10 # Number of random initial trees

threads=30 # ilość wątków używanych maksymalnie przez pipeline

# Timetree parameters
clockrate="" #


# Usage function to display help
usage() {
    echo "Użycie: $0 --input_fasta ŚCIEŻKA --results_dir ŚCIEŻKA --results_prefix PREFIX --profile NAZWA --metadata metadata.txt --organism NAZWA --projectDir SCIEZKA "
    echo
    echo "Skrypt uruchamia pipeline filogenetyczny dla pelnogenomowych sekwncji wybrnaych wirusow"
    echo
    echo "Wymagane parametry:"
    echo "  -i, --input_fasta ŚCIEŻKA       Ścieżka do katalogu z danymi wejściowymi Fasta (WYMAGANE)"
    echo "  -m, --metadata ŚCIEŻKA          Ścieżka do pliku z metadanymi (WYMAGANE)"
    echo "  -g, --organism NAZWA            Rodzaj wirusa: sars-cov-2, influenza, rsv (WYMAGANE)"
    echo "  -p, --results_prefix PREFIX     Prefiks dodawany do wszystkich plików wynikowych (WYMAGANE)"
    echo "  -d, --projectDir SCIEZKA        Sciezka do katalogu z pobranym repozytorium"
    echo
    echo "Opcjonalne parametry:"
    echo "  -o, --results_dir ŚCIEŻKA       Katalog wynikowy (domyślnie: ./results)"
    echo "  -x, --profile NAZWA             Profil wykonania Nextflow (dozwolone: 'local' lub 'slurm', domyślnie: local)"
    echo "  --model MODEL                   Model substytucji dla IQ-Tree (domyślnie: GTR+G)"
    echo "  --bootstrap LICZBA              Liczba replikacji bootstrap dla IQ-Tree  (domyślnie: 1000)"
    echo "  --min_support LICZBA            Minimalne wsparcie gałęzi, by pozostała w końcowym drzewie (domyślnie: 75)"
    echo "  --starting_trees LICZBA         Liczba drzew startowych dla IQ-Tree  (domyślnie: 10)"
    echo "  --clockrate WARTOŚĆ             Stała szybkości zegara molekularnego do TimeTree; jeśli nie podana, szacowana z danych lub ustawiana na wartość domyślną dla rodzaju"
    echo "  --threads LICZBA                Liczba rdzeni CPU do wykorzystania (domyślnie: 30)"
    echo "  --threshold_Ns LICZBA           Maksymalny odsetek N w genomie (float z przedziału [0, 1]) (domyślnie: 0.02)"
    echo "  --threshold_ambiguities LICZBA  Maksymalny odsetek symboli niejednoznacznych w genomie (float z przedziału [0, 1]) (domyślnie: 0)"
    echo "  --main_image NAZWA:TAG          Obraz Docker zawierający narzędzia używane przez pipeline"
    echo "  --map_detail STR                Informacja czy na mapie próbka przypisana jest do poziomu kraju czy miasta"
    echo "                                  (dozwolone wartości 'country' lub 'city', domyślnie city)"
    echo "  -h, --help                      Show this help message"
    exit 1
}

# Parse arguments using GNU getopt
TEMP=$(getopt -o hi:m:g:o:x:p:d: \
  --long help,input_fasta:,metadata:,organism:,results_dir:,profile:,results_prefix:,projectDir:,\
model:,bootstrap:,min_support:,starting_trees:,threads:,threshold_Ns:,threshold_ambiguities:,\
main_image:,map_detail:,clockrate: -n "$0" -- "$@") || { usage; exit 1; }
eval set -- "$TEMP"

while true; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    -i|--input_fasta)         input_fasta="$2"; shift 2 ;;
    -m|--metadata)            metadata="$2"; shift 2 ;;
    -g|--organism)            organism="$2"; shift 2 ;;
    -o|--results_dir)         results_dir="$2"; shift 2 ;;
    -x|--profile)             profile="$2"; shift 2 ;;
    -p|--results_prefix)      results_prefix="$2"; shift 2 ;;
    -d|--projectDir)          projectDir="$2"; shift 2 ;;
    --model)                  model="$2"; shift 2 ;;
    --bootstrap)              bootstrap="$2"; shift 2 ;;
    --min_support)            min_support="$2"; shift 2 ;;
    --starting_trees)         starting_trees="$2"; shift 2 ;;
    --threads)                threads="$2"; shift 2 ;;
    --threshold_Ns)           threshold_Ns="$2"; shift 2 ;;
    --threshold_ambiguities)  threshold_ambiguities="$2"; shift 2 ;;
    --main_image)             main_image="$2"; shift 2 ;;
    --map_detail)             map_detail="$2"; shift 2 ;;
    --clockrate)              clockrate="$2"; shift 2 ;;
    --) shift; break ;;
    *) echo "Internal parsing error near '$1'"; usage; exit 1 ;;
  esac
done
# 1) Required presence
[ -n "$input_fasta" ]     || err "Missing --input_fasta"
[ -n "$metadata" ]        || err "Missing --metadata"
[ -n "$organism" ]        || err "Missing --organism"
[ -n "$results_prefix" ]  || err "Missing --results_prefix"




# 2) Paths
[ -e "$metadata" ]        || err "Metadata not found: $metadata"
[ -e "$input_fasta" ]     || err "Input FASTA path not found: $input_fasta"
[ -d "$results_dir" ]     || mkdir -p "$results_dir"
[ -d "$projectDir" ]      || err "Program dir not found: $projectDir"


# 3) Profile
case "$profile" in
  local|slurm) : ;;
  *) err "Invalid --profile '$profile' (allowed: local, slurm)";;
esac

# 4) Organism (case-insensitive)
shopt -s nocasematch
case "$organism" in
  sars-cov-2|sarscov2|sars[-_]?cov[-_]?2) organism="sars-cov-2" ;;
  influenza|influ)                        organism="influenza"  ;;
  rsv)                                    organism="rsv"        ;;
  *) err "Invalid --organism '$organism' (allowed: sars-cov-2, influenza, rsv)";;
esac
shopt -u nocasematch

# 5) Integers
[[ "$bootstrap" =~ ^[0-9]+$ ]]     || err "--bootstrap must be integer"
[[ "$min_support" =~ ^[0-9]+$ ]]    || err "--min_support must be integer"
[[ "$starting_trees" =~ ^[0-9]+$ ]] || err "--starting_trees must be integer"
[[ "$threads" =~ ^[0-9]+$ ]]       || err "--threads must be integer"

# 6) Floats in [0,1] for thresholds
is_float_0_1 () {
  local v="$1"
  [[ "$v" =~ ^([0-1]|0?\.[0-9]+|1\.0+)$ ]] || return 1
  awk "BEGIN{exit !($v>=0 && $v<=1)}" >/dev/null 2>&1
}
is_float_0_1 "$threshold_Ns" || err "--threshold_Ns must be float in [0,1]"
is_float_0_1 "$threshold_ambiguities" || err "--threshold_ambiguities must be float in [0,1]"

# 7) map_detail
case "$map_detail" in
  city|country) : ;;
  *) err "Invalid --map_detail '$map_detail' (allowed: city, country)";;
esac

# 8) Optional clockRate if provided: float >0
if [ -n "clockrate" ]; then
  [[ "clockrate" =~ ^[0-9]*\.?[0-9]+$ ]] || err "--clockrate must be a positive float"
  awk "BEGIN{exit !(clockrate>0)}" >/dev/null 2>&1 || err "--clockRate must be > 0"
fi

# Safegurads
# Check if metadata file contain all required columns i.e. strain, virus, date, country, city
# Throw an error if entries in a column specified as a safeguard_level are non unique

# Determine the safeguard level
safeguard_level="virus"
header=$(head -n 1 "$metadata")

# Find virus column
 --- Required metadata columns per README ---
strain_col=$(get_col_idx "strain" "$header")
if [ -z "$strain_col" ]; then
    echo "Błąd: Kolumna 'strain' nie znaleziona w metadanych."; exit 1
fi

virus_col=$(get_col_idx "virus" "$header")
if [ -z "$virus_col" ]; then
    echo "Błąd: Kolumna 'virus' nie znaleziona w metadanych."; exit 1
fi

date_col=$(get_col_idx "date" "$header")
if [ -z "$date_col" ]; then
    echo "Błąd: Kolumna 'date' nie znaleziona w metadanych."; exit 1
fi

country_col=$(get_col_idx "country" "$header")
if [ -z "$country_col" ]; then
    echo "Błąd: Kolumna 'country' nie znaleziona w metadanych."; exit 1
fi

city_col=$(get_col_idx "city" "$header")
if [ -z "$city_col" ]; then
    echo "Błąd: Kolumna 'city' nie znaleziona w metadanych."; exit 1
fi

# Checks depending on safeguard_level

if [ "$safeguard_level" = "virus" ]; then
    unique_virus=$(awk -v col="virus_col" -F'\t' 'NR>1 {print $col}' "$metadata" | sort | uniq | wc -l)
    if [ "unique_virus" -gt 1 ]; then
        echo "Błąd: Wykryto wiele identyfikatorow wirusa w metadanych. Program sluzy do analizy probek tego samego wirusa."; exit 1
    fi
fi


# ---------- Run Nextflow ----------
args=(
  "--input_fasta"           "$input_fasta"
  "--metadata"              "$metadata"
  "--organism"              "$organism"
  "--results_dir"           "$results_dir"
  "--results_prefix"         "$results_prefix"
  "--projectDir"            "$projectDir"
  "--model"                 "$model"
  "--bootstrap"             "$bootstrap"
  "--min_support"           "$min_support"
  "--starting_trees"        "$starting_trees"
  "--threads"               "$threads"
  "--threshold_Ns"          "$threshold_Ns"
  "--threshold_ambiguities" "$threshold_ambiguities"
  "--main_image"            "$main_image"
  "--map_detail"            "$map_detail"
)

# Append optional clockrate only if set
[ -n "${clockrate:-}" ] && args+=( "--clockrate" "$clockrate" )

# ---------- Run Nextflow ----------
set -x
nextflow run "${projectDir}/nf_viral_phylogenetic_pipeline.nf" -profile "$profile" "${args[@]}"