"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.  

SPDX-License-Identifier: CC-BY-NC-4.0


The module contains util functions to compute the metrics of a trained model.
"""

import json
import numpy as np
import pandas as pd


def execute_matching(tool, row, entities):
    """
    Execute the true and predicted query of a give row.

    Args:
        tool(nlq2SqlTool):  Tool with the functions for the query is be rendered and executed.
        row: Row for a single query.
        entities(dict): Dictionary of specific values for the query arguments.

    Returns:
        True if the inferred query can be executed and returns the same as the true query. Otherwise, returns False.
    """

    base_question = row["base_question"]
    unfolded_question = row["unfolded_questions"]
    true_query = row["query"]
    pred_query = row["preds_wiki"]
    indx = int(row.name) + 1

    # Render & execute targets
    true_sql_query = tool.render_template_query(true_query, entities)
    true_output = tool.execute_sql_query(true_sql_query)
    #     print(true_output.iloc[:5])

    # Render & execute predictions
    try:
        pred_sql_query = tool.render_template_query(pred_query, entities)
        pred_output = tool.execute_sql_query(pred_sql_query)
    except:
        pred_output = None

    if pred_output is not None:
        # Fix the reordering of the output columns
        true_columns = true_output.columns.tolist()
        pred_columns = pred_output.columns.tolist()

        if set(true_columns) == set(pred_columns):
            pred_output = pred_output[true_columns]

    if pred_output is None:
        return 0

    true_first_c = true_output.columns[0]
    pred_first_c = pred_output.columns[0]

    true_output0 = true_output.sort_values(by=true_first_c).values
    pred_output0 = pred_output.sort_values(by=pred_first_c).values

    if true_query == pred_query or np.array_equal(true_output0, pred_output0):
        return 1.0
    else:
        return 0.0


def exact_matching(row, column):
    """
    Computes exact matching accuracy for a single row (query).

    Args:
        row(pd.Series): Data for a single row with the input and inferred queries.
        column(str): Column where the inferred query is stored.

    Returns:
        True if there is exact matching between the true and inferred queries. Otherwise, returns False.
    """

    if row["query"] == row[column]:
        return 1.0
    else:
        return 0.0


## Correct GT Query
def correct_gt_query(df):
    """
    Correct ground-truth query template.

    Args:
        df(pd.DataFrame): Input data in pandas dataframe format.

    Returns:
        Pandas DataFrame with the corrected queries.
    """

    old_query = "SELECT race, ethnicity, COUNT( DISTINCT pe1.person_id) FROM ((<SCHEMA>.person pe1 JOIN <RACE-TEMPLATE> ON pe1.race_concept_id=concept_id) JOIN <ETHNICITY-TEMPLATE> eth_temp1 ON pe1.gender_concept_id=eth_temp1.concept_id ) GROUP BY race, ethnicity ;"
    corrected_query = "SELECT race, ethnicity, COUNT( DISTINCT pe1.person_id) FROM ((<SCHEMA>.person pe1 JOIN <RACE-TEMPLATE> ON pe1.race_concept_id=concept_id) JOIN <ETHNICITY-TEMPLATE> eth_temp1 ON pe1.ethnicity_concept_id=eth_temp1.concept_id ) GROUP BY race, ethnicity ;"
    queries = df["query"].values.tolist()
    queries = [corrected_query if qry == old_query else qry for qry in queries]
    df["query"] = queries
    return df


def get_metrics(tool, df, query2args_dict):
    """
    Computes the exact matching and execution accuracies for each inferred query.

    Args:
        tool(nlq2SqlTool): Tool with the functions for the query is be rendered and executed.
        df(pd.DataFrame): Pandas dataframe where the input and inferred queries are stored.
        query2args_dict(dict): Dictionary of default arguments for the queries.

    Returns:
        Pandas dataframe with the calculated accuracies.
    """

    df["exact_match_wiki"] = df.apply(exact_matching, args=("preds_wiki",), axis=1)

    df0 = df.drop_duplicates(
        subset=["base_question", "query", "preds_wiki"], inplace=False
    ).reset_index(drop=True)
    exec_match_wiki = []
    for i, (_, row) in enumerate(df0.iterrows()):
        if i % 10 == 0:
            print(f"Executing {i}/{df0.shape[0]}...")
        exec_match_wiki.append(
            execute_matching(
                tool, row, query2args_dict.get(row["query"], query2args_dict["default"])
            )
        )

    df0["exec_match_wiki"] = exec_match_wiki

    columns = ["base_question", "query", "preds_wiki", "exec_match_wiki"]
    df1 = df0[columns]
    common = ["base_question", "query", "preds_wiki"]
    df_final = pd.merge(
        left=df, right=df1, how="inner", left_on=common, right_on=common
    )

    return df_final


def get_average_metrics(df):
    """
    Computes the average accuracies of the model.

    Args:
        df(pd.DataFrame): DataFrame with the accuracies per query.
    Returns:
        Tuple of the average exact-matching and execution accuracies.
    """
    acc_if = df.exact_match_wiki.mean()
    acc_ex = df.exec_match_wiki.mean()
    return acc_if, acc_ex


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
    target_tensors = model.tokenizer.batch_encode_plus(
        df["query"].values.tolist(),
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="pt",
    )

    lengths = target_tensors["attention_mask"].numpy().sum(1)
    return lengths
