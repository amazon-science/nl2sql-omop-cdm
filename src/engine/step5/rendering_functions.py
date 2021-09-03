"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

SPDX-License-Identifier: CC-BY-NC-4.0
"""

# This module contains the rendering functions used to convert ML outputs into final queries.
# The mapping placeholder -> template is specified in src/config & the rendered sub-queries in template_definitions.


from __init__ import *
from template_definitions import (
    #     get_descendent_concepts_template_from_concept_name,
    get_descendent_concepts_template_from_vocab_code,
    get_unique_concept_template,
    get_state_template,
)


def render_condition_template(schema, condition_code):
    """Renders and returns the condition template with a column `concept_id`
    with the OMOP CDM standard code for `condition_code` and its descendents.


    Args:
        schema (str): Schema name of the database.
        condition_code (str): Code of the condition in ICD10CM

    Returns:
        str: Rendered subquery with input arguments.
    """
    out = get_descendent_concepts_template_from_vocab_code(
        schema, "ICD10CM", condition_code
    )
    return out


def render_drug_template(schema, drug_code):
    """Renders and returns the drug template with a column `concept_id`
    with the OMOP CDM standard code for `drug_code` and its descendents.

    Args:
        schema (str): Schema name of the database.
        drug_name (str):

    Returns:
        str: Rendered subquery with input arguments.
    """
    out = get_descendent_concepts_template_from_vocab_code(schema, "RxNorm", drug_code)
    return out


def render_gender_template(schema, gender_name):
    """Renders and returns the gender template with a column `concept_id`
    with the OMOP CDM standard code for `gender_name`.

    Args:
        schema (str): Schema name of the database.
        gender_name (str): Gender name as it appears in OMOP CDM standard concepts.

    Returns:
        str: Rendered subquery with input arguments.
    """
    out = get_unique_concept_template(schema, "Gender", gender_name)
    return out


def render_race_template(schema, race_name):
    """Renders and returns the race template with a column `concept_id`
    with the OMOP CDM standard code for `race_name`.


    Args:
        schema (str): Schema name of the database.
        race_name (str): Race name as it appears in OMOP CDM standard concepts.

    Returns:
        str: Rendered subquery with input arguments.
    """
    out = get_unique_concept_template(schema, "Race", race_name)
    return out


def render_ethnicity_template(schema, ethnicity_name):
    """Renders and returns the ethnicity template with a column `concept_id`
    with the OMOP CDM standard code for `ethnicity_name`.


    Args:
        schema (str): Schema name of the database.
        ethnicity_name (str): Ethnicity name as it appears in OMOP CDM standard concepts.

    Returns:
        str: Rendered subquery with input arguments.
    """
    out = get_unique_concept_template(schema, "Ethnicity", ethnicity_name)
    return out


def render_state_template(schema, state_acronym):
    """Renders and returns the ethnicity template with a column `concept_id`
    with the OMOP CDM standard code for `ethnicity_name`.


    Args:
        schema (str): Schema name of the database.
        state_acronym (str): Acronym of the state as it appears in OMOP CDM standard concepts.

    Returns:
        str: Rendered subquery with input arguments.
    """
    return get_state_template(schema, state_acronym)
