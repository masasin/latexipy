#!/usr/bin/env bash
set -e

script_dir=$(dirname -- "$(readlink -e -- "$BASH_SOURCE")")
cd $script_dir
python examples.py
pdflatex -shell-escape example.tex
