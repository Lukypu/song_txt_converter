#!/usr/bin/env bash

set -e

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  cat << 'EOF'
Usage:
  print_song_pdf.sh [OPTIONS] input_file(s)

Description:
  Converts .tex and .crd song files to PDF format.
  Output files are automatically placed in a "pdf" directory
  located in the parent directory of the input file.

Arguments:
  input_file(s)         One or more input files (wildcards allowed)

Options:
  -h, --help            Show this help message and exit

Behavior:
  - Only files with extensions ".tex" and ".crd" are processed
  - Output path is automatically determined as:
        <parent_dir>/pdf/<filename>.pdf

  - Example transformation:
        input:  path/to/tex/song.tex
        output: path/to/pdf/song.pdf

  - Output directory is created automatically if it does not exist

Examples:
  print_song_pdf.sh song.tex
  print_song_pdf.sh *.tex
  print_song_pdf.sh *.crd
  print_song_pdf.sh *.tex *.crd

Notes:
  - Conversion is performed via FUNCTION_TEX (must be implemented)
  - Files with unsupported extensions are skipped
  - Existing PDF files may be overwritten
EOF
  exit 0
fi

# ----------- main loop -----------
for pattern in "$@"; do
  for file in $pattern; do
    [ -e "$file" ] || continue

    filename=$(basename "$file")
    base="${filename%.*}"
    ext="${filename##*.}"

    input_dir=$(dirname "$file")
    parent_dir=$(dirname "$input_dir")

    out_dir="${parent_dir}/pdf"
    mkdir -p "$out_dir"

    out="${out_dir}/${base}.pdf"

    case "$ext" in
      tex)
        FUNCTION_TEX "$file" "$out"
        ;;
      crd|chord|chordpro)
        chordpro $file --cfg myconfig.json -o $out
        ;;
      *)
        echo "Skipping unsupported file: $file"
        ;;
    esac
  done
done