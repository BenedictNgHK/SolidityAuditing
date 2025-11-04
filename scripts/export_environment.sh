#!/bin/bash

# Export Environment Script for Solidity Auditing Tool
# This script helps export the current conda environment to environment.yml

set -e

ENV_NAME="solidity-auditing"
ENV_FILE="environment.yml"

echo "🔧 Exporting conda environment '$ENV_NAME' to $ENV_FILE..."

# Check if environment exists
if ! conda env list | grep -q "^$ENV_NAME "; then
    echo "❌ Environment '$ENV_NAME' not found. Please create it first:"
    echo "   conda env create -f environment.yml"
    exit 1
fi

# Export the environment
conda env export -n "$ENV_NAME" > "$ENV_FILE"

echo "✅ Environment exported to $ENV_FILE"

# Clean up the export (remove build-specific hashes for better reproducibility)
sed -i.bak \
    -e '/^prefix:/d' \
    -e 's/=[a-f0-9]\{16,\}/=*/g' \
    "$ENV_FILE" && rm "${ENV_FILE}.bak"

echo "🧹 Cleaned up build-specific hashes for better reproducibility"

# Display summary
echo ""
echo "📋 Environment Summary:"
echo "- Environment: $ENV_NAME"
echo "- Exported to: $ENV_FILE"
echo "- Python version: $(conda run -n $ENV_NAME python --version)"
echo "- Packages: $(conda list -n $ENV_NAME --export | wc -l) total"
echo ""
echo "💡 To recreate this environment:"
echo "   conda env create -f $ENV_FILE"
echo "   conda activate $ENV_NAME"
