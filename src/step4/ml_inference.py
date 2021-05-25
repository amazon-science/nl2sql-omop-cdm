
import re
# from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from os import path as osp
import argparse
from model import T5FineTuner
import torch

PAD_P = re.compile('<pad> |</s>')

file_dir = osp.dirname(osp.realpath(__file__))
MODEL_PATH = osp.join(file_dir, 'step4/model/0506_wikisql_all_v1e4.ckpt')

def load_model(fp):
    #import pdb; pdb.set_trace()
    checkpoint = torch.load(fp)
    args = argparse.Namespace(**checkpoint['hyper_parameters'])
    model = T5FineTuner(args)
    model.load_state_dict(checkpoint['state_dict'])
    return model


class Inferencer(object):
    
    def __init__(self, model_path):

        self.model = load_model(model_path)
        self.tokenizer = self.model.tokenizer
#         self.tokenizer = AutoTokenizer.from_pretrained("mrm8488/t5-base-finetuned-wikiSQL")
#         self.model = AutoModelForSeq2SeqLM.from_pretrained("mrm8488/t5-base-finetuned-wikiSQL")

    def __call__(self, query):
        
        input_text = "translate English to SQL: %s </s>" % query
        
        features = self.tokenizer.batch_encode_plus([input_text], 
                                  max_length=200,
                                  padding='max_length', 
                                  truncation=True,
                                  return_tensors='pt')
        

        output = self.model.generate(input_ids=features['input_ids'], 
                                     attention_mask=features['attention_mask'],
                                     max_length=756, 
                                     num_beams=2,
                                     repetition_penalty=2.5, 
                                     length_penalty=1.0)
        
        output = self.tokenizer.decode(output[0])
        
        # generic sql post-processing
        output = re.sub(PAD_P, '', output)
        output = output.replace('[', '<').replace(']', '>').strip()

        return output

            
if __name__=="__main__":
    
    query = "How many people are taking Aspirin?"
    
    inferencer = Inferencer()
    
    sql = inferencer.get_sql(query)
    
    print("Input: ", query)
    print("Output: ", sql)