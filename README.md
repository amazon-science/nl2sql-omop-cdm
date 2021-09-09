# NL2SQL: Natural Language to SQL Queries Tool

IMPORTANT: READ SECTION 2.1 TO USE THE UI.

This repo contains the UI tool and ML model development process to convert natural language questions to SQL queries. At the root level, it contains the following folders/files:

* `setup`: Directory that contains scripts/files to setup the development environment.
* `src`: All the source code related to the development of the end-to-end ML pipeline for the NL2SQL project. 
* `nl2sql_main.ipynb`: The UI tool (notebook) to run the model inference and query execution graphically.

In the following sections, we will cover:

1. Environment setup  
2. Getting started  
    2.1 Using the UI  
    2.2 Iterating on the underlying ML model

## 1. Environment setup

Note: The pipeline has been tested in Amazon's SageMaker Linux instance. It assumes that:

* You are in a GPU instance with CUDA 11.0, especially for model training. To setup the conda environment and install the remaining python packages, please change the directory to `setup/` and run `setup.sh` script. You first need to change the bash file mode if needed. Instructions to complete setup are as follows:

```bash
$ /bin/bash cd setup/
$ /bin/bash chmod +x setup.sh
$ /bin/bash ./setup.sh
```

The setup can take a few minutes. Once finalized, you will have the `conda_nl2sql_environment` conda environment to run this repo.

## 2. Getting started

This section covers how this repo is intended to be used. 

### 2.1. Using the UI

To run the UI tool and test the pipeline, it's assumed that you already have the trained model ready and your notebook instance is already connected to the Redshift database. To run the tool, follow the steps below:
* Open `src/config.py` and UPDATE THE MODEL PATH AND REDSHIFT DATABASE CONFIGURATION.
* Open `nl2sql_main.ipynb` and change the python kernel into `conda_nl2sql_environment`.
* Follow the instructions provided in the notebook.


### 2.2. Iterating on the underlying ML model

This section explains the T5-based model development process (training, inference and evaluation). The NL2SQL problem is defined as a text-to-text problem where the input is the question text and the output is the query template. In this project, T5-based model is fine-tuned with the NL2SQL dataset.

All the code related to the model development is located in `src/engine/step4/model_dev/`. Change your directory into this path:

```bash
$ /bin/bash cd src/engine/step4/model_dev/
```

### Data Preparation
**Note:** The dataset used in this project is hosted [here](https://github.com/OHDSI/Nostos). Please download the csv files and save them under the `data/folded_questions` path. In addition to the csv files, don't also forget to download [nonzero_args_by_query.json](nonzero_args_by_query.json) and save it in `data/` directory. This file contains sample values for the argumenents in the csv files.

Before you start model training, you need to have the data splits (train/validation/test) ready in CSV format. Each split has at least two columns (`unfolded_questions` for the input questions and `query` for the model's output query template.

The data csv files that were downloaded from the provided link contain the folded (compressed) version of the equivalent questions. So, you will need to unfold all the input equivalent questions for it to be ready for model development. Please open the `prepare_data.ipynb`, update the input and output data paths and run it.


### Model Training
In this project, T5 model that was pretrained with [WikiSQL dataset](https://github.com/salesforce/WikiSQL) was used for model fine-tuning. To fine-tune the [WikiSQL pretrained T5 model](https://huggingface.co/mrm8488/t5-small-finetuned-wikiSQL), you first need to update the model configuration file `t5_config.py`. Especially, you need to specify the input `data_dir` and `output_dir` for input data and model output directory respectively. At least, you need to update the following:
* model path
* database schema name
* Redshift database information (e.g., endpoint, database name, etc.)

Once you update the config file, run the following command to fine-tune the T5 model:

```bash
$ /bin/bash python t5_training.py
```

Note: As the T5 model is big, you will need GPU instances for training.


### Model Inference
To test the trained model and run inference for a single input question, you can use `t5_inference.py`. First open the file and update the model path and input question.

To run the inference script, run the command below:

```bash
$ /bin/bash python t5_inference.py
```


### Model Evaluation
Finally, you can also run the inference on the whole validation and test sets and compute the model performance (exact-matching and execution accuracies). You can use `t5_evaluation.py` to run the whole dataset inference and compute accuracies. First you need to open the file and update the data path, model path and output directory. And then you can run the following command to run the script:

```bash
$ /bin/bash python t5_evaluation.py
```

Please note that the whole data inference is compute intensive. And you may need an instance with multiple GPUs.


### Model Performance Metrics
In this project, there are two metrics used to evaluate the model:

1. Exact-matching (Logical-form) Accuracy: 
The percentage of the predicted queries having the exact match with the ground truth queries.

2. Execution Accuracy: 
The percentage of the predicted queries, when executed, result in the correct result.


To get more info about the NL2SQL tool, please refer to [this nl2sql-tool doc](nl2sql-tool.md).

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) License. See the [LICENSE](LICENSE) file.
