import os
import json
import pandas as pd
from sklearn.model_selection import train_test_split
from nlp import load_dataset
from transformers import T5Tokenizer
from torch.utils.data import Dataset

class NL2SQLDataset(Dataset):
    def __init__(self, data_dir: str,
                       data_split: str, 
                       input_length: int, 
                       output_length: int,
                       num_samples: int = None,
                       tokenizer = T5Tokenizer.from_pretrained('t5-small')) -> None:

        data_path = os.path.join(data_dir, f'{data_split}.csv')
        self.dataset = load_dataset('csv', data_files={data_split: data_path})
        self.data_split = data_split
        #self.dataset =  load_dataset('wikisql', 'all', data_dir='data/', split=data_split)
        if num_samples:
            self.dataset = self.dataset.select(list(range(0, num_samples)))
        self.input_length = input_length
        self.tokenizer = tokenizer
        self.output_length = output_length
  
    def __len__(self) -> int:
        return self.dataset[self.data_split].shape[0]
    

    def convert_to_features(self, example_batch):
        input_ = "translate English to SQL: " + example_batch['question']
        target_ = example_batch['query']

        source = self.tokenizer.batch_encode_plus([input_], max_length=self.input_length, 
                                                     padding='max_length', truncation=True, return_tensors="pt")
        
        targets = self.tokenizer.batch_encode_plus([target_], max_length=self.output_length, 
                                                     padding='max_length', truncation=True, return_tensors="pt")
    
       
        return source, targets
  
    def __getitem__(self, index: int) -> dict:
        source, targets = self.convert_to_features(self.dataset[self.data_split][index])
        
        source_ids = source["input_ids"].squeeze()
        target_ids = targets["input_ids"].squeeze()

        src_mask    = source["attention_mask"].squeeze()
        target_mask = targets["attention_mask"].squeeze()

        return {"source_ids": source_ids, "source_mask": src_mask, "target_ids": target_ids, "target_mask": target_mask}


def get_dataset(tokenizer, data_split: str, num_samples: int, args) -> NL2SQLDataset:
      return NL2SQLDataset(data_dir=args.data_dir,
                           data_split=data_split,
                           num_samples=num_samples,  
                           input_length=args.max_input_length, 
                           output_length=args.max_output_length)
    
    
def preprocess_data(json_path, csv_path):
    """Loads data, cleans and saves it in csv format."""
    #Load json data
    with open(json_path, 'r') as fp:
        data = json.load(fp)
        
    #Convert to Pandas Dataframe
    df = pd.DataFrame(data)

    #Remove unnecessary columns
    columns = df.columns.tolist()
    excluded_cols = [col for col in columns if 'Unnamed' in col]
    df.drop(excluded_cols, axis=1, inplace=True)

    #Save data
    output_dir = os.path.dirname(csv_path)
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(csv_path, index=False)
    
    return df
    
    
def split_data(csv_path, output_dir, val_size=0.1, test_size=0.1):
    """Splits data into train/validation/test."""
    #Load data
    df = pd.read_csv(csv_path)
    
    #Split data
    df_train, df_val_test = train_test_split(df, test_size=val_size+test_size, shuffle=True)
    df_val, df_test = train_test_split(df_val_test, test_size=test_size/(val_size+test_size))
    
    #Save data
    output_dir = os.path.dirname(csv_path)
    os.makedirs(output_dir, exist_ok=True)
    
    train_path = os.path.join(output_dir, 'train.csv')
    val_path = os.path.join(output_dir, 'validation.csv')
    test_path = os.path.join(output_dir, 'test.csv')
    
    df_train.to_csv(train_path, index=False)
    if val_size:
        df_val.to_csv(val_path, index=False)
    if test_size:
        df_test.to_csv(test_path, index=False)
    return df_train, df_val, df_test
    
    
    
    
    
    