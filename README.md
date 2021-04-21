# Merck: Natural Languge Queries to SQL queries

This repo contains the UI, tool, labeling material and ML modeling material developed as part of the ML Solutions Lab PoC for Merck. At the root level it is organized in 4 folders:

* `labeling`: 
* `src`: 
* `docs`: 
* `t5`: 

## Environment

The pipeline has been tested in Amazon's SageMaker `pytorch_p36` environment. It assumes:

* You are in a GPU instance with CUDA 11.0 (for different versions please update `spacy` in `requirements.txt` accordingly).
* Repo is located in the `~/SageMaker` folder. 

Instructions to complete set up are as follows:

```bash
$ /bin/bash set_up.sh
```