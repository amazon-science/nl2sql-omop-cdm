#!/bin/bash

source activate pytorch_latest_p36
pip install -r requirements.txt
python -m spacy download en_core_web_sm