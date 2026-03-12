#!/usr/bin/env bash
#
# E2E data pipeline: download -> transform -> scorecard
#
# Usage: bash pipeline/run.sh
#        bash pipeline/run.sh --skip-download   (use cached CSVs)
#

set -euo pipefail
cd "$(dirname "$0")/.."

SKIP_DOWNLOAD=false
if [[ "${1:-}" == "--skip-download" ]]; then
    SKIP_DOWNLOAD=true
fi

echo "======================================="
echo "  Canada Central Plots — Data Pipeline"
echo "======================================="
echo ""

# Step 1: Download
if [ "$SKIP_DOWNLOAD" = false ]; then
    python3 pipeline/download.py
    echo ""
else
    echo "=== Skipping download (using cached data) ==="
    echo ""
fi

# Step 2: Transform CSVs to JSON
python3 pipeline/transform.py
echo ""

# Step 3: Compute scorecard
python3 pipeline/scorecard.py
echo ""

echo "======================================="
echo "  Pipeline complete!"
echo "  Output: data/*.json"
echo "======================================="
