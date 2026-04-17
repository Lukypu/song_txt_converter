#!/usr/bin/env bash

set -e

show_help() {
  cat << 'EOF'
Usage:
  index_songs.sh <folder>

Description:
  Scans all files in the given folder and extracts metadata into CSV.

Extracted fields:
  - filename
  - Title   (line 1)
  - Artist  (line 2)
  - Language, Source, Date (Key: Value format)

Output:
  song_index.csv (created in current working directory)

Notes:
  - Only regular files are processed
  - Metadata keys are case-insensitive
EOF
}

# ---------- argument validation ----------
if [ "$#" -ne 1 ] || [ ! -d "$1" ]; then
  show_help
  exit 1
fi

input_dir="$1"
output="song_index.csv"

echo "filename;Title;Artist;Language;Source;Date" > "$output"

# ---------- main loop ----------
for file in "$input_dir"/*; do
  [ -f "$file" ] || continue

  filename=$(basename "$file")

  title=$(sed -n '1p' "$file")
  artist=$(sed -n '2p' "$file")

  language=$(grep -i "^Language[[:space:]]*:" "$file" | head -n1 | sed 's/^[^:]*:[[:space:]]*//')
  source=$(grep -i "^Source[[:space:]]*:" "$file" | head -n1 | sed 's/^[^:]*:[[:space:]]*//')
  date=$(grep -i "^Date[[:space:]]*:" "$file" | head -n1 | sed 's/^[^:]*:[[:space:]]*//')

  echo "${filename};${title};${artist};${language};${source};${date}" >> "$output"
done