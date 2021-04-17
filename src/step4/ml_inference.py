from transformers import AutoModelWithLMHead, AutoTokenizer


class Inferencer(object):
    
    def __init__(self, )

        self.tokenizer = AutoTokenizer.from_pretrained("mrm8488/t5-base-finetuned-wikiSQL")
        self.model = AutoModelWithLMHead.from_pretrained("mrm8488/t5-base-finetuned-wikiSQL")

    def get_sql(self, query):
        """
        v0 source: https://huggingface.co/mrm8488/t5-base-finetuned-wikiSQL
        """
        
        input_text = "translate English to SQL: %s </s>" % query
        
        features = tokenizer([input_text], return_tensors='pt')
        
        output = model.generate(input_ids=features['input_ids'], 
                                attention_mask=features['attention_mask'])

        return tokenizer.decode(output[0])

            
if __name__=="__main__":
    
    query = "How many models were finetuned using BERT as base model?"
    
    inferencer = Inferencer()
    
    sql = inferencer.get_sql(query)
    
    print("Input: ", query)
    print("Output: ", sql)