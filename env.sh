#!/bin/bash

CONDAENV=ai2-results-extraction

if ! (which conda); then
	echo "No `conda` installation found.  Installing..."
	if [[ $(uname) == "Darwin" ]]; then
	  wget --continue https://repo.continuum.io/miniconda/Miniconda3-4.3.31-Linux-x86_64.sh
	  bash Miniconda3-4.3.31-Linux-x86_64.sh -b
	else
	  wget --continue https://repo.continuum.io/miniconda/Miniconda3-4.3.31-MacOSX-x86_64.sh
	  bash Miniconda3-4.3.1-MacOSX-x86_64.sh -b
	fi
fi

export PATH=$HOME/miniconda3/bin:$PATH

source ~/miniconda3/bin/deactivate ${CONDAENV}

conda remove -y --name ${CONDAENV} --all

conda create -n ${CONDAENV} -y python=3.6 pytest || true

echo "Activating Miniconda Environment ----->"
source ~/miniconda3/bin/activate ${CONDAENV}

pip install -r requirements.txt
