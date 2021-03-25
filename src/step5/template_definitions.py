# This module contains the templates used to render the output of the ML model.
# The mapping placeholder -> template is specified in src/config & the domain-specific rendering functions in rendering_functions.


def get_descendent_concepts_template(schema, domain, concept_name):
    '''
    Renders a sub-sql query that returns a column of `concept_id`s of a specific standard concept with concept name `concept_name` containing the concept_id and all it's descendents.
    
    Args:
        schema (str): Schema of the database.
        domain (str): Domain of the concept. Intended use with Drug or Condition.
        concept_name (str): concept_name as it appears in the `schema.concept` table.
        
    Returns:
        str: Rendered subquery with input arguments. 
    '''
    out = f" ( \
SELECT c1.concept_id \
from {schema}.CONCEPT c1 \
join {schema}.CONCEPT_ANCESTOR ca \
on c1.concept_id = ca.descendant_concept_id \
and ca.ancestor_concept_id in ( \
SELECT concept_id \
FROM {schema}.concept \
WHERE concept_name='{concept_name}' \
AND domain_id='{domain}' \
AND standard_concept='S' \
) \
and c1.invalid_reason is null \
UNION \
select descendant_concept_id from \
(select * \
from {schema}.CONCEPT c2 \
join {schema}.CONCEPT_RELATIONSHIP cr \
on c2.concept_id = cr.concept_id_1 \
and c2.concept_id in ( \
SELECT concept_id \
FROM {schema}.concept \
WHERE concept_name='{concept_name}' \
AND domain_id='{domain}' \
AND standard_concept='S' \
) \
and relationship_id='Maps to') \
join {schema}.CONCEPT_ANCESTOR ca \
on concept_id_2 = ca.ancestor_concept_id \
and concept_id in ( \
SELECT concept_id \
FROM {schema}.concept \
WHERE concept_name='{concept_name}' \
AND domain_id='{domain}' \
AND standard_concept='S' )\
) "
    return out


def get_unique_concept_template(schema, domain, concept_name):
    '''
    Renders a sub-sql query that returns a column `concept_id` with the concept_id corresponding to the standard concept of `concept_name`.
    
    Args:
        schema (str): Schema of the database.
        domain (str): Domain of the concept. Intended use with Drug or Condition.
        concept_name (str): concept_name as it appears in the `schema.concept` table.
        
    Returns:
        str: Rendered subquery with input arguments. 
    '''
    out = f" ( \
SELECT concept_id \
FROM {schema}.concept \
WHERE concept_name='{concept_name}' \
AND domain_id='{domain}' \
AND standard_concept='S' \
) "
    return out


def get_concept_name_template(schema, domain):
    '''
    
    
    Args:
        schema (str): Schema of the database.
        domain (str): Domain of the concept. Intended use with Drug or Condition.
        
    Returns:
        str: Rendered subquery with input arguments. 
    '''
    out = f" ( \
SELECT concept_id, concept_name AS {domain.lower()} \
FROM {schema}.concept \
WHERE domain_id='{domain}' \
) "
    return out



def get_state_template(schema, state_acronym):
    '''
    
    
    Args:
        schema (str): Schema of the database.
        state_acronym (str): 
        
    Returns:
        str: Rendered subquery with input arguments. 
    '''
    out = f" ( \
SELECT location_id \
FROM {schema}.location \
WHERE state='{state_acronym}' \
) "
    return out


def get_state_name_template(schema):
    '''
    
    
    Args:
        schema (str): Schema of the database.
        
    Returns:
        str: Rendered subquery with input arguments. 
    '''
    out = f" ( \
SELECT location_id, state \
FROM {schema}.location \
) "
    return out