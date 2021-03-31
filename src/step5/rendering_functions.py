# This module contains the rendering functions used to convert ML outputs into final queries.
# The mapping placeholder -> template is specified in src/config & the rendered sub-queries in template_definitions.



# TODO: use get_descendent_concepts_template_from_vocab_code when using ICD10 codes or rxnorm codes.

from __init__ import *
from template_definitions import (
#     get_descendent_concepts_template_from_concept_name,
    get_descendent_concepts_template_from_vocab_code, 
    get_unique_concept_template, 
    get_state_template
)


def render_condition_template(schema, condition_code):
    '''
    
    
    Args:
        schema (str): Schema of the database.
        condition_name (str): 
        
    Returns:
        str: Rendered subquery with input arguments. 
    '''
#     out = get_descendent_concepts_template_from_concept_name(schema, 'Condition', condition_name)
    out = get_descendent_concepts_template_from_vocab_code(schema, 'ICD10', condition_code)
    return out


def render_drug_template(schema, drug_code):
    '''
    
    
    Args:
        schema (str): Schema of the database.
        drug_name (str): 
        
    Returns:
        str: Rendered subquery with input arguments. 
    '''
#     out = get_descendent_concepts_template_from_concept_name(schema, 'Drug', drug_name)
    out = get_descendent_concepts_template_from_vocab_code(schema, 'RxNorm', drug_code)
    return out


def render_gender_template(schema, gender_name):
    '''
    
    
    Args:
        schema (str): Schema of the database.
        domain (gender_name): 
        
    Returns:
        str: Rendered subquery with input arguments. 
    '''
    out = get_unique_concept_template(schema, 'Gender', gender_name)
    return out


def render_race_template(schema, race_name):
    '''
    
    
    Args:
        schema (str): Schema of the database.
        race_name (str): 
        
    Returns:
        str: Rendered subquery with input arguments. 
    '''
    out = get_unique_concept_template(schema, 'Race', race_name)
    return out


def render_ethnicity_template(schema, ethnicity_name):
    '''
    
    
    Args:
        schema (str): Schema of the database.
        ethnicity_name (str): 
        
    Returns:
        str: Rendered subquery with input arguments. 
    '''
    out = get_unique_concept_template(schema, 'Ethnicity', ethnicity_name)
    return out


def render_state_template(schema, state_acronym):
    '''
    
    
    Args:
        schema (str): Schema of the database.
        state_acronym (str): 
        
    Returns:
        str: Rendered subquery with input arguments. 
    '''
    return get_state_template(schema, state_acronym)
