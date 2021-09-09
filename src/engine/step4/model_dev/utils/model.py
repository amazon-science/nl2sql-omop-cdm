"""
The module creates a class to fine-tune T5-based pretrained model.
"""

import torch
import random
import numpy as np
import argparse
import time
import torch
import numpy as np
from nlp import load_metric
import pytorch_lightning as pl
from torch.utils.data import DataLoader
from typing import Callable, Dict, Iterable, List, Tuple, Union
from dataset import get_dataset
from torch.optim.lr_scheduler import CosineAnnealingLR


from transformers import (
    AdamW,
    T5ForConditionalGeneration,
    T5Tokenizer,
    get_linear_schedule_with_warmup,
)


class T5FineTuner(pl.LightningModule):
    """
    Class to create T5-based fine-tuner object.
    """

    def __init__(self, hparams) -> None:
        """
        Creates fine-tuner object.

        Args:
            hparams(argparse.Namespace): Hyperparamters of the model object to be created.
            added_tokens(list). Tokens to be added to an existing vocab.
        """

        super(T5FineTuner, self).__init__()
        self.hparams = hparams
        self.model = T5ForConditionalGeneration.from_pretrained(hparams.model_name)
        self.tokenizer = T5Tokenizer.from_pretrained(hparams.tokenizer_name)

        if self.hparams.freeze_embeds:
            self.freeze_embeds()
        if self.hparams.freeze_encoder:
            self.freeze_params(self.model.get_encoder())
            self.assert_all_frozen(self.model.get_encoder())

        self.new_special_tokens = self.added_tokens()

        additional_special_tokens = (
            self.tokenizer.additional_special_tokens + self.new_special_tokens
        )
        self.tokenizer.add_special_tokens(
            {"additional_special_tokens": additional_special_tokens}
        )

        num_added_toks = self.tokenizer.add_special_tokens(
            {"additional_special_tokens": self.new_special_tokens}
        )
        self.model.resize_token_embeddings(len(self.tokenizer))

        n_observations_per_split = {
            "train": self.hparams.n_train,
            "validation": self.hparams.n_val,
            "test": self.hparams.n_test,
        }
        self.n_obs = {
            k: v if v >= 0 else None for k, v in n_observations_per_split.items()
        }

    def added_tokens(self):
        """Tokens to be added to the pretrained tokenizer/vocab."""
        added_tokens = [
            "[ARG-DRUG]",
            "[ARG-CONDITION]",
            "[ARG-GENDER]",
            "[ARG-RACE]",
            "[ARG-ETHNICITY]",
            "[ARG-STATE]",
            "[ARG-AGE]",
            "[ARG-TIMEDAYS]",
            "[ARG-TIMEYEARS]",
            "[GENDER-TEMPLATE]",
            "[RACE-TEMPLATE]",
            "[ETHNICITY-TEMPLATE]",
            "[STATEID-TEMPLATE]",
            "[CONDITION-TEMPLATE]",
            "[DRUG-TEMPLATE]",
            "[ARG-CONDITION]",
            "[STATENAME-TEMPLATE]",
            "[ARG-DRUG]",
            "[ARG-DAYS]",
            "DATEDIFF",
            "DISTINCT",
            "GREATEST",
            "[SCHEMA]",
            "SELECT",
            "GROUP",
            "LEAST",
            "UNION",
            "COUNT",
            "WHERE",
            "JOIN",
            "FROM",
            "AND",
            "AS",
            "OR",
            "BY",
            "ON",
        ] + [f"[{i}]" for i in range(10)]

        return added_tokens

    def freeze_params(self, model):
        """Freezes model paramters.

        Args:
            model(T5ForConditionalGeneration): T5ForConditionalGeneration model object.
        """
        for par in model.parameters():
            par.requires_grad = False

    def freeze_embeds(self):
        """Freeze token embeddings and positional embeddings for bart, just token embeddings for t5."""
        try:
            self.freeze_params(self.model.model.shared)
            for d in [self.model.model.encoder, self.model.model.decoder]:
                self.freeze_params(d.embed_positions)
                self.freeze_params(d.embed_tokens)
        except AttributeError:
            self.freeze_params(self.model.shared)
            for d in [self.model.encoder, self.model.decoder]:
                self.freeze_params(d.embed_tokens)

    def lmap(self, f: Callable, x: Iterable) -> List:
        """list(map(f, x))"""
        return list(map(f, x))

    def assert_all_frozen(self, model):
        """Check all model frozen params."""
        model_grads: List[bool] = list(self.grad_status(model))
        n_require_grad = sum(self.lmap(int, model_grads))
        npars = len(model_grads)
        assert not any(
            model_grads
        ), f"{n_require_grad/npars:.1%} of {npars} weights require grad"

    def is_logger(self):
        """Check model copy used for logging."""
        return self.trainer.global_rank <= 0

    def parse_score(self, result):
        """Parses all scores and rounds the values."""
        return {k: round(v.mid.fmeasure * 100, 4) for k, v in result.items()}

    def forward(
        self,
        input_ids,
        attention_mask=None,
        decoder_input_ids=None,
        decoder_attention_mask=None,
        labels=None,
    ):
        """Wrapper for model's forward method."""
        return self.model(
            input_ids,
            attention_mask=attention_mask,
            decoder_input_ids=decoder_input_ids,
            decoder_attention_mask=decoder_attention_mask,
            labels=labels,
        )

    def _step(self, batch):
        """
        Get loss for a given train step.

        Args:
            batch(dict): Batch of examples.
        Returns:
            Model loss.
        """
        labels = batch["target_ids"]
        labels[labels[:, :] == self.tokenizer.pad_token_id] = -100

        outputs = self(
            input_ids=batch["source_ids"],
            attention_mask=batch["source_mask"],
            labels=labels,
            decoder_attention_mask=batch["target_mask"],
        )

        loss = outputs[0]

        return loss

    def ids_to_clean_text(self, generated_ids):
        """
        Get text from the generated token ids.

        Args:
            generated_ids(Tensor): Token ids.

        Returns:
            Corresponding text.
        """

        gen_text = self.tokenizer.batch_decode(
            generated_ids, skip_special_tokens=False, clean_up_tokenization_spaces=True
        )
        return self.lmap(str.strip, gen_text)

    def _generative_step(self, batch):
        """
        Get metrics(val_loss) from a given step

        Args:
            batch(dict): Batch of examples.

        Returns:
            dictionary of metric values (validation loss)
        """

        loss = self._step(batch)
        base_metrics = {"val_loss": loss}

        return base_metrics

    def training_step(self, batch, batch_idx):
        """
        Get loss and tensorboard logs from a training step.

        Args:
            batch(dict): Dictionary of batch examples.

        Returns:
            Training loss and tensorboard logs.
        """
        loss = self._step(batch)

        self.log(
            "train_loss",
            loss,
            on_step=True,
            on_epoch=True,
            sync_dist=True,
            prog_bar=True,
        )

        tensorboard_logs = {"loss": loss.detach()}

        return {"loss": loss, "log": tensorboard_logs}

    def validation_step(self, batch, batch_idx):
        """
        Get validation loss from a validation step.

        Args:
            batch(dict): Dictionary of batch examples.

        Returns:
            Validation loss.
        """

        return self._generative_step(batch)

    def validation_epoch_end(self, outputs):
        """
        Gets loss and log at the end of validation epoch.

        Args:
            outputs(Tensor): Model outputs

        Returns:
            Dictionary of validation loss and logs.
        """

        avg_loss = torch.stack([x["val_loss"] for x in outputs]).mean()
        tensorboard_logs = {"val_loss": avg_loss}

        self.target_gen = []
        self.prediction_gen = []

        self.log("val_loss", avg_loss, on_epoch=True, sync_dist=True, prog_bar=True)
        tensor_board_logs = {"val_loss": avg_loss.detach()}

        return {"val_loss": avg_loss, "log": tensor_board_logs}

    def configure_optimizers(self):
        """
        Prepare optimizer and schedule (linear warmup and decay)

        Args:
            None

        Returns:
            Tuple of optimizer and scheduler.
        """

        model = self.model
        no_decay = ["bias", "LayerNorm.weight"]
        optimizer_grouped_parameters = [
            {
                "params": [
                    p
                    for n, p in model.named_parameters()
                    if not any(nd in n for nd in no_decay)
                ],
                "weight_decay": self.hparams.weight_decay,
            },
            {
                "params": [
                    p
                    for n, p in model.named_parameters()
                    if any(nd in n for nd in no_decay)
                ],
                "weight_decay": 0.0,
            },
        ]
        optimizer = AdamW(
            optimizer_grouped_parameters,
            lr=self.hparams.learning_rate,
            eps=self.hparams.adam_epsilon,
        )
        self.opt = optimizer
        scheduler = CosineAnnealingLR(
            optimizer, T_max=100, eta_min=1e-5, last_epoch=-1, verbose=False
        )

        return [optimizer], [scheduler]

    def train_dataloader(self):
        """
        Train data loader.

        Args:
            None

        Returns:
            DataLoader object.
        """
        n_samples = self.n_obs["train"]

        train_dataset = get_dataset(
            tokenizer=self.tokenizer,
            data_split="train",
            num_samples=n_samples,
            args=self.hparams,
        )
        dataloader = DataLoader(
            train_dataset,
            batch_size=self.hparams.train_batch_size,
            drop_last=True,
            shuffle=True,
            prefetch_factor=4,
            num_workers=96,
        )
        t_total = (
            (
                len(dataloader.dataset)
                // (self.hparams.train_batch_size * max(1, self.hparams.n_gpu))
            )
            // self.hparams.gradient_accumulation_steps
            * float(self.hparams.num_train_epochs)
        )
        scheduler = get_linear_schedule_with_warmup(
            self.opt,
            num_warmup_steps=self.hparams.warmup_steps,
            num_training_steps=t_total,
        )
        self.lr_scheduler = scheduler
        return dataloader

    def val_dataloader(self):
        """
        Validation data loader.

        Args:
            None

        Returns:
            DataLoader object.
        """
        n_samples = self.n_obs["validation"]
        validation_dataset = get_dataset(
            tokenizer=self.tokenizer,
            data_split="validation",
            num_samples=n_samples,
            args=self.hparams,
        )

        return DataLoader(
            validation_dataset,
            batch_size=self.hparams.eval_batch_size,
            prefetch_factor=4,
            num_workers=96,
        )

    def test_dataloader(self):
        """
        Test data loader.

        Args:
            None

        Returns:
            DataLoader object.
        """
        n_samples = self.n_obs["test"]
        test_dataset = get_dataset(
            tokenizer=self.tokenizer,
            data_split="test",
            num_samples=n_samples,
            args=self.hparams,
        )

        return DataLoader(
            test_dataset, batch_size=self.hparams.eval_batch_size, num_workers=24
        )


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
        checkpoint = torch.load(fp, map_location=torch.device("cpu"))

    args = argparse.Namespace(**checkpoint["hyper_parameters"])
    model = T5FineTuner(args)
    model.load_state_dict(checkpoint["state_dict"])
    return model


def set_seed(seed):
    """Seed random seed if needed."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
