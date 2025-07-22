#!/bin/bash

# Simplified script to run viral phylogenetic pipeline using SNP data

# required to run .nf script + "modules" should be a subdirectory

# docker images required to execute this pipeline
main_image="pzh_pipeline-phylo:latest" # main image used by phylogenetic pipeline

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
threshold_Ns=1.0 # Maksymalny odsetek N w genomie (liczba zmiennoprzecinkowa z przedziału [0, 1])
threshold_ambiguities=1.0 # Maksymalny odsetek symboli niejednoznacznych w genomie (liczba zmiennoprzecinkowa z przedziału [0, 1])
# Visualization
map_detail="city"  #  poziom hierarchii na mapie przypisany próbce. Możliwe wartości to country lub city.

# Usage function to display help
usage() {
    echo "Użycie: $0 --input_dir ŚCIEŻKA --input_type TYP --results_dir ŚCIEŻKA --profile TYP --metadata metadata.txt --genus Salmonella --results_prefix prefiks"
    echo
    echo "Skrypt uruchamia bakteryjny pipeline filogenetyczny oparty na danych SNP."
    echo
    echo "Wymagane parametry:"
    echo "  -i, --input_fasta ŚCIEŻKA       Ścieżka do katalogu z danymi wejściowymi Fasta (WYMAGANE)"
    echo "  -m, --metadata ŚCIEŻKA          Ścieżka do pliku metadata (WYMAGANE)"
    echo "  -g, --organism NAZWA            Rodzaj wirusa: sars-cov-2, influenza, rsv (WYMAGANE)"
    echo
    echo "Opcjonalne parametry:"
    echo "  -x, --profile NAZWA             Profil wykonania Nextflow (dozwolone: 'local' lub 'slurm', domyślnie: local)"
    echo "  --threads LICZBA                Liczba rdzeni CPU do wykorzystania (domyślnie: 36, wielkość musi byc iloczynem 12)"
    echo "  --threshold_Ns LICZBA           Maksymalny odsetek N w genomie (float z przedziału [0, 1]) (domyślnie: 1.0)"
    echo "  --threshold_ambiguities LICZBA  Maksymalny odsetek symboli niejednoznacznych w genomie (float z przedziału [0, 1]) (domyślnie: 1.0)"
    echo "  --main_image NAZWA:TAG          Obraz Docker zawierający narzędzia używane przez pipeline"
    echo "  --map_detail STR                Informacja czy na mapie próbka przypisana jest do poziomu kraju czy miasta"
    echo "                                  (dozwolone wartości 'country' lub 'city', domyślnie city)"
    echo "  -h, --help                      Show this help message"
    exit 1
}

# Parse arguments using GNU getopt
TEMP=$(getopt -o hi:m:g:o:x: \
--long input_fasta:,metadata:,organism:,results_dir:,profile:,threshold_Ns:,threshold_ambiguities:,main_image:,prokka_image:,map_detail:,help \
-n "$0" -- "$@")

if [ $? != 0 ]; then usage; fi
eval set -- "$TEMP"

# Parse args into variables
while true; do
  case "$1" in
    -m|--metadata) metadata="$2"; shift 2 ;;
    -i|--input_fasta) input_fasta="$2"; shift 2 ;;
    -g|--organism) organism="$2"; shift 2 ;;
    -x|--profile) profile="$2"; shift 2 ;;
    --threshold_Ns) threshold_Ns="$2"; shift 2 ;;
    --threshold_ambiguities) threshold_ambiguities="$2"; shift 2 ;;
    --main_image) main_image="$2"; shift 2 ;;
    --map_detail) map_detail="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    --) shift; break ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Check required arguments
if [[ -z "$metadata" || -z "$input_fasta" || -z "$organism" ]]; then
    echo "Błąd: brakuje wymaganych argumentów!"
    usage
fi

# 1. Check if input paths exist
if [ ! -f "$metadata" ]; then
    echo "Błąd: plik metadata '$metadata' nie istnieje."; exit 1
fi
if [ ! -f "$input_fasta" ]; then
    echo "Błąd: katalog wejściowy '$input_fasta' nie istnieje."; exit 1
fi

# 2. Check if Docker images exist locally
if ! docker image inspect "$main_image" > /dev/null 2>&1; then
    echo "Błąd: obraz Docker '$main_image' nie istnieje lokalnie."; exit 1
fi

# 3. Validate profile
if [[ "$profile" != "local" && "$profile" != "slurm" ]]; then
    echo "Błąd: nieprawidłowy profil Nextflow: '$profile'. Dozwolone: 'local', 'slurm'."; exit 1
fi

# 4. Validate genus
shopt -s nocasematch
if [[ ! "$organism" =~ ^(sars(-cov-2)?|influenza|influ|rsv)$ ]]; then
    echo "Błąd: nieprawidłowy organizm: '$organism'. Dozwolone: sars-cov-2, influenza, rsv."
    exit 1
fi
shopt -u nocasematch

# 7. Validate map_detail
if [[ "${map_detail}" != "country" && "${map_detail}" != "city" ]]; then
    echo "Błąd: nieprawidłowy typ danych wejściowych: '${map_detail}'. Dozwolone: city, country."; exit 1
fi

nextflow run nf_viral_phylogenetic_pipeline.nf \
       --input_fasta ${input_fasta} \
       --input_type ${inputType} \
       --metadata ${metadata}  \
       --organism ${organism} \
       --input_prefix ${results_prefix} \
       --threshold_Ns ${thresholdN} \
       --threshold_ambiguities ${thresholdAmbiguous} \
       --main_image ${main_image} \
       --map_detail ${map_detail} \
       -profile ${profile} 
