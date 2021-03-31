import re

def replace_name_for_placeholder(nlq, entities):
    '''
    
    Args:
        
        
    Returns:
        
        
    '''
    out_nlq = nlq
    for category_entities in entities.values():
        for entity in category_entities:
            name = entity["Text"]
            placeholder = entity["Placeholder"]

            temp_pattern = re.compile(f"(?i)\\b{name}\\b")
            out_nlq = re.sub(temp_pattern, placeholder, out_nlq)
    
    return out_nlq
