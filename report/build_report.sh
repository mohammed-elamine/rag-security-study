#!/usr/bin/env bash
# Build report.pdf from report.md. Run from anywhere: bash report/build_report.sh
set -euo pipefail
cd "$(dirname "$0")"   # the report/ directory (image paths are relative to here)

pandoc report.md -o report.pdf \
  --pdf-engine=xelatex \
  --highlight-style=tango

echo "Built $(pwd)/report.pdf"
