#!/usr/bin/env bash

set -e

SCRIPT="$HOME/Personal/Kytara/Songbook/song_parser_and_formatter/main.py"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MINIMIZE=""

OUTPUT=""
INPUTS=()

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  cat << 'EOF'
Same as translate song but imidiately calls print_song_pdf.sh
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

        "$SCRIPT_DIR/translate_songs.sh" $file -o "$suf" $MINIMIZE
        "$SCRIPT_DIR/print_song_pdf.sh" ${parent_dir}/converted/${base}.${suf}
      
      done
    fi
 done
done