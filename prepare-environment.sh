#!/usr/bin/env bash
. /home/siulkilulki/pkgs/miniconda3/etc/profile.d/conda.sh
if conda info --envs | grep -q "polish-masses"; then
    (>&2 echo "Environment exist. Ready to process.")
else
    (>&2 conda env create -f environment.yml)
fi

conda activate polish-masses
export PYTHONIOENCODING=utf8
env | sed 's/=/:=/' | sed 's/^/export /'
