"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

SPDX-License-Identifier: CC-BY-NC-4.0
"""

from disambiguation_helpers import (
    add_condition_options,
    add_drug_options,
    add_gender_options,
    add_race_options,
    add_ethnicity_options,
    add_time_options,
    add_state_options,
)

CATEGORY2PROC_FUN = {
    "CONDITION": add_condition_options,
    "DRUG": add_drug_options,
    "ETHNICITY": add_ethnicity_options,
    "GENDER": add_gender_options,
    "RACE": add_race_options,
    "TIMEDAYS": add_time_options,
    "TIMEYEARS": add_time_options,
    "STATE": add_state_options,
}


def add_omop_disambiguation_options(entities):
    """
    Provide options for each name depending on it's category using the CATEGORY2PROC_FUN mapping.

    Args:
        entities (dict): Detected entities in a NLQ.

    Returns:
        dict: Input entities with added "Options" and "Query-arg" fields.

    """
    for category, f in CATEGORY2PROC_FUN.items():
        if category in entities:
            entities[category] = f(entities[category])

    return entities


def add_placeholders(all_entities, start_indices={}, **kwargs):
    """
    Assigns placeholder to each entity in `all_entities` based on category and arbitrary order within each category.

    Args:
        all_entities (dict): Dictionary with keys being entity category (e.g. CONDITION, DRUG, etc.) and the value a list of dictionaries representing the entities in each category.

    Returns:
        dict: `all_entities` with an added "Placeholder" field.

    """
    for category, entities in all_entities.items():
        start_idx = start_indices.get(category, 0)
        for i, entity in enumerate(entities, start_idx):
            idx = str(i)
            placeholder = f"<ARG-{category}><{idx}>"
            entity["Placeholder"] = placeholder

    return all_entities
