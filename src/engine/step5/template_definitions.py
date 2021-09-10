"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

SPDX-License-Identifier: CC-BY-NC-4.0
"""

# This module contains the templates used to render the output of the ML model.
# The mapping placeholder -> template is specified in src/config & the domain-specific rendering functions in rendering_functions.


def get_descendent_concepts_template_from_vocab_code(schema, vocab, concept_codes):
    """
    Renders a pre-defined sub-sql query schema returning a column of `concept_id`s of a specific standard concept with OMOP CDM concept code and its
    descendents using the vocabulary `vocab` and the vocab concept code.

    Assumption: ICD10 codes don't have ";"

    Args:
        config (module): General tool configuration.
        general_query (str): General SQL query.
        args_dict (dict): Dictionary of processed arguments from step 2.

    Returns:
        str: Rendered query by replacing argument and template placeholders.

    Example args
        schema = cmsdesynpuf23m
        vocab = ICD10
        concept_code = A97;G47.00

    """
    # support for 1+ codes (drug or condition)
    concept_codes_conditions = [
        f"concept_code='{concept_code.strip()}'"
        for concept_code in concept_codes.split(";")
        if concept_code.strip()
    ]

    join_codes_condition = "( " + " OR ".join(concept_codes_conditions) + " )"

    out = (
        f"( SELECT descendant_concept_id AS concept_id FROM "
        + f"(SELECT * FROM "
        + f"(SELECT concept_id_2 FROM "
        + f"( "
        + f"(SELECT concept_id FROM "
        + f"{schema}.concept WHERE vocabulary_id='{vocab}' AND {join_codes_condition}) "
        + f"JOIN "
        + f"( SELECT concept_id_1, concept_id_2 FROM "
        + f"{schema}.concept_relationship WHERE relationship_id='Maps to' ) "
        + f"ON concept_id=concept_id_1) "
        + f") JOIN {schema}.concept ON concept_id_2=concept_id) "
        + f"JOIN {schema}.concept_ancestor ON concept_id=ancestor_concept_id "
        + f") "
    )

    return out


def get_unique_concept_template(schema, domain, concept_name):
    """
    Renders a pre-defined sub-sql query schema returning a column `concept_id` with the concept_id corresponding to the standard concept of `concept_name` in `domain`.

    Args:
        schema (str): Schema of the database.
        domain (str): Domain of the concept. Intended use with Drug or Condition.
        concept_name (str): concept_name as it appears in the `schema.concept` table.

    Returns:
        str: Rendered subquery with input arguments.
    """

    out = (
        f" ( "
        + f"SELECT concept_id "
        + f"FROM {schema}.concept "
        + f"WHERE concept_name='{concept_name}' "
        + f"AND domain_id='{domain}' "
        + f"AND standard_concept='S' "
        + f") "
    )

    return out


def get_concept_name_template(schema, domain):
    """
    Renders a pre-defined sub-sql query schema returning two columns: `concept_id` and `concept_name` with all the standard concept of `domain`.

    Args:
        schema (str): Schema of the database.
        domain (str): Domain of the concept. Intended use with Drug or Condition.

    Returns:
        str: Rendered subquery with input arguments.
    """

    out = (
        f" ( "
        + f"SELECT concept_id, concept_name AS {domain.lower()} "
        + f"FROM {schema}.concept "
        + f"WHERE domain_id='{domain}' "
        + f"AND standard_concept='S' "
        + f") "
    )

    return out


def get_state_template(schema, state_acronym):
    """
    Renders a pre-defined sub-sql query schema returning a columns `location_id` with the OMOP CDM state id of state `state_acronym`.

    Args:
        schema (str): Schema of the database.
        state_acronym (str): State acronym.

    Returns:
        str: Rendered subquery with input arguments.
    """
    out = (
        f" ( "
        + f"SELECT location_id "
        + f"FROM {schema}.location "
        + f"WHERE state='{state_acronym}' "
        + f") "
    )
    return out


def get_state_name_template(schema):
    """
    Renders a pre-defined sub-sql query schema returning two columns: `location_id` and `state` with the OMOP CDM state id and it's name respectively.

    Args:
        schema (str): Schema of the database.

    Returns:
        str: Rendered subquery with input arguments.
    """
    out = f" ( " + f"SELECT location_id, state " + f"FROM {schema}.location " + f") "
    return out
