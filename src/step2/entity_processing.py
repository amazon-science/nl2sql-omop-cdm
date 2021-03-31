from disambiguation_helpers import (
    add_condition_options,
    add_drug_options,
    add_gender_options,
    add_race_options,
    add_ethnicity_options,
    add_dosage_options,
    add_time_options,
    add_state_options
)

def add_omop_disambiguation_options(entities):
    entities['CONDITION'] = add_condition_options(entities['CONDITION'])
    entities['DOSAGE'] = add_dosage_options(entities['DOSAGE'])
    entities['DRUG'] = add_drug_options(entities['DRUG'])
    entities['ETHNICITY'] = add_ethnicity_options(entities['ETHNICITY'])
    entities['GENDER'] = add_gender_options(entities['GENDER'])
    entities['RACE'] = add_race_options(entities['RACE'])
    entities['TIMEDAYS'] = add_time_options(entities['TIMEDAYS'])
    entities['TIMEYEARS'] = add_time_options(entities['TIMEYEARS'])
#     entities['STATE'] = add_state_options(entities['STATE'])
    
    return entities


def add_placeholders(all_entities):
    '''
    Assigns placeholder to each entity in `all_entities` based on category and arbitrary order within each category.
    
    Args:
        all_entities (dict): Dictionary with keys being entity category (e.g. CONDITION, DRUG, etc.) and the value a list of dictionaries representing the entities in each category. 
        
    Returns:
        dict: `all_entities` with placeholders. 
        
    '''
    for category, entities in all_entities.items():
        for i, entity in enumerate(entities):
            idx = str(i)
            placeholder = f'<ARG-{category}><{idx}>'
            entity["Placeholder"] = placeholder
    
    return all_entities