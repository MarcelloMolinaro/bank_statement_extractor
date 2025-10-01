#!/usr/bin/env bash
set -euo pipefail

# Run the extractor using the project's virtual environment.
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

if [ ! -d .venv ]; then
  echo ".venv not found. Run ./build.sh first." >&2
  exit 1
fi

source .venv/bin/activate
python src/extract.py "$@"


