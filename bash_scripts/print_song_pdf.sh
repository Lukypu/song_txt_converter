#!/usr/bin/env bash

set -e

TEX_PREAMBLE="$HOME/Personal/Kytara/Songbook/song_parser_and_formatter/latex_templates/one_song.tex"

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

TWO_COL=0

while getopts "ch" opt; do
  case "$opt" in
    c) TWO_COL=1 ;;
    h) exec "$0" --help ;;
  esac
done

shift $((OPTIND - 1))


inject_and_compile() {
  local preamble="$1"
  local tex_song="$2"
  local output="$3"

  local workdir
  workdir=$(mktemp -d)

  local song_tex="$workdir/song.tex"
  local preamble_mod="$workdir/main.tex"

  local out_dir
  out_dir=$(dirname "$output")
  mkdir -p "$out_dir"

  # write song file
  cp "$tex_song" "$song_tex"

  # inject \include{song} at line 50
 awk -v twocol="$TWO_COL" '
  /\\begin{document}/ {
    if (twocol == 1) {
      print "\\songcolumns{2}"
    }
    print
    print "\\include{song}"
    next
  }
  {print}
' "$preamble" > "$preamble_mod"

  echo "Compiling in: $workdir"

  pdflatex -interaction=nonstopmode \
           -output-directory="$workdir" \
           "$preamble_mod" >"$workdir/build.log" 2>&1

  # move result
  local pdf_name
  pdf_name=$(basename "${preamble_mod%.tex}.pdf")

  mv "$workdir/$pdf_name" "$output" 2>/dev/null || true

  # cleanup
  rm -rf "$workdir"
}


# ----------- main loop -----------
for pattern in "$@"; do
  for file in $pattern; do
    echo $file
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
        if ! inject_and_compile "$TEX_PREAMBLE" "$file" "$out"; then
          echo "Failed to process: $file"
        fi
        ;;
      crd|chord|chordpro)
        if [ "$TWO_COL" -eq 0 ]; then
          chordpro $file --cfg myconfig.json -o $out
        elif [ "$TWO_COL" -eq 1 ]; then
          chordpro $file --cfg myconfig2.json -o $out
        fi
        ;;
      *)
        echo "Skipping unsupported file: $file"
        ;;
    esac
  done
done

