"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

SPDX-License-Identifier: CC-BY-NC-4.0
"""

import re


def replace_name_for_placeholder(nlq, entities):
    """Replaces the name in entities for the corresponding placeholder in the nlq.

    Args:
        nlq (str): Natural Langugae Query
        entities (dict): Dictionary with keys being entity category (e.g. CONDITION, DRUG, etc.) and the value a list of dictionaries representing the entities in each category.

    Returns:
        str: Natural Language Query with the names replaced.

    """
    out_nlq = nlq
    for category_entities in entities.values():
        for entity in category_entities:
            name = entity["Text"]
            placeholder = entity["Placeholder"]

            temp_pattern = re.compile(f"(?i)\\b{name}\\b")
            out_nlq = re.sub(temp_pattern, placeholder, out_nlq)

    return out_nlq
