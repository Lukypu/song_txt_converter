#!/usr/bin/env bash

set -e

SCRIPT="$HOME/Personal/Kytara/Songbook/scripts/song_parser_and_formatter/main.py"
MINIMIZE=""

OUTPUT=""
INPUTS=()

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