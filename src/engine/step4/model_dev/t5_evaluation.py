"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

SPDX-License-Identifier: CC-BY-NC-4.0
"""

"""
The module performs the following tasks:
    - Get model inference for validation and test sets.
    - Compute the model's exact-matching and execution accuracies
"""

import os
from os import path as osp
import sys
import json

sys.path.append("../../../")

import math

import torch
import pandas as pd
from utils.model import T5FineTuner

# from t5_config import model_params
import config
from engine.pipeline import nlq2SqlTool
import argparse
import getpass

import torch.multiprocessing as mp
from torch.multiprocessing import Pool, Process, set_start_method
from utils.metrics import *
from utils.model import load_model

import warnings

warnings.filterwarnings("ignore")


def do_inference(args):
    """
    Get inferences of input questions based on the given args (for parallel inference).
    Args:
        args(tuple): Tuple model, dataframe and gpu device number.

    Returns:
        The list of the inferred queries templates.
    """

    model_test, df, device = args
    try:
        proc_input = [
            "translate English to SQL: %s" % input_text
            for input_text in df["unfolded_questions"]
        ]
        batch_size = 16
        model_test.eval()
        queries = []
        total = df.shape[0]
        with torch.no_grad():
            for i in range(0, len(proc_input), batch_size):
                print(f"{i}/{total} done")
                batch = proc_input[i : i + batch_size]
                inputs = model_test.tokenizer.batch_encode_plus(
                    batch,
                    max_length=model_test.hparams.max_input_length,
                    padding="max_length",
                    truncation=True,
                    return_tensors="pt",
                )
                inputs = inputs.to(f"cuda:{device}")
                output = model_test.model.generate(
                    inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                    max_length=model_test.hparams.max_output_length,
                    num_beams=2,
                    repetition_penalty=2.5,
                    length_penalty=1.0,
                )
                queries.extend(output.cpu().numpy().tolist())

        queries = model_test.tokenizer.batch_decode(queries)
        queries = [
            sql.replace("<pad>", "")
            .replace("</s>", "")
            .replace("[", "<")
            .replace("]", ">")
            .strip()
            for sql in queries
        ]
        model_test.to("cpu")
    finally:
        pass

    return queries


def multi_proc_inference(model_path, df):
    """Multi-GPU Model Inference.

    Args:
        model_path(str): Model path.
        df(pd.DataFrame): Dataframe with the input questions.

    Returns:
        The list of inferred queries templates.
    """
    # Get total gpus
    num_gpus = torch.cuda.device_count()
    devices = range(1, num_gpus)
    n_devices = len(devices)
    n_rows = df.shape[0]

    step = math.ceil(n_rows / n_devices)

    my_pool = mp.Pool(processes=n_devices)

    args = []
    j = 0
    for i in range(0, n_rows, step):
        df0 = df.iloc[i : i + step]

        model_test = load_model(model_path)

        device = devices[j]
        args.append((model_test.to(f"cuda:{device}"), df0, device))
        print(f"Device: {device}, rows: {df0.shape}")
        j += 1

    results = my_pool.map(do_inference, args)

    my_pool.close()
    my_pool.join()
    return results


def inference_wrapper(df, model_path, tool, query2args_dict):
    """Multi-GPU Model Inference Wrapper with computing accuracies.

    Args:
        df(pd.DataFrame): Dataframe with the input questions.
        model_path(str): Model path.

    Returns:
        Dataframe with the output queries and model accuracies for each output query.
    """

    print("Processing the WikiSQL pretrained model inference...")
    queries = multi_proc_inference(model_path, df)
    queries = [item for sublist in queries for item in sublist]
    df["preds_wiki"] = queries

    # compute query length
    print("Computing the output query lengths....")
    model = load_model(model_path)
    model.to("cuda:1")
    df["query_length"] = get_query_length(model, df)

    # Compute exact matching accuracy
    print("Computing the exact-matching and execution accuracies...")
    df = get_metrics(tool, df, query2args_dict)

    return df


if __name__ == "__main__":

    # Data Dir
    DATA_DIR = "/home/ec2-user/SageMaker/efs/data/pilot_nl2sql_dev/0607_final_data/splits/In-Scope/sample_sizes/sampling_number_1/150/"

    # Trained T5 model checkpoint
    MODEL_PATH = (
        "/home/ec2-user/SageMaker/efs/deliverable_models/0607_wikisql_all_v0e4.ckpt"
    )

    # Default Values for Arguments.
    ARGS_PATH = (
        "/home/ec2-user/SageMaker/efs/data/pilot_nl2sql_dev/nonzer_args_by_query.json"
    )

    # out folders
    inference_folder = osp.join(DATA_DIR, "inferenced_p4_v2_epoch04_trial")
    os.makedirs(inference_folder, exist_ok=True)
    metric_path = osp.join(inference_folder, "metrics_results.csv")

    with open(ARGS_PATH, "r") as fp:
        query2args = json.load(fp)

    try:
        set_start_method("spawn")
    except RuntimeError:
        pass

    #### INFERENCE ######

    ##### ----- VALIDATION ######

    DATA_PATH = os.path.join(DATA_DIR, "validation.csv")
    inference_validation_out = os.path.join(inference_folder, "validation.csv")

    print(f"Reading {DATA_PATH}...")
    val_df = pd.read_csv(DATA_PATH)

    tool = nlq2SqlTool(config)

    user = input("Enter Redshift Database Username: ")
    password = getpass.getpass(prompt="Enter Redshift Datbase Password: ")

    tool.set_db_credentials(user, password)

    val_df = inference_wrapper(val_df, MODEL_PATH, tool, query2args)

    # Save the results
    print(f"Saving the results to {inference_validation_out}...")
    val_df.to_csv(inference_validation_out, index=False)

    print(f"Done! Total Predictions: {val_df.shape[0]}")

    ##### ----- TEST ######

    DATA_PATH = os.path.join(DATA_DIR, "test.csv")
    inference_test_out = os.path.join(inference_folder, "test.csv")

    print(f"Reading {DATA_PATH}...")
    test_df = pd.read_csv(DATA_PATH)

    test_df = inference_wrapper(test_df, MODEL_PATH, tool, query2args)

    # Save the results
    print(f"Saving the results to {inference_test_out}...")
    test_df.to_csv(inference_test_out, index=False)

    print(f"Done! Total Predictions: {test_df.shape[0]}")

    #### Average Metric computation ######

    print("Computing and Saving Model Average Accuracies...")

    val_acc_if, val_acc_ex = get_average_metrics(val_df)
    test_acc_if, test_acc_ex = get_average_metrics(test_df)

    # prepare & write df
    metrics_df_info = [
        {"metric": "exact match", "validation": val_acc_if, "test": test_acc_if},
        {"metric": "execution match", "validation": val_acc_ex, "test": test_acc_ex},
    ]
    metrics_df = pd.DataFrame(metrics_df_info)
    metrics_df.to_csv(metric_path, index=False)
