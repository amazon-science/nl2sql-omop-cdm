import boto3
import re
import json
from os import path as osp
# test
from pprint import pprint


CM_CLIENT = boto3.client('comprehendmedical')
ETHNICITY_P = re.compile("(?i)\\b(not)\\b")


def load_dict2pattern(filepath):
    with open(filepath, 'r') as fp:
        category2pattern = json.load(fp)
        out = {category: re.compile(pattern) for category, pattern in category2pattern.items()}
    return out

current_folder = osp.dirname(osp.abspath(__file__))
GENDER2STANDARD = load_dict2pattern(osp.join(current_folder, 'gender2pattern.json'))
RACE2STANDARD = load_dict2pattern(osp.join(current_folder, 'race2pattern.json'))
STATE2STANDARD = load_dict2pattern(osp.join(current_folder, 'state2pattern.json'))


def _use_pattern_dict(name, standard2pattern):
    '''
    
    
    Args:
    
    
    Returns:
    
    
    '''
    for standard, pattern in standard2pattern.items():
        if re.match(pattern, name):
            return standard
    return f'NA'
    
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
    
    
def _state_name2standard(race_name):
    '''
    
    
    Args:
    
    
    Returns:
    
    
    '''
    return _use_pattern_dict(race_name, STATE2STANDARD)
    
    
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


def add_state_options(entities):
    '''
    
    
    Args:
    
    
    Returns:
    
    
    '''
    return _use_function_for_options(entities, _state_name2standard)
    
    
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


def add_age_options(entities):
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
        response = CM_CLIENT.infer_icd10_cm(Text = entity["Text"])['Entities']
        if response:
            options = response[0]["ICD10CMConcepts"]
            default = options[0]["Code"]
        else:
            options = [{"Score": -1., "Code": "-1", "Description": "N/A"}]
            default = "N/A"
            
        entity["Options"] = options
        entity["Query-arg"] = default
        
    return entities
    
    
def add_drug_options(entities):
    '''
    
    
    Args:
    
    
    Returns:
    
    
    '''
    for entity in entities:
        response = CM_CLIENT.infer_rx_norm(Text = entity["Text"])['Entities']
        if response:
            result = response[0]
            options = result["RxNormConcepts"]
            default = options[0]["Code"]
        else:
            options = [{"Score": -1., "Code": "-1", "Description": "N/A"}]
            default = "N/A"
        entity["Options"] = options
        entity["Query-arg"] = default
    
    return entities
    
    