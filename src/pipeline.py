from step1.entity_extraction import detect_entities
from step2.entity_processing import add_omop_disambiguation_options, add_placeholders
from step3.nlq_processing import replace_name_for_placeholder
# step4: ml module -> ml class wrapped around saved model and method to do inference.
from step5.sql_processing import render_template_query
from utils.query_execution import connect_to_db, execute_query

class nlq2SqlTool(object):
    
    def __init__(self, config):
        
        # initialize arguments
        self.config = config
    
        # open redshift connection and initialize ML object
        
        
    def _open_redshift_connection(self, ):
        self.conn = connect_to_db(self.config.REDSHIFT_PARM)
    
    
    def _close_redshift_connection(self, ):
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
    
    def process_entities(self, entities):
        '''Process entiteis by adding disambiguation options to match OMOP CDM terminology & assign placeholder
        
        Args:
            
            
        Returns:
            
        
        '''
#         TODO: Implement add_omop_disambiguation_options and add_placeholders
        entities = add_omop_disambiguation_options(entities)
        
        entities = add_placeholders(entities)
        
        return entities
        
    def replace_name_for_placeholder(self, nlq, entities):
        #         TODO: Implement call model (inside funct: seq-foward + idx2token + concat)
        nlq2 = replace_name_for_placeholder(nlq, entities)
        return nlq2
    
    
    def ml_call(self, nlq):
#         TODO: Implement call model (inside funct: seq-foward + idx2token + concat)
        raise NotImplemented()
    
       
    def render_template_query(self, template_sql, entities):
        
        return render_template_query(self.config, template_sql, entities)
    
    
    def execute_sql_query(self, sql_query):
        self._open_redshift_connection()
        cursor = self.conn.cursor()
        out_df = execute_query(cursor, sql_query)
        self._close_redshift_connection()
        return out_df
    
    
    def nlq2sql(self, nlq):
        
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