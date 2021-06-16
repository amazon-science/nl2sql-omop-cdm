"""
The module performs the following tasks:
    - Get model inference for validation and test sets.
    - Compute the model's exact-matching and execution accuracies
"""

import os
from os import path as osp
import sys
import json

sys.path.append('../')

import math

import torch
import pandas as pd
from t5_tuning.model import T5FineTuner
from t5_tuning.t5_config import model_params
import src.config as config
from src.pipeline import nlq2SqlTool
import argparse


import torch.multiprocessing as mp
from torch.multiprocessing import Pool, Process, set_start_method
from utils_metrics import compute_wiki_acc_by_obs, get_metrics

import warnings
warnings.filterwarnings("ignore")


def load_model(fp):
    """
    Loads trained T5 models from a checkpoint file.
    
    Args:
        fp(str): Checkpoint file path.
    
    Returns:
        T5FineTuner object with the loaded weights.
    """
    if torch.cuda.is_available():
        checkpoint = torch.load(fp)
    else:
        checkpoint = torch.load(fp, map_location=torch.device('cpu'))

    args = argparse.Namespace(**checkpoint['hyper_parameters'])
    model = T5FineTuner(args)
    model.load_state_dict(checkpoint['state_dict'])
    return model


def get_query_length(model, df, max_length=1000):
    """
    Get output length of each query.
    
    Args:
        model(T5FineTuner): Model to be used.
        df(pd.DataFrame): Data with the queries.
        max_length(int): Max length of a query.
        
    Returns:
        List of query lengths.
    """
    target_tensors = model.tokenizer.batch_encode_plus(df['query'].values.tolist(), 
                                             max_length=max_length,
                                             padding='max_length', 
                                             truncation=True, 
                                             return_tensors="pt")

    lengths = target_tensors['attention_mask'].numpy().sum(1)
    return lengths


def acc_if_v2(gt_col, pred_col, token=True):
    """
    Args
        gt_col (pd.core.series.Series or np.array):
        pred_col (pd.core.series.Series or np.array):
        token (bool): Whether or not to compare as tokens (if False will be compared as full sentences)

    Retruns:
        float:
    """
    if isinstance(gt_col, pd.core.series.Series):
        gt_col = gt_col.values
    if isinstance(pred_col, pd.core.series.Series):
        pred_col = pred_col.values

    assert len(gt_col) == len(pred_col), 'Length of Cols Not Equal'

    len_samples = len(gt_col)
    accuracy_if = 0.
    accuracies = []

    if token:
        nlp = spacy.load("en_core_web_sm")
        pattern = r'[()]'
        for ii in range(len_samples):
            gt_col_idx = re.sub(pattern, '', gt_col[ii])
            gt_li = nlp(gt_col_idx)
            gt_tok = [i.text for i in gt_li]

            pred_col_idx = re.sub(pattern, '', pred_col[ii])
            pred_li = nlp(pred_col_idx)
            pred_tok = [i.text for i in pred_li]

            if np.array_equal(gt_tok, pred_tok):
                accuracy_if += 1
                accuracies.append(1.)
            else:
                accuracies.append(0.)

    else:
        for ii in range(len_samples):
            if gt_col[ii] == pred_col[ii]:
                accuracy_if += 1
                accuracies.append(1.)
            else:
                accuracies.append(0.)

    accuracy_if = accuracy_if / len_samples

    return accuracy_if, accuracies


def do_inference(test_model, input_text, input_max_length=256, output_max_length=750):
    """
    Get inference of an input question based on the trained model.
    Args:
        test_model(T5FineTuner): Model to be used for inference.
        input_text(str): Input question.
        input_max_length(int): Max length of the input text (question).
        output_max_length(int): Max length of the output text (query).
        
    Returns:
        The inferred query template.
    """
    nlq = "translate English to SQL: %s" % input_text
    test_model.eval()
    
    inputs = test_model.tokenizer.batch_encode_plus([nlq], 
                                             max_length=input_max_length,
                                             padding='max_length', 
                                             truncation=True, 
                                             return_tensors="pt")
    inputs = inputs.to('cuda')
    output = test_model.model.generate(
                    inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                    max_length=output_max_length, 
                    num_beams=2,
                    repetition_penalty=2.5, 
                    length_penalty=1.0
                    )
    sql = [test_model.tokenizer.decode(ids) for ids in output][0]
    sql = (sql.replace('<pad>', '')
           .replace('</s>', '')
           .replace('[', '<')
           .replace(']', '>')
           .strip()
          )
    return sql


