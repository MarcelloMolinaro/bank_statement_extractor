#!/usr/bin/env bash
set -euo pipefail

# Create and activate a Python virtual environment, then install dependencies.

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found. Please install Python 3." >&2
  exit 1
fi

if [ ! -d .venv ]; then
  echo "Creating virtual environment at .venv..."
  python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing requirements..."
pip install -r requirements.txt

echo "Build complete. To activate: source .venv/bin/activate"


