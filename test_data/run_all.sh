#!/bin/bash
# Generate all test data .aep files using After Effects on macOS.
# Detects installed AE versions and runs against the first found.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT_PATH="${SCRIPT_DIR}/run_all.jsx"

AE_APP=""

for VERSION in 2026 2025 2024; do
    APP_PATH="/Applications/Adobe After Effects ${VERSION}/Adobe After Effects ${VERSION}.app/Contents/MacOS/AfterFX"
    if [ -f "$APP_PATH" ]; then
        AE_APP="$APP_PATH"
        echo "Found After Effects ${VERSION}"
        break
    fi
done

if [ -z "$AE_APP" ]; then
    echo "ERROR: Could not find After Effects installation."
    echo "Run manually: /path/to/AfterFX -s \"\$.evalFile('${SCRIPT_PATH}')\""
    exit 1
fi

echo "Running test data generation..."
echo "AE Path: ${AE_APP}"
echo "Script: ${SCRIPT_PATH}"
echo

"$AE_APP" -s "\$.evalFile('${SCRIPT_PATH}')"

echo
echo "Done. Check test_data/output/ for generated .aep files."
echo "Check test_data/output/generation_log.txt for results."
