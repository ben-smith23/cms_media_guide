#!/bin/bash
# Script to run the LaTeX generator with virtual environment
cd "$(dirname "$0")"
source venv/bin/activate
python cms_media_guide/generate_latex.py
echo "Generated LaTeX saved to: latex/sections/generated_latex.tex"
