#!/bin/bash
# Helper script to run the Streamlit app with the correct Python interpreter

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the project directory
cd "$SCRIPT_DIR"

# Run Streamlit using the venv Python
./venv/bin/python3 -m streamlit run app.py
