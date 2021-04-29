import pandas as pd
import numpy as np
import re
import spacy
from pipeline import nlq2SqlTool
import config


def acc_if(gt_col, pred_col, token=True):
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

    else:
        for ii in range(len_samples):
            if gt_col[ii] == pred_col[ii]:
                accuracy_if += 1

    accuracy_if = accuracy_if / len_samples

    return accuracy_if


def acc_ex(gt_col, pred_col, entites):
    """
    Compares if prediction is able to execute and if it is the same as gt executed.

    Args:
        gt_col (pd.core.series.Series or np.array):
        pred_col (pd.core.series.Series or np.array):
        entites (list): List of dictionaries with entities to be rendered to produce the final sql query needed to retrieve results from the DB.

    """
    if isinstance(gt_col, pd.core.series.Series):
        gt_col = gt_col.values
    if isinstance(pred_col, pd.core.series.Series):
        pred_col = pred_col.values

    assert len(gt_col) == len(pred_col) and len(pred_col) == len(entites), 'Length of Cols Not Equal'

    len_samples = len(gt_col)
    acc_is_able_to_execute = 0.
    accuracy_exec_comparison = 0.
    tool = nlq2SqlTool(config)
    for ii in range(len_samples):
        # render gt with parameters detected.
        rendered_query_gt = tool.render_template_query(gt_col[ii], entites[ii])

        # render prediction with parameters detected.
        rendered_query_pred = tool.render_template_query(pred_col[ii], entites[ii])

        # execute prediction gt. Have a try/error, If runs 1 else 0.
        try:
            table_pred = tool.execute_sql_query(rendered_query_pred)
            acc_is_able_to_execute += 1
        except:
            continue

        # exectue rendered gt
        table_gt = tool.execute_sql_query(rendered_query_gt)

        # compare tables of results (5 first rows). If match 1 else 0.
        table_gt = table_gt[:5]
        table_pred = table_pred[:5]

        if table_gt.equals(table_pred):
            accuracy_exec_comparison += 1

    acc_is_able_to_execute /= len(gt_col)
    accuracy_exec_comparison /= len(gt_col)

    return acc_is_able_to_execute, accuracy_exec_comparison


def arganalysis(arg_col):
    if isinstance(arg_col,pd.core.series.Series):
        arg_col = arg_col.values
    predefined_dict = {"ARG-DRUG":0,"ARG-CONDITION":0,"ARG- DOSAGE":0,"ARG-GENDER":0,"ARG-STATE":0,
                       "ARG-TIMEDAYS":0,"ARG-TIMEYEARS":0,"ARG-AGE":0,"join":0,'table':0}
    for ii in range(len(arg_col)):
        helper = arg_col[ii].replace('<',' ').replace('>',' ')
        tokens = helper.split(' ')
        for token in tokens:
            token = token.upper()
            # print(token)
            if token in predefined_dict:
                predefined_dict[token] +=1
    return predefined_dict
