"""
Config file for T5 model fine-tuning
"""

# Model pyperparameters
model_params = {
    "data_dir": "/home/ec2-user/SageMaker/efs/data/pilot_nl2sql_dev/0607_final_data/splits/In-Scope/all/",
    "output_dir": "/home/ec2-user/SageMaker/efs/data/pilot_nl2sql_dev/0607_models/p4_v2/",
    "model_name": "mrm8488/t5-base-finetuned-wikiSQL",
    "tokenizer_name": "mrm8488/t5-base-finetuned-wikiSQL",
    "max_input_length": 256,
    "max_output_length": 576,
    "freeze_encoder": False,
    "freeze_embeds": False,
    "learning_rate": 1e-3,
    "weight_decay": 0.0,
    "adam_epsilon": 1e-8,
    "warmup_steps": 0,
    "train_batch_size": 128,
    "eval_batch_size": 256,
    "num_train_epochs": 5,
    "gradient_accumulation_steps": 1,
    "n_gpu": -1,
    "resume_from_checkpoint": True,
    "val_check_interval": 0.8,
    "n_train": -1,
    "n_val": -1,
    "n_test": -1,
    "early_stop_callback": True,
    "fp_16": False,
    "opt_level": "O1",
    "max_grad_norm": 1.0,
    "seed": None,
    "automatic_optimization": True,
}
