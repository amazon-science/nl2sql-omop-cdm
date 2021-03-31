import boto3
import re
# test
from pprint import pprint

CM_CLIENT = boto3.client('comprehendmedical')

ETHNICITY_P = re.compile("(?i)\\b(not)\\b")

# TODO: fill dictionaries -- or use rematching?
GENDER2STANDARD = [
    # (OMOP CDM concept name, pattern that has to match)
    ("FEMALE", re.compile("(?i)\\b(females?|wom(a|e)n)\\b")),
    ("MALE", re.compile("(?i)\\b(males?|m(a|e)n)\\b"))
]
RACE2STANDARD = [
    # (OMOP CDM concept name, pattern that has to match)
    ("Black or African American", re.compile("(?i)\\b(black or african americans?|african americans?|blacks?)\\b")),
    ("White", re.compile("(?i)\\b(whites?)\\b"))
]


def _use_pattern_dict(name, standard2pattern):
    '''
    
    
    Args:
    
    
    Returns:
    
    
    '''
    for standard, pattern in standard2pattern:
        if re.search(pattern, name):
            return standard
    
    # Error handeling
    standards = ''.join([i[0] for i in standard2pattern])
    raise ValueError(f"Name {name} don't match any pattern in dict with standards: {standards}")
    

def _gender_name2standard(gender_name):
    '''
    
    
    Args:
    
    
    Returns:
    
    
    '''
    return _use_pattern_dict(gender_name, GENDER2STANDARD)
    
    
def _race_name2standard(race_name):
    '''
    
    
    Args:
    
    
    Returns:
    
    
    '''
    return _use_pattern_dict(race_name, RACE2STANDARD)
    
    
def _ethnicity_name2standard(ethnicity_name):
    '''
    
    
    Args:
    
    
    Returns:
    
    
    '''
    if re.search(ETHNICITY_P, ethnicity_name):
        return "Not Hispanic or Latino"
    else:
        return "Hispanic or Latino"
    
    
def _use_function_for_options(entities, fun):
    '''
    
    
    Args:
    
    
    Returns:
    
    
    '''
    for entity in entities:
        entity["Options"] = [{"Code": fun(entity["Text"])}]
        entity["Query-arg"] = entity["Options"][0]["Code"]
    
    return entities
    
    
def _use_text_as_options(entities):
    '''
    
    
    Args:
    
    
    Returns:
    
    
    '''
    for entity in entities:
        entity["Options"] = [{"Code": entity["Text"]}]
        entity["Query-arg"] = entity["Options"][0]["Code"]
        
    return entities


def add_gender_options(entities):
    '''
    
    
    Args:
    
    
    Returns:
    
    
    '''
    return _use_function_for_options(entities, _gender_name2standard)


def add_race_options(entities):
    '''
    
    
    Args:
    
    
    Returns:
    
    
    '''
    return _use_function_for_options(entities, _race_name2standard)
    
    
def add_ethnicity_options(entities):
    '''
    
    
    Args:
    
    
    Returns:
    
    
    '''
    return _use_function_for_options(entities, _ethnicity_name2standard)

    
def add_dosage_options(entities):
    '''
    
    
    Args:
    
    
    Returns:
    
    
    '''
    return _use_text_as_options(entities)
    
    
def add_time_options(entities):
    '''
    
    
    Args:
    
    
    Returns:
    
    
    '''
    return _use_text_as_options(entities)


def add_state_options(entities):
    '''
    
    
    Args:
    
    
    Returns:
    
    
    '''
    return _use_text_as_options(entities)


def add_condition_options(entities):
    """
    TODO: Optimize to reduce # calls --> reduce cost
    
    
    Args:
    
    
    Returns:
    
    
    """
    
    for entity in entities:
        response = CM_CLIENT.infer_icd10_cm(Text = entity["Text"])
        result = response['Entities'][0]
#         pprint(result)
        entity["Options"] = result["ICD10CMConcepts"]
        entity["Query-arg"] = entity["Options"][0]["Code"]
    
    return entities
    
    
def add_drug_options(entities):
    '''
    
    
    Args:
    
    
    Returns:
    
    
    '''
    for entity in entities:
        response = CM_CLIENT.infer_rx_norm(Text = entity["Text"])
        try:
            result = response['Entities'][0]
        except:
            print(entity["Text"])
            pprint(response)
        entity["Options"] = result["RxNormConcepts"]
        entity["Query-arg"] = entity["Options"][0]["Code"]
    
    return entities
    
    