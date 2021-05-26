# This module contains the templates used to render the output of the ML model.
# The mapping placeholder -> template is specified in src/config & the domain-specific rendering functions in rendering_functions.


def get_descendent_concepts_template_from_concept_name(schema, domain, concept_name):
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


def get_descendent_concepts_template_from_vocab_code(schema, vocab, concept_codes):
    '''
    Assumption: ICD10 codes don't have ";"
    
    Example args
    
        schema = cmsdesynpuf23m
        vocab = ICD10
        concept_code = A97
    
    '''
    concept_codes_conditions = [f"concept_code='{concept_code.strip()}'" 
                                for concept_code in concept_codes.split(';') if concept_code.strip()]
    
    join_codes_condition = "( " + " OR ".join(concept_codes_conditions) + " )"
    
    out = f"( SELECT descendant_concept_id AS concept_id FROM \
(SELECT * FROM \
(SELECT concept_id_2 FROM \
( \
(SELECT concept_id FROM  \
{schema}.concept WHERE vocabulary_id='{vocab}' AND {join_codes_condition}) \
JOIN  \
( SELECT concept_id_1, concept_id_2 FROM  \
{schema}.concept_relationship WHERE relationship_id='Maps to' )  \
ON concept_id=concept_id_1) \
) JOIN {schema}.concept ON concept_id_2=concept_id) \
JOIN {schema}.concept_ancestor ON concept_id=ancestor_concept_id \
) "
    
#     out = f"( SELECT descendant_concept_id AS concept_id FROM \
# (SELECT * FROM \
# (SELECT concept_id_2 FROM \
# ( \
# (SELECT concept_id FROM  \
# {schema}.concept WHERE vocabulary_id='{vocab}' AND concept_code='{concept_code}') \
# JOIN  \
# ( SELECT concept_id_1, concept_id_2 FROM  \
# {schema}.concept_relationship WHERE relationship_id='Maps to' )  \
# ON concept_id=concept_id_1) \
# ) JOIN {schema}.concept ON concept_id_2=concept_id) \
# JOIN {schema}.concept_ancestor ON concept_id=ancestor_concept_id \
# ) "
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