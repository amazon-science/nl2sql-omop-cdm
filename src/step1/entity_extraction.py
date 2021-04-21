import boto3
import re
from extraction_helpers import (
    _add_cm_entity,
    _detect_entities_with_regex
)

GENDER_P = re.compile("(?i)\\b((fe)?males?|(wo)?m(a|e)n)\\b")
ETHNICITY_P = re.compile("(?i)\\b((not? +)?(hispanics? +or +latinos?|hispanics?|latinos?))\\b")
RACE_P = re.compile("(?i)\\b(black or african americans?|african americans?|blacks?|whites?)\\b")

CM_CLIENT = boto3.client('comprehendmedical')
COMPLEMENT_CATEGS = set(('DOSAGE','STRENGTH', 'ACUITY'))


def add_cm_entities(nlq, entities_by_category, seen_names, entity_detection_score_thr, drug_relationship_score_thr):
    '''
    
    
    Args:
        
        
    Returns:
        
        
    '''
    result = CM_CLIENT.detect_entities_v2(Text = nlq)
    
    # initialize categories
    entities_by_category["TIMEDAYS"] = []
    entities_by_category["TIMEYEARS"] = []
    entities_by_category["DRUG"] = []
    entities_by_category["CONDITION"] = []
#     entities_by_category["DOSAGE"] = []
    entities_by_category["AGE"] = []
    entities_by_category["STATE"] = []
    
    
    # extract entities from main entities and attributes.
    for entity in result['Entities']:
        complement = None
        
        # TODO add logic to handle more than one attribute that should go into the name
        for attribute in entity.get("Attributes", []):
            if attribute['Score'] > entity_detection_score_thr:
                if attribute['RelationshipType'] in COMPLEMENT_CATEGS and attribute['RelationshipScore'] > drug_relationship_score_thr:
                    complement = attribute
                    
            elif attribute['RelationshipType'] not in COMPLEMENT_CATEGS:
                entities_by_category, seen_names = _add_cm_entity(attribute, entities_by_category, 
                                                                  seen_names)
                
        if entity['Score'] > entity_detection_score_thr:
            
            if complement:
                if complement['BeginOffset'] < entity['BeginOffset']:
                    entity['Text'] = complement['Text'] + ' ' + entity['Text'] 
                    entity['BeginOffset'] = complement['BeginOffset']
                
                else:
                    entity['Text'] = entity['Text'] + ' ' + complement['Text']
                    entity['EndOffset'] = complement['EndOffset']
                    
                
            entities_by_category, seen_names = _add_cm_entity(entity, entities_by_category, 
                                                                  seen_names)

        
    return entities_by_category, seen_names
    
    
def add_gender_entities(nlq, entities_by_category, seen_names):
    '''
    
    
    Args:
        
        
    Returns:
        
        
    '''
    entities, seen_names = _detect_entities_with_regex(nlq, 
                                                       GENDER_P, 
                                                       seen_names)
    entities_by_category["GENDER"] = entities
    
    return entities_by_category, seen_names


def add_ethnicity_entities(nlq, entities_by_category, seen_names):
    '''
    
    
    Args:
        
        
    Returns:
        
        
    '''
    entities, seen_names = _detect_entities_with_regex(nlq, 
                                                       ETHNICITY_P, 
                                                       seen_names)
    entities_by_category["ETHNICITY"] = entities
    
    return entities_by_category, seen_names


def add_race_entities(nlq, entities_by_category, seen_names):
    '''
    
    
    Args:
        
        
    Returns:
        
        
    '''
    entities, seen_names = _detect_entities_with_regex(nlq, 
                                                       RACE_P, 
                                                       seen_names)
    entities_by_category["RACE"] = entities
    
    return entities_by_category, seen_names


# main function
def detect_entities(nlq, entity_detection_score_thr, drug_relationship_score_thr):
    '''
    
    
    Args:
        
        
    Returns:
        
        
    '''
    entities_by_category = {}
    seen_names = set()
    
    # Comprehend Medical NER
    entities_by_category, seen_names = add_cm_entities(nlq, entities_by_category, seen_names,
                                                       entity_detection_score_thr, drug_relationship_score_thr
                                                      )

    # regex NER
    entities_by_category, seen_names = add_gender_entities(nlq, entities_by_category, seen_names)
    entities_by_category, seen_names = add_ethnicity_entities(nlq, entities_by_category, seen_names)
    entities_by_category, seen_names = add_race_entities(nlq, entities_by_category, seen_names)
    
    return entities_by_category


if __name__=='__main__':
    from pprint import pprint
    # example
    queries = "How many latinos started taking aspirine 30g after 24 months of taking ibuprofen?. How many female had Laryngitis in year 2009?. Number african americans that have obstruction of larynx?"
    
    entities = detect_entities(queries)
    pprint(entities)
    