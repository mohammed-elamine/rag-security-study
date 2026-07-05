#!/usr/bin/env bash
# Build a report PDF from Markdown. Run from anywhere:
#   bash report/build_report.sh              # builds report.md -> report.pdf
#   bash report/build_report.sh report_fr.md # builds report_fr.md -> report_fr.pdf
set -euo pipefail
cd "$(dirname "$0")"   # the report/ directory (image paths are relative to here)

SRC="${1:-report.md}"
OUT="${SRC%.md}.pdf"

pandoc "$SRC" -o "$OUT" \
  --pdf-engine=xelatex \
  --highlight-style=tango

echo "Built $(pwd)/$OUT"
