"""
Module to load and infer query from the given input question.


Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

SPDX-License-Identifier: CC-BY-NC-4.0
"""


import re
from os import path as osp
import argparse
from utils.model import T5FineTuner, load_model
import torch

PAD_P = re.compile("<pad> |</s>")


class Inferencer(object):
    def __init__(self, model_path):
        """Initialize model and tokenizer base on a pkl filepath.

        Args:
            model_path (str): Absolute path to the stored model.

        Returns:
            str: None

        """
        self.model = load_model(model_path)
        self.tokenizer = self.model.tokenizer

    def __call__(self, input_text):
        """Maps a general NLQ (with placeholders) to a general SQL query (with placeholders)

        Args:
            input_text (str): General Natural Language question text.

        Returns:
            str: Generic SQL Query.
        """
        input_text = "translate English to SQL: %s" % input_text

        features = self.tokenizer.batch_encode_plus(
            [input_text],
            max_length=self.model.hparams.max_input_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        output = self.model.model.generate(
            input_ids=features["input_ids"],
            attention_mask=features["attention_mask"],
            max_length=self.model.hparams.max_output_length,
            num_beams=2,
            repetition_penalty=2.5,
            length_penalty=1.0,
        )

        output = self.tokenizer.decode(output[0])

        # generic sql post-processing
        output = re.sub(PAD_P, "", output)
        output = output.replace("[", "<").replace("]", ">").strip()

        return output


if __name__ == "__main__":

    # Model location
    MODEL_PATH = (
        "/home/ec2-user/SageMaker/efs/deliverable_models/0607_wikisql_all_v0e4.ckpt"
    )

    # Model input text/question
    QUESTION = "Number of patients taking <ARG-DRUG><0>"

    inferencer = Inferencer(MODEL_PATH)

    sql = inferencer(QUESTION)

    print("Input Question: \n", QUESTION)
    print("Output Query Template: \n", sql)
