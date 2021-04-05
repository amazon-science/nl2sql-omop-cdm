'''


Notes
    Time has to be given in digits, not words. It can handle cases such as "24 days". 
    For the time being we are not looking at extracting time unit even though it will be a relatively easy simple 
    feature to extract -> will require one more placeholder <ARG-TIMEUNIT>

'''
# import boto3
import re
from pprint import pprint

WORDS_P = re.compile("[A-Za-z]*")
DIGITS_P = re.compile("\d*")

def _reformat_cm_entity(entity):
    '''
    
    
    Args:
        
        
    Returns:
        
        
    '''
    out = {
        'BeginOffset': entity["BeginOffset"],
        'EndOffset': entity["EndOffset"],
        'Text': entity["Text"],
        'Category': entity["Category"],
        'Type': entity["Type"]
    }
    return out

def _reformat_regex_entity(entity):
    '''
    
    
    Args:
        
        
    Returns:
        
        
    '''
    out = {
        'BeginOffset': entity.start(), 
        'EndOffset': entity.end(), 
        'Text': entity.string[entity.start():entity.end()]
    }
    return out
    

def _update_category_with_cm_record(entity, category_records, seen_names):
    '''
    
    
    Args:
        
        
    Returns:
        
        
    '''
    del entity['Category']
    del entity['Type']
    category_records.append(entity)
    seen_names.add(entity["Text"])
    

def _update_time_category_with_cm_record(entity, time_entities, seen_names):
    '''
    
    
    Args:
        
        
    Returns:
        
        
    '''
    name = entity["Text"]
        
    # filter out digit form time. E.g. "23 days" -> "23"
    if re.search(WORDS_P, name):
        digit_entity = re.search(DIGITS_P, name)
        entity["Text"] = name[digit_entity.start():digit_entity.end()]
        seen_names.add(name)

        '''
        # Code to get time units
        time_unit_entity = re.search(WORDS_P, name)
        time_unit = name[time_unit_entity.start():time_unit_entity.end()]

        _update_category_with_cm_record({"Text": time_unit}, 
                                    entities_by_category["TIMEMEASURE"], 
                                    seen_names)
        '''
        
    _update_category_with_cm_record(entity, time_entities, seen_names)


def _add_cm_entity(raw_entity, entities_by_category, seen_names):
    '''
    
    
    Args:
        
        
    Returns:
        
        
    '''
    entity = _reformat_cm_entity(raw_entity)
    
    if entity["Text"] in seen_names:
        return entities_by_category, seen_names
    
    entity_category, entity_type = entity["Category"], entity["Type"]

    if entity_category == "MEDICATION" and entity_type == "DURATION":
        _update_time_category_with_cm_record(entity, 
                                             entities_by_category["TIMEDAYS"],
                                             seen_names)

    elif entity_category == "MEDICATION" and entity_type == "DOSAGE":
        _update_category_with_cm_record(entity, 
                                        entities_by_category["DOSAGE"], 
                                        seen_names)

    elif entity_category == "PROTECTED_HEALTH_INFORMATION" and entity_type == "DATE":
        _update_category_with_cm_record(entity, 
                                        entities_by_category["TIMEYEARS"], 
                                        seen_names)
        
    elif entity_category == "PROTECTED_HEALTH_INFORMATION" and entity_type == "AGE":
        _update_category_with_cm_record(entity, 
                                        entities_by_category["AGE"], 
                                        seen_names)
        
    elif entity_category == "PROTECTED_HEALTH_INFORMATION" and entity_type == "ADDRESS":
        _update_category_with_cm_record(entity, 
                                        entities_by_category["STATE"], 
                                        seen_names)

    elif entity_category == "MEDICATION" and (entity_type in ("GENERIC_NAME", "BRAND_NAME")):
        _update_category_with_cm_record(entity, 
                                        entities_by_category["DRUG"], 
                                        seen_names)

    elif entity_category == "MEDICAL_CONDITION":
        _update_category_with_cm_record(entity, 
                                        entities_by_category["CONDITION"], 
                                        seen_names)
        
    return entities_by_category, seen_names


def _detect_entities_with_regex(nlq, pattern, seen_names):
    '''
    
    
    Args:
        
        
    Returns:
        
        
    '''
    entities = []
    
    for entity in re.finditer(pattern, nlq):
        ref_entity = _reformat_regex_entity(entity)
        name = ref_entity['Text']
        if name not in seen_names:
            entities.append(ref_entity)
            seen_names.add(name)
            
    return entities, seen_names
    
