import re
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

PAD_P = re.compile('<pad> |</s>')

class Inferencer(object):
    
    def __init__(self, ):

        self.tokenizer = AutoTokenizer.from_pretrained("mrm8488/t5-base-finetuned-wikiSQL")
#         self.model = AutoModelWithLMHead.from_pretrained("mrm8488/t5-base-finetuned-wikiSQL")
        self.model = AutoModelForSeq2SeqLM.from_pretrained("mrm8488/t5-base-finetuned-wikiSQL")

    def __call__(self, query):
        """
        v0 source: https://huggingface.co/mrm8488/t5-base-finetuned-wikiSQL
        """
        
        input_text = "translate English to SQL: %s </s>" % query
        
        features = self.tokenizer([input_text], return_tensors='pt')
        
        output = self.model.generate(input_ids=features['input_ids'], 
                                attention_mask=features['attention_mask'])
        
        output = self.tokenizer.decode(output[0])
        
        output = re.sub(PAD_P, '', output)

        return output

            
if __name__=="__main__":
    
    query = "How many people are taking Aspirin?"
    
    inferencer = Inferencer()
    
    sql = inferencer.get_sql(query)
    
    print("Input: ", query)
    print("Output: ", sql)