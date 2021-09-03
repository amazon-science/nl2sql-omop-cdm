"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

SPDX-License-Identifier: CC-BY-NC-4.0
"""

# Notes
#     Time has to be given in digits, not words. It can handle cases such as "24 days".
#     For the time being we are not looking at extracting time unit even though it will be a relatively easy simple
#     feature to extract -> will require one more placeholder <ARG-TIMEUNIT>


import re
from pprint import pprint

WORDS_P = re.compile("[A-Za-z]*")
DIGITS_P = re.compile("\d*")


def _reformat_cm_entity(entity):
    """Reformat Amazon's Comprehend Medical output to be handeled by the tool.


    Args:
        entity (dict): Entity dictionary from Amazon Comprehend Medical

    Returns:
        dict: Entity tool-standarized dictionary.
    """
    out = {
        "BeginOffset": entity["BeginOffset"],
        "EndOffset": entity["EndOffset"],
        "Text": entity["Text"],
        "Category": entity["Category"],
        "Type": entity["Type"],
    }
    return out


def _reformat_regex_entity(entity):
    """Reformat Regex entity to be handeled by the tool.

    Args:
        entity (dict): Entity dictionary from regex.

    Returns:
        dict: Entity tool-standarized dictionary.
    """
    out = {
        "BeginOffset": entity.start(),
        "EndOffset": entity.end(),
        "Text": entity.string[entity.start() : entity.end()],
    }
    return out


def _update_category_with_cm_record(entity, category_records, seen_names):
    """Update the category records with the passed entity and record seen names.

    Args:
        entity (dict): entity to be added to the category records.
        category_records (list): List of a category records.
        seen_names (set): Set of seen names.

    Returns:
        None
    """
    del entity["Category"]
    del entity["Type"]
    category_records.append(entity)
    seen_names.add(entity["Text"])


def _update_time_category_with_cm_record(entity, time_entities, seen_names):
    """Update the time category records. They require a special processing.

    Args:
        entity (dict): entity to be added to the category records.
        time_entities (list): List of time name records.
        seen_names (set): Set of seen names.

    Returns:
        None

    """
    name = entity["Text"]

    # filter out digit form time. E.g. "23 days" -> "23"
    if re.search(WORDS_P, name):
        digit_entity = re.search(DIGITS_P, name)
        entity["Text"] = name[digit_entity.start() : digit_entity.end()]
        seen_names.add(name)

    _update_category_with_cm_record(entity, time_entities, seen_names)


def _add_cm_entity(raw_entity, entities_by_category, seen_names):
    """Classifies and records names detected by CM based on CM category and type into tool's categories.


    Args:
        raw_entity (dict): Dictionary defining the raw entity detected by CM.
        entities_by_category (dict): Dictionary of previously detected entities by category.
        seen_names (set): Set of names of already detected entities.

    Returns:
        tuple: First is the updated dictionary with entities by category. Second element is the set of seen names.

    """
    entity = _reformat_cm_entity(raw_entity)

    if entity["Text"] in seen_names:
        return entities_by_category, seen_names

    entity_category, entity_type = entity["Category"], entity["Type"]

    if entity_category == "MEDICATION" and entity_type == "DURATION":
        _update_time_category_with_cm_record(
            entity, entities_by_category["TIMEDAYS"], seen_names
        )

    elif entity_category == "PROTECTED_HEALTH_INFORMATION" and entity_type == "DATE":
        _update_category_with_cm_record(
            entity, entities_by_category["TIMEYEARS"], seen_names
        )

    elif entity_category == "PROTECTED_HEALTH_INFORMATION" and entity_type == "AGE":
        _update_category_with_cm_record(entity, entities_by_category["AGE"], seen_names)

    elif entity_category == "PROTECTED_HEALTH_INFORMATION" and entity_type == "ADDRESS":
        _update_category_with_cm_record(
            entity, entities_by_category["STATE"], seen_names
        )

    elif entity_category == "MEDICATION" and (
        entity_type in ("GENERIC_NAME", "BRAND_NAME")
    ):
        _update_category_with_cm_record(
            entity, entities_by_category["DRUG"], seen_names
        )

    elif entity_category == "MEDICAL_CONDITION":
        _update_category_with_cm_record(
            entity, entities_by_category["CONDITION"], seen_names
        )

    return entities_by_category, seen_names


def _detect_entities_with_regex(nlq, pattern, seen_names):
    """Detects entities in the Natural Language Query based on a given regex pattern.

    Args:
        nlq (str): Natural Language Query
        pattern (_sre.SRE_Pattern): Regex compiled pattern defining the sub-strings to be found.
        seen_names (set): Set of names of already detected entities.

    Returns:
        tuple: First is the list of dictionary defining the records detected with the given pattern. Second element is the set of seen names.
    """
    entities = []

    for entity in re.finditer(pattern, nlq):
        ref_entity = _reformat_regex_entity(entity)
        name = ref_entity["Text"]
        if name not in seen_names:
            entities.append(ref_entity)
            seen_names.add(name)

    return entities, seen_names
