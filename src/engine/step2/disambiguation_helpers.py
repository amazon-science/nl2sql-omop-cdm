"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

SPDX-License-Identifier: CC-BY-NC-4.0
"""

import boto3
import re
import json
from os import path as osp

# test
from pprint import pprint


CM_CLIENT = boto3.client("comprehendmedical")
ETHNICITY_P = re.compile("(?i)\\b(not)\\b")


def load_dict2pattern(filepath):
    with open(filepath, "r") as fp:
        category2pattern = json.load(fp)
        out = {
            category: re.compile(pattern)
            for category, pattern in category2pattern.items()
        }
    return out


current_folder = osp.dirname(osp.abspath(__file__))
GENDER2STANDARD = load_dict2pattern(osp.join(current_folder, "gender2pattern.json"))
RACE2STANDARD = load_dict2pattern(osp.join(current_folder, "race2pattern.json"))
STATE2STANDARD = load_dict2pattern(osp.join(current_folder, "state2pattern.json"))

IDENTITY = lambda x: x


def _use_pattern_dict(name, standard2pattern):
    """Standarize a name based on pre-defined mappings and regex matching.

    Args:
        name (str): Name to be standarized.
        standard2pattern (dict): Dictionary where key are the standarized names and values are the matching patterns.

    Returns:
        str: Returns standarized name if found. Else '[NOT FOUND]-name'

    """
    for standard, pattern in standard2pattern.items():
        if re.match(pattern, name):
            return standard
    return f"[NOT FOUND]-{name}"

    # Error handeling
    standards = "".join([i[0] for i in standard2pattern])
    raise ValueError(
        f"Name {name} don't match any pattern in dict with standards: {standards}"
    )


def _gender_name2standard(gender_name):
    """Standarize gender names

    Args:
        gender_name (str): Non-standard gender name.

    Returns:
        str: standard gender name

    """
    return _use_pattern_dict(gender_name, GENDER2STANDARD)


def _race_name2standard(race_name):
    """Standarize race names

    Args:
        race_name (str): Non-standard race name.

    Returns:
        str: standard race name

    """
    return _use_pattern_dict(race_name, RACE2STANDARD)


def _ethnicity_name2standard(ethnicity_name):
    """Standarize ethnicity names

    Args:
        gender_name (str): Non-standard ethnicity name.

    Returns:
        str: standard ethnicity name

    """
    if re.search(ETHNICITY_P, ethnicity_name):
        return "Not Hispanic or Latino"
    else:
        return "Hispanic or Latino"


def _state_name2standard(state_name):
    """Standarize state names

    Args:
        gender_name (str): Non-standard gender name.

    Returns:
        str: standard gender name

    """
    return _use_pattern_dict(state_name, STATE2STANDARD)


def _use_function_for_options(entities, fun=IDENTITY):
    """Creates disambiguation options and default disambiguation based on `fun` for names in `entities`.

    Args:
        entities (dir): Non-standard gender name.
        fun (function): Function providing the disambiguation options for names in entities. Default to identity.

    Returns:
        dict: Input entities updated with disambiguation options and default disambiguation.

    """
    for entity in entities:
        entity["Options"] = [{"Code": fun(entity["Text"])}]
        entity["Query-arg"] = entity["Options"][0]["Code"]

    return entities


def add_gender_options(entities):
    """Add option on entities in the category "gender"

    Args:
        entities: List of entity records of category "gender"

    Returns:
        dict: List of entity records of category "gender" updated with options and default disambiguation.

    """
    return _use_function_for_options(entities, _gender_name2standard)


def add_race_options(entities):
    """Add option on entities in the category "race"

    Args:
        entities: List of entity records of category "race"

    Returns:
        dict: List of entity records of category "race" updated with options and default disambiguation.


    """
    return _use_function_for_options(entities, _race_name2standard)


def add_state_options(entities):
    """Add option on entities in the category "state"

    Args:
        entities: List of entity records of category "state"

    Returns:
        dict: List of entity records of category "state" updated with options and default disambiguation.

    """
    return _use_function_for_options(entities, _state_name2standard)


def add_ethnicity_options(entities):
    """Add option on entities in the category "ethnicity"

    Args:
        entities: List of entity records of category "ethnicity"

    Returns:
        dict: List of entity records of category "ethnicity" updated with options and default disambiguation.

    """
    return _use_function_for_options(entities, _ethnicity_name2standard)


# def add_dosage_options(entities):
#     """Add option on entities in the category "race"

#     Args:


#     Returns:


#     """
#     return _use_function_for_options(entities)


def add_time_options(entities):
    """Add option on entities in the category "TIMEDAYS" & "TIMEYEARS"

    Args:
        entities: List of entity records of category "TIMEDAYS" or "TIMEYEARS"

    Returns:
        dict: List of entity records of category "TIMEDAYS" & "TIMEYEARS" updated with options and default disambiguation.

    """
    return _use_function_for_options(entities)


# def add_age_options(entities):
#     """Add option on entities in the category "TIMEDAYS" & "TIMEYEARS"

#     Args:


#     Returns:


#     """
#     return _use_function_for_options(entities)


def add_condition_options(entities):
    """Add option on entities in the category "Condition"

    Args:
        entities: List of entity records of category "Condition"

    Returns:
        dict: List of entity records of category "Condition" updated with options and default disambiguation.

    """

    for entity in entities:
        response = CM_CLIENT.infer_icd10_cm(Text=entity["Text"])["Entities"]
        if response:
            options = response[0]["ICD10CMConcepts"]
            default = options[0]["Code"]
        else:
            options = [{"Score": -1.0, "Code": "-1", "Description": "N/A"}]
            default = "N/A"

        entity["Options"] = options
        entity["Query-arg"] = default

    return entities


def add_drug_options(entities):
    """Add option on entities in the category "Drug"

    Args:
        entities: List of entity records of category "Drug"

    Returns:
        dict: List of entity records of category "Drug" updated with options and default disambiguation.

    """
    for entity in entities:
        response = CM_CLIENT.infer_rx_norm(Text=entity["Text"])["Entities"]
        if response:
            result = response[0]
            options = result["RxNormConcepts"]
            default = options[0]["Code"]
        else:
            options = [{"Score": -1.0, "Code": "-1", "Description": "N/A"}]
            default = "N/A"
        entity["Options"] = options
        entity["Query-arg"] = default

    return entities
