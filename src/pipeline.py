from step1.entity_extraction import detect_entities
from step2.entity_processing import add_omop_disambiguation_options, add_placeholders
from step3.nlq_processing import replace_name_for_placeholder
from step4.ml_inference import Inferencer
from step5.sql_processing import render_template_query
from utils.query_execution import connect_to_db, execute_query
from copy import deepcopy

class nlq2SqlTool(object):
    
    def __init__(self, config):
        '''Comment
        
        Args:
            
            
        Returns:
            
        
        '''
        
        self.config = config
        self.model = Inferencer(config.MODEL_PATH)
        
    def set_db_credentials(self, user, password):
        self._user = user
        self._password = password
        
        # test connection
        test_conn = connect_to_db(self.config.REDSHIFT_PARM, self._user, self._password)
        test_conn.close()
    
    def clear_credentials(self):
        if self.credentials_exist():
            del self._user
            del self._password
        
        
    def credentials_exist(self,):
        return hasattr(self, '_user') and hasattr(self, '_password')
        
    
    def _open_redshift_connection(self, ):
        '''Comment
        
        Args:
            
            
        Returns:
            
        
        '''
        self.conn = connect_to_db(self.config.REDSHIFT_PARM, self._user, self._password)
    
    
    def _close_redshift_connection(self, ):
        '''Comment
        
        Args:
            
            
        Returns:
            
        
        '''
        if not hasattr(self, 'conn'):
            raise AttributeError("Connection has to be opened before closing it")
            
        self.conn.close()
    
    
    def detect_entities(self, nlq):
        '''Detect entities in a Natural Language Query
        
        Args:
            
            
        Returns:
            
        
        '''
        return detect_entities(nlq, self.config.ENTITY_DETECTION_SCORE_THR, 
                               self.config.DRUG_RELATIONSHIP_SCORE_THR)
    
    
    def process_entities(self, entities, **kwargs):
        '''Process entiteis by adding disambiguation options to match OMOP CDM terminology & assign placeholder
        
        Args:
            
            
        Returns:
            
        
        '''
        entities = deepcopy(entities)
#         TODO: Implement add_omop_disambiguation_options and add_placeholders
        entities = add_omop_disambiguation_options(entities)
        
        entities = add_placeholders(entities, **kwargs)
        
        return entities
        
        
    def replace_name_for_placeholder(self, nlq, entities):
        '''Comment
        
        Args:
            
            
        Returns:
            
        
        '''
        nlq2 = replace_name_for_placeholder(nlq, entities)
        return nlq2
    
    
    def ml_call(self, nlq):
        '''Comment
        
        Args:
            
            
        Returns:
            
        
        '''
        sql_query = self.model(nlq, self.config.INPUT_MAX_LENGTH, self.config.OUTPUT_MAX_LENGTH)
        return sql_query
    
       
    def render_template_query(self, template_sql, entities):
        '''Comment
        
        Args:
            
            
        Returns:
            
        
        '''
        return render_template_query(self.config, template_sql, entities)
    
    
    def execute_sql_query(self, sql_query):
        '''Comment
        
        Args:
            
            
        Returns:
            
        
        '''
        self._open_redshift_connection()
        cursor = self.conn.cursor()
        out_df = execute_query(cursor, sql_query)
        self._close_redshift_connection()
        return out_df
    
    
    def __call__(self, nlq):
        '''Comment
        
        Args:
            
            
        Returns:
            
        
        '''
        # step1: detect_entities
        entities = self.detect_entities(nlq)
        
        # step2: disambiguate to OMOP CDM ontology & assign placeholder
        entities = slef.process_entities(entities)
        
        # step3: replace placeholder in nlq -> nlq2
        nlq2 = self.replace_name_for_placeholder(nlq, entities)
        
        # step4: exectu ML to get sql 
        template_sql = self.ml_call(nlq2)
        
        # step5: render sql query
        final_sql = self.render_template_query(template_sql, entities)
        
        # execute sql query
        result = self.execute_sql_query(final_sql)
        
        return result
    
    
if __name__=='__main__':
    
    import config
    tool = nlq2SqlTool(config)
    
    query = 'How many people are taking Aspirin?'
    
    df = tool(query)
    
    print('Input :', query)
    print('Output :', df)
    