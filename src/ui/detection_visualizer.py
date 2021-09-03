"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

SPDX-License-Identifier: CC-BY-NC-4.0
"""

from spacy import displacy
import re
from copy import deepcopy

renderer = displacy.EntityRenderer(options={})

renderer.colors = {
    "DRUG": "#7aecec",
    "CONDITION": "#bfeeb7",
    "AGE": "#feca74",
    "STATE": "#ff9561",
    "ETHNICITY": "#aa9cfc",
    "RACE": "#c887fb",
    "TIMEDAYS": "#bfe1d9",
    "TIMEYEARS": "#bfe1d9",
    "GENDER": "#e4e7d2",
}


def reformat_raw_entities(entities):
    """Reformat raw entities into an orderd list of names based
    on starting position rather than ordered by category.


    Args:
        entities (dict): Detected entities in a NLQ.

    Returns:
        list: List of dictionaries with entites information sorted by starting position.

    """
    out = [
        {
            "start": name_dict["BeginOffset"],
            "end": name_dict["EndOffset"],
            "label": category,
        }
        for category, name_dicts in entities.items()
        for name_dict in name_dicts
    ]
    out = sorted(out, key=lambda x: x["start"])
    return out


def prepare_visualization_input_for_raw_entities(text, entities):
    """Prepares detected entities and text to be ingested into the HTML visualization feature.


    Args:
        text (str): Natural Language Query.
        entities (dict): Detected entities in a NLQ.

    Returns:
        dict:

    """
    ents = reformat_raw_entities(entities)
    out = {
        "text": text,
        "ents": ents,
        "title": None,
        "settings": {"lang": "en", "direction": "ltr"},
    }
    return out


def get_reformatted_proc_entities(text, entities):
    """Reformat processed entities to be ingested in the HTML visualization feature.


    Args:
        text (str): Natural Language Query with disambiguations replaced by original name.
        entities (dict): Processed entities in text.

    Returns:
        list: List of positions of diambiguated names occur and their category sorted by starting position.

    """
    out = []
    for category, name_dicts in entities.items():
        for name_dict in name_dicts:
            repl_text = name_dict["Query-arg"]
            p = re.compile(f"(?i)\\b{repl_text}\\b")
            match = list(re.finditer(p, text))[0]
            out.append({"start": match.start(), "end": match.end(), "label": category})
    out = sorted(out, key=lambda x: x["start"])
    return out


def get_reformatted_nlq(text, entities):
    """Replace the `entities` names in `text` by their disambiguation option.


    Args:
        text (str): Natural Language Query
        entities (dict): Detected entities in a NLQ.

    Returns:
        str: Natural Language Query with replaced names by their disambiguation name.

    """
    out_text = deepcopy(text)
    for cat_entities in entities.values():
        for entity in cat_entities:
            orig_text = entity["Text"]
            p = re.compile(f"(?i)\\b{orig_text}\\b")
            repl_text = entity["Query-arg"]
            out_text = re.sub(p, repl_text, out_text)
    return out_text


def prepare_visualization_input_for_processed_entities(text, entities):
    """Prepares processed entities and text to be ingested into the HTML visualization feature.


    Args:
        text (str): Natural Language Query
        entities (dict): Processed entities in a NLQ.

    Returns:
        dict: Processed entities input to the HTML visualization feature.

    """
    text2 = get_reformatted_nlq(text, entities)
    ents = get_reformatted_proc_entities(text2, entities)
    out = {
        "text": text2,
        "ents": ents,
        "title": None,
        "settings": {"lang": "en", "direction": "ltr"},
    }
    return out
