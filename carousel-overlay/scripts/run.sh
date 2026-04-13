#!/bin/bash
# carousel-overlay/scripts/run.sh
# One-command runner for the carousel overlay pipeline.
#
# Usage:
#   bash scripts/run.sh --input ./frames --output ./output --captions assets/captions/episode-01.py
#
# All flags are optional — defaults shown below.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(dirname "$SCRIPT_DIR")"

INPUT="."
OUTPUT="./output"
CAPTIONS=""

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --input)    INPUT="$2";    shift 2 ;;
        --output)   OUTPUT="$2";   shift 2 ;;
        --captions) CAPTIONS="$2"; shift 2 ;;
        *) echo "Unknown flag: $1"; exit 1 ;;
    esac
done

# Validate
if [ -z "$INPUT" ] || [ ! -d "$INPUT" ]; then
    echo "Error: --input directory not found: $INPUT"
    exit 1
fi

if [ -n "$CAPTIONS" ] && [ ! -f "$CAPTIONS" ]; then
    echo "Error: --captions file not found: $CAPTIONS"
    exit 1
fi

mkdir -p "$OUTPUT"

# Build python command
PY_CMD="python \"$SCRIPT_DIR/overlay_engine.py\" --input \"$INPUT\" --output \"$OUTPUT\""
if [ -n "$CAPTIONS" ]; then
    PY_CMD="$PY_CMD --captions \"$CAPTIONS\""
fi

echo ""
echo "Carousel Overlay Pipeline"
echo "  Input:    $INPUT"
echo "  Output:   $OUTPUT"
echo "  Captions: ${CAPTIONS:-'(using default from overlay_engine.py)'}"
echo ""

eval $PY_CMD

echo ""
echo "Done. Frames saved to: $OUTPUT"