def do_inference_v2(row, test_model, input_max_length=256, output_max_length=750):
    """
    Get inference of an input question based on the trained model.
    Args:
        row(pd.Series): Input row with a single input question.
        test_model(T5FineTuner): Model to be used for inference.
        input_max_length(int): Max length of the input text (question).
        output_max_length(int): Max length of the output text (query).
        
    Returns:
        The inferred query template.
    """

    input_text = row['question']
    #nlq = "translate English to SQL: %s </s>" % input_text
    nlq = "translate English to SQL: %s" % input_text
    test_model.eval()
    
    print(f'Processing {input_text}...')
    
    inputs = test_model.tokenizer.batch_encode_plus([nlq], 
                                             max_length=input_max_length,
                                             padding='max_length', 
                                             truncation=True, 
                                             return_tensors="pt")
    inputs = inputs.to('cuda')
    output = test_model.model.generate(
                    inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                    max_length=output_max_length, 
                    num_beams=2,
                    repetition_penalty=2.5, 
                    length_penalty=1.0
                    )
    sql = [test_model.tokenizer.decode(ids) for ids in output][0]
    sql = (sql.replace('<pad>', '')
           .replace('</s>', '')
           .replace('[', '<')
           .replace(']', '>')
           .strip()
          )
    return sql


def do_inference_v3(model_test, val_df, name, device=1, input_max_length=256, output_max_length=750):
    """
    Get inferences of input questions for the whole dataframe based on the trained model.
    
    Args:
        test_model(T5FineTuner): Model to be used for inference.
        val_df(pd.DataFrame): Dataframe with the input questions.
        input_max_length(int): Max length of the input text (question).
        output_max_length(int): Max length of the output text (query).
        
    Returns:
        The inferred query template.
    """
    
    proc_input = ["translate English to SQL: %s" % input_text for input_text in val_df['unfolded_questions']]
    batch_size = 16
    model_test = model_test.to(f'cuda:{device}')
    model_test.eval()
    queries = []
    total = val_df.shape[0]
    with torch.no_grad():
        for i in range(0, len(proc_input), batch_size):
            print(f"{i}/{total} done")
            batch = proc_input[i:i+batch_size]
            inputs = model_test.tokenizer.batch_encode_plus(batch, 
                                                         max_length=input_max_length,
                                                         padding='max_length', 
                                                         truncation=True, 
                                                         return_tensors="pt")
            inputs = inputs.to(f'cuda:{device}')
            output = model_test.model.generate(
                            inputs["input_ids"],
                            attention_mask=inputs["attention_mask"],
                            max_length=output_max_length, 
                            num_beams=2,
                            repetition_penalty=2.5, 
                            length_penalty=1.0
                            )
            queries.extend([model_test.tokenizer.decode(ids) for ids in output])
    queries = [sql.replace('<pad>', '')
               .replace('</s>', '')
               .replace('[', '<')
               .replace(']', '>')
               .strip() for sql in queries]
    val_df[f'preds_{name}'] = queries
    model_test.to('cpu')
    return val_df


def do_inference_v4(args):
    """
    Get inferences of input questions based on the given args (for parallel inference).
    Args:
        args(tuple): Tuple model, dataframe and gpu device number, input and output max length.

    Returns:
        The list of the inferred queries templates.
    """

    model_test, df, device, input_max_length, ouput_max_length = args
    try:
        proc_input = ["translate English to SQL: %s" % input_text for input_text in df['unfolded_questions']]
        batch_size = 16
        model_test.eval()
        queries = []
        total = df.shape[0]
        with torch.no_grad():
            for i in range(0, len(proc_input), batch_size):
                print(f"{i}/{total} done")
                batch = proc_input[i:i+batch_size]
                inputs = model_test.tokenizer.batch_encode_plus(batch, 
                                                             max_length=input_max_length,
                                                             padding='max_length', 
                                                             truncation=True, 
                                                             return_tensors="pt")
                inputs = inputs.to(f'cuda:{device}')
                output = model_test.model.generate(
                                inputs["input_ids"],
                                attention_mask=inputs["attention_mask"],
                                max_length=ouput_max_length, 
                                num_beams=2,
                                repetition_penalty=2.5, 
                                length_penalty=1.0
                                )
                queries.extend(output.cpu().numpy().tolist())
        
        queries = model_test.tokenizer.batch_decode(queries)
        queries = [sql.replace('<pad>', '')
                   .replace('</s>', '')
                   .replace('[', '<')
                   .replace(']', '>')
                   .strip() for sql in queries]
        model_test.to('cpu')
    finally:
        pass
    
    return queries


def multi_proc_inference(model_path, df, input_max_length, output_max_length):
    """Multi-GPU Model Inference.
    
    Args:
        model_path(str): Model path.
        df(pd.DataFrame): Dataframe with the input questions.
        input_max_length(int): Max length of the input text (question).
        output_max_length(int): Max length of the output text (query).
        
    Returns:
        The list of inferred queries templates.    
    """
    #Get total gpus
    num_gpus = torch.cuda.device_count()
    devices = range(1, num_gpus)
    n_devices = len(devices)
    n_rows = df.shape[0]
    
    step = math.ceil(n_rows/n_devices)
            
    my_pool = mp.Pool(processes=n_devices)
    
    args = []
    j = 0
    for i in range(0, n_rows, step):
        df0 = df.iloc[i:i+step]
        
        model_test = load_model(model_path)

        device = devices[j]
        args.append((model_test.to(f'cuda:{device}'), df0, device))
        print(f'Device: {device}, rows: {df0.shape}')
        j += 1        
    
    results = my_pool.map(do_inference_v4, args)

    my_pool.close()
    my_pool.join()
    return results


