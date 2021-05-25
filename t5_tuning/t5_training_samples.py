import argparse
import torch
import os
import time
import pytorch_lightning as pl
from pytorch_lightning import loggers as pl_loggers
from model import T5FineTuner, set_seed
from callback import LoggingCallback, logger
from config import model_params


def train(args):

    model = T5FineTuner(args)

    checkpoint_callback = pl.callbacks.ModelCheckpoint(
        monitor="val_loss",
        filename='model_checkpoint-{epoch:02d}-{val_loss:.3f}',
        save_top_k=-1,
        save_last=True
    )

    tb_logger = pl_loggers.TensorBoardLogger(args.output_dir)
    
    train_params = dict(
        accumulate_grad_batches=args.gradient_accumulation_steps,
        gpus=-1,
        max_epochs=args.num_train_epochs,
        precision= 16 if args.fp_16 else 32,
        amp_level=args.opt_level,
        resume_from_checkpoint=args.resume_from_checkpoint,
        gradient_clip_val=args.max_grad_norm,
        checkpoint_callback=checkpoint_callback,
        val_check_interval=args.val_check_interval,
        logger=tb_logger,
        callbacks=[LoggingCallback()],
        accelerator="dp", 
    )    

    trainer = pl.Trainer(**train_params)
    trainer.fit(model)

    # After model has been trained, save its state into output_data_dir
    with open(os.path.join(args.output_dir, "model_{0}.pth".format(time.strftime("%Y%m%d-%H%M%S"))), 'wb') as f:
        torch.save(model.state_dict(), f)


if __name__ == "__main__":
    print(model_params)
    if model_params["seed"]:
        set_seed(model_params["seed"])
    args = argparse.Namespace(**model_params)
    train(args)
    
 