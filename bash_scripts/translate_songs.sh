#!/usr/bin/env bash

set -e

SCRIPT="$HOME/Personal/Kytara/Songbook/song_parser_and_formatter/main.py"
MINIMIZE=""

OUTPUT=""
INPUTS=()

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  cat << 'EOF'
Usage:
  translate_songs.sh [OPTIONS] input_file(s)

Description:
  Wrapper script for processing song files via a Python backend.
  Supports batch processing, multiple output formats, and optional minimization.

Arguments:
  input_file(s)         One or more input files (wildcards allowed)

Options:
  -o "SUFFIXES"         Output specification.

                        1) Space-separated suffix list:
                           -o "txt tex crd"
                           Creates outputs in:
                             <parent_dir>/<suffix>/<filename>.<suffix>

                        2) Full output path:
                           -o path/to/output.tex
                           Writes directly to the specified file

  -m                    Enable minimize mode (passed to Python script)

  -h, --help            Show this help message and exit

Output behavior:
  - When suffixes are used, files are written to:
        parent_directory_of_input/<suffix>/

  - Filenames are preserved:
        input:  path/song.txt
        output: path/tex/song.tex

Examples:
  translate_songs.sh song.txt -o "tex txt"
  translate_songs.sh *.txt -o "crd"
  translate_songs.sh song.txt -o output/result.tex
  translate_songs.sh song.txt -o "tex" -m

Notes:
  - Suffixes may be given with or without leading dots (tex or .tex)
  - Multiple inputs are processed sequentially
  - Output directories are created automatically
EOF
  exit 0
fi
# ----------- parse args -----------
while [[ $# -gt 0 ]]; do
  case "$1" in
    -o)
      OUTPUT="$2"
      shift 2
      ;;
    -m)
      MINIMIZE="-m"
      shift
      ;;
    *)
      INPUTS+=("$1")
      shift
      ;;
  esac
done

if [[ -z "$OUTPUT" ]]; then
  echo "Error: -o required"
  exit 1
fi

# ----------- detect mode -----------
is_suffix=false

# if contains space OR no slash → treat as suffix list
if [[ "$OUTPUT" == *" "* || "$OUTPUT" != */* ]]; then
  is_suffix=true
fi

# ----------- process -----------
for input in "${INPUTS[@]}"; do
  for file in $input; do
    [ -e "$file" ] || continue

    filename=$(basename "$file")
    base="${filename%.*}"
    input_dir=$(dirname "$file")
    parent_dir=$(dirname "$input_dir")
    
    if $is_suffix; then
      read -ra suffixes <<< "$OUTPUT"
    
      for suf in "${suffixes[@]}"; do
        suf=${suf#.}
    
        # out_dir="${parent_dir}/${suf}"
        out_dir="${parent_dir}/converted"
        mkdir -p "$out_dir"
    
        out="${out_dir}/${base}.${suf}"
    
        echo "Processing: $file -> $out"
        "$SCRIPT" "$file" -o "$out" --csv "$parent_dir/song-list.csv" $MINIMIZE
      done
    
    else
      echo "Processing: $file -> $OUTPUT"
      "$SCRIPT" -i "$file" -o "$OUTPUT"
    fi 
  done
done