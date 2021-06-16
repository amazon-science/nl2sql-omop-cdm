"""
Module to load and infer query from the given input question.
"""
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
    """
    Loads trained T5 models from a checkpoint file.
    
    Args:
        fp(str): Checkpoint file path.
    
    Returns:
        T5FineTuner object with the loaded weights.
    """
    if torch.cuda.is_available():
        checkpoint = torch.load(fp)
    else:
        checkpoint = torch.load(fp, map_location=torch.device('cpu'))
        
    args = argparse.Namespace(**checkpoint['hyper_parameters'])
    model = T5FineTuner(args)
    model.load_state_dict(checkpoint['state_dict'])
    return model


class Inferencer(object):
    
    def __init__(self, model_path):
        ''' Initialize model and tokenizer base on a pkl filepath.
    
        Args:
            model_path (str): Absolute path to the stored model.

        Returns:
            str: None

        '''
        self.model = load_model(model_path)
        self.tokenizer = self.model.tokenizer


    def __call__(self, query, input_max_length=256, output_max_length=750):
        '''Maps a general NLQ (with placeholders) to a general SQL query (with placeholders)
    
        Args:
            query (str): General Natural Language Query.
            input_max_length (int): Input sequence length used by the transformer model.
            output_max_length (int): Output sequence length used by the transformer model.

        Returns:
            str: Generic SQL Query.
        '''
        input_text = "translate English to SQL: %s </s>" % query
        
        features = self.tokenizer.batch_encode_plus([input_text], 
                                  max_length=input_max_length,
                                  padding='max_length', 
                                  truncation=True,
                                  return_tensors='pt')
        

        output = self.model.model.generate(input_ids=features['input_ids'], 
                                     attention_mask=features['attention_mask'],
                                     max_length=output_max_length, 
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
    input_max_length=256
    output_max_length=750
    
    inferencer = Inferencer()
    
    sql = inferencer.get_sql(query, input_max_length, output_max_length)
    
    print("Input: ", query)
    print("Output: ", sql)
