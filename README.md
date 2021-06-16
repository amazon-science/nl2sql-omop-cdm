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

## Model Development

This section explains the process of T5 model development process (training, inference and evaluation). The NL2SQL problem is defined as a text-to-text problem where the input is the question text and the output is the query template. In this project T5-based model is fine-tuned with the NL2SQL dataset.

### Data Preparation
Before you start model training, you need to have the data splits (train/validation/test) ready. Each split has at least two columns (`unfolded_questions` for the input questions and `query` for the model's output query template.

### Model Training
To fine-tune WikiSQL pretrained T5 model, you first need to update the model configuration file `ml_config.py`. Especially, you need to specify the input `data_dir` and `output_dir` for input data and model output directory respectively. Once you update the config file, run the following command the training script:

```bash
$ /bin/bash python t5_training.py
```

### Model Evaluation
Once the model is trained, you will need to run inference for both validation and test set, and compute the exact-matching and execution accuracies for both dataset splits.

Please note that there are two metrics used here:
* Exact matching accuracy
* Execution accuracy

Open `t5_performance.py` and update the model path, data dir, output dir, etc. Once you update, the model, you will need to run the following command to get the inferences and metrics:

```bash
$ /bin/bash python t5_performance.py
```


### Model Inference

