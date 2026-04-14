#!/usr/bin/env bash

set -e

INPUT_DIR="$HOME/Downloads"
ORIGINAL_OUTPUT_DIR="$HOME/Personal/Kytara/Songbook"
OUTPUT_DIR="$HOME/Personal/Kytara/Songbook"
ASK_LANG=true
USE_LOGFILE=true
LOGFILE="$OUTPUT_DIR/song-list.log.csv"
REPLY="none"

# ----------- parse args -----------
while getopts "i:o:n:l" opt; do
  case $opt in
    i) INPUT_DIR="$OPTARG" ;;
    o) OUTPUT_DIR="$OPTARG" ;;
    n) ASK_LANG=false ;;
    l) USE_LOGFILE=false;;
    *) echo "Usage: $0 [-i input_dir] [-o output_dir] [-n (no prompt)] [-l (no logfile)]"; exit 1 ;;
  esac
done

# ----------- language selection -----------
choose_language() {
  local options=(english czech german slovak french spanish russian other none)

  echo "Choose language:"
  for i in "${!options[@]}"; do
    echo "$((i+1))) ${options[i]}"
  done

  while true; do
    read -rp "Enter number: " choice
    if [[ "$choice" =~ ^[1-9]$ ]]; then
      REPLY="${options[$((choice-1))]}"
      return
    fi
    echo "Invalid choice"
  done
}

# ----------- process files -----------
if $ASK_LANG; then
  choose_language
  lang=$REPLY
else
  lang="none"
fi


for file in "$INPUT_DIR"/*-*-*.txt; do
  [ -e "$file" ] || continue

  # ----------- insert language line (3rd line) -----------
  if [ "$lang" != "none" ]; then
    tmp_file=$(mktemp)
  
    awk -v lang="$lang" '
      NR==3 { print "language: " lang }
      { print }
    ' "$file" > "$tmp_file"
  
    mv "$tmp_file" "$file"
  fi

  # ----------- decide target dir -----------
  if [ "$OUTPUT_DIR" != "$ORIGINAL_OUTPUT_DIR" ]; then
    target="$OUTPUT_DIR"
  else
    case "$lang" in
      czech) target="$OUTPUT_DIR/czech/source" ;;
      english) target="$OUTPUT_DIR/english/source" ;;
      *) target="$OUTPUT_DIR/other_languages/source" ;;
    esac
  fi
  
  mkdir -p "$target"
  mv "$file" "$target/"

  if $USE_LOGFILE; then
    filename=$(basename "$file")
    today=$(date +%F)
    
    echo "${filename};${lang};${today}" >> "$LOGFILE"
  fi

done