#!/usr/bin/env bash
if conda info --envs | grep -q "env-name"; then
    (>&2 echo "Environment exist. Ready to process.")
else
    (>&2 conda env create -f environment.yml)
fi

source activate env-name
export PYTHONIOENCODING=utf8
env | sed 's/=/:=/' | sed 's/^/export /'
