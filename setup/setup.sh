#!/bin/bash

echo "Creating nl2sql_environment environment ...."
KERNEL_NAME="nl2sql_environment"
PYTHON="3.6"

source activate JupyterSystemEnv

conda create --yes --name "$KERNEL_NAME" python="$PYTHON"
source activate $KERNEL_NAME

pip install --quiet ipykernel

source activate nl2sql_environment
conda env update --file environment.yml

echo "Installing dependencies in nl2sql_environment ...."
pip install -r pip_requirements.txt
python -m spacy download en_core_web_sm
