#!/bin/bash
cd ~/SageMaker/merck_nl2sql/
source activate pytorch_p36
pip install --upgrade torch torchvision
pip install -r requirements.txt
python -m spacy download en_core_web_sm