def inference_wrapper(df, model_path, input_max_length, output_max_length):
    """Multi-GPU Model Inference Wrapper with computing accuracies.
    
    Args:
        df(pd.DataFrame): Dataframe with the input questions.
        model_path(str): Model path.
        input_max_length(int): Max length of the input text (question).
        output_max_length(int): Max length of the output text (query).
        
    Returns:
        Dataframe with the output queries and model accuracies for each output query.    
    """
    
    print('Processing the WikiSQL pretrained model inference...')
    queries = multi_proc_inference(model_path, df, input_max_length, output_max_length)
    queries = [item for sublist in queries for item in sublist]
    df['preds_wiki'] = queries

    #compute query length
    print('Computing the output query lengths....')
    model = load_model(model_path)
    model.to('cuda:1')
    df['query_length'] = get_query_length(model, df, output_max_length)
    
    #Compute exact matching accuracy
    print('Computing the exact matching accuracy...')
    avg_wiki, df['exact_match_wiki'] = acc_if_v2(df['query'], df['preds_wiki'], token=False)
    
    #Get the average exact matching accuracy grouped by input questions
    print('Getting exact matching accuracy grouped by base questions...')
    df_mean = df.groupby('base_question')[['exact_match_wiki']].mean().reset_index().rename(columns={'exact_match_wiki': 'avg_exact_wiki'})
    df = pd.merge(df, df_mean, how='inner', left_on='base_question', right_on='base_question')
    
    return df


if __name__ == '__main__':
    
    #Data Dir
    DATA_DIR = '/home/ec2-user/SageMaker/efs/data/pilot_nl2sql_dev/0607_final_data/splits/In-Scope/all/'

    #Trained T5 model checkpoint
    MODEL_PATH = '/home/ec2-user/SageMaker/efs/data/pilot_nl2sql_dev/0607_models/p4_v2/default/version_0/checkpoints/model_checkpoint-epoch=04-val_loss=0.000.ckpt'

    # Default Values for Arguments.
    ARGS_PATH = "/home/ec2-user/SageMaker/efs/data/pilot_nl2sql_dev/nonzer_args_by_query.json"

    # out folders
    inference_folder = osp.join(DATA_DIR, 'inferenced_p4_v2_epoch04')
    os.makedirs(inference_folder, exist_ok=True)
    metric_path = osp.join(inference_folder, 'metrics_results.csv')
  
    with open(ARGS_PATH, 'r') as fp:
        query2args = json.load(fp)
    
    try:
         set_start_method('spawn')
    except RuntimeError:
        pass
    
    #### INFERENCE ######
    
    ##### ----- VALIDATION ######
    
    DATA_PATH = os.path.join(DATA_DIR, 'validation.csv')
    inference_validation_out = os.path.join(inference_folder, 'validation.csv')
    
    print(f'Reading {DATA_PATH}...')
    val_df = pd.read_csv(DATA_PATH)

    val_df = inference_wrapper(val_df, MODEL_PATH)

    #Save the results
    print(f'Saving the results to {inference_validation_out}...')
    val_df.to_csv(inference_validation_out, index=False)

    print(f'Done! Total Predictions: {val_df.shape[0]}')
        
    ##### ----- TEST ######
    
    DATA_PATH = os.path.join(DATA_DIR, 'test.csv')
    inference_test_out = os.path.join(inference_folder, 'test.csv')
    
    print(f'Reading {DATA_PATH}...')
    test_df = pd.read_csv(DATA_PATH)

    test_df = inference_wrapper(test_df, MODEL_PATH)

    #Save the results
    print(f'Saving the results to {inference_test_out}...')
    test_df.to_csv(inference_test_out, index=False)

    print(f'Done! Total Predictions: {test_df.shape[0]}')
    
    
    #### Metric computation ######
    
    print('Computing and Saving Model Accuracies...')
    
    tool = nlq2SqlTool(config)
    
    validation_df_w_perf = compute_wiki_acc_by_obs(tool, val_df, query2args)
    test_df_w_perf = compute_wiki_acc_by_obs(tool, test_df, query2args)
    
    val_acc_if, val_acc_ex = get_metrics(validation_df_w_perf)
    test_acc_if, test_acc_ex = get_metrics(test_df_w_perf)
    
    
    # prepare & write df
    metrics_df_info = [
        {'metric': 'exact match', 'validation': val_acc_if, 'test': test_acc_if},
        {'metric': 'execution match', 'validation': val_acc_ex, 'test': test_acc_ex},
    ]
    metrics_df = pd.DataFrame(metrics_df_info)
    metrics_df.to_csv(metric_path, index=False)
    
    
