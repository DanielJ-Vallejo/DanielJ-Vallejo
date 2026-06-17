"""BETO fine-tuning for 5-class polarity classification.

Heavy dependencies (torch / transformers / datasets) are imported lazily so
the rest of the package stays usable in lightweight environments. Run on a
GPU machine or Google Colab; on the MeIA 2025 challenge this configuration
reached a leaderboard score of 0.5889.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

from .config import TrainingConfig
from .data import oversample_minority


def train(
    df_train: pd.DataFrame,
    cfg: TrainingConfig | None = None,
    output_dir: Path | str | None = None,
):
    """Fine-tune BETO and return the fitted ``transformers.Trainer``."""
    import torch
    from datasets import Dataset
    from transformers import (
        AutoModelForSequenceClassification,
        AutoTokenizer,
        EarlyStoppingCallback,
        Trainer,
        TrainingArguments,
    )

    cfg = cfg or TrainingConfig()
    output_dir = str(output_dir or cfg.output_dir)

    df_bal = oversample_minority(
        df_train[["text", "label"]], random_state=cfg.random_state
    )
    train_df, val_df = train_test_split(
        df_bal,
        test_size=cfg.val_fraction,
        stratify=df_bal["label"],
        random_state=cfg.random_state,
    )

    tokenizer = AutoTokenizer.from_pretrained(cfg.model_name, revision=cfg.model_revision)

    def tokenize(batch):
        return tokenizer(
            batch["text"],
            padding="max_length",
            truncation=True,
            max_length=cfg.max_length,
        )

    train_ds = Dataset.from_pandas(train_df, preserve_index=False).map(
        tokenize, batched=True
    )
    val_ds = Dataset.from_pandas(val_df, preserve_index=False).map(
        tokenize, batched=True
    )

    model = AutoModelForSequenceClassification.from_pretrained(
        cfg.model_name,
        revision=cfg.model_revision,
        num_labels=cfg.num_labels,
        hidden_dropout_prob=cfg.hidden_dropout,
        attention_probs_dropout_prob=cfg.attention_dropout,
        id2label={i: str(i + 1) for i in range(cfg.num_labels)},
        label2id={str(i + 1): i for i in range(cfg.num_labels)},
    )

    # Freeze the lower encoder layers: keeps general Spanish morphology
    # intact and reduces overfitting on ~5k training reviews.
    for name, param in model.bert.named_parameters():
        if name.startswith("encoder.layer"):
            if int(name.split(".")[2]) < cfg.frozen_layers:
                param.requires_grad = False

    total_steps = (len(train_ds) // (cfg.batch_size * 2)) * cfg.num_epochs
    args = TrainingArguments(
        output_dir=output_dir,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=1,
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        greater_is_better=True,
        per_device_train_batch_size=cfg.batch_size,
        per_device_eval_batch_size=cfg.batch_size,
        gradient_accumulation_steps=2,
        learning_rate=cfg.learning_rate,
        weight_decay=cfg.weight_decay,
        num_train_epochs=cfg.num_epochs,
        warmup_steps=int(total_steps * cfg.warmup_ratio),
        lr_scheduler_type="cosine",
        logging_steps=50,
        report_to="none",
        fp16=torch.cuda.is_available(),
        gradient_checkpointing=True,
        optim="adamw_torch",
    )

    def compute_metrics(p):
        preds = np.argmax(p.predictions, axis=1)
        return {
            "accuracy": accuracy_score(p.label_ids, preds),
            "f1_macro": f1_score(p.label_ids, preds, average="macro"),
        }

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
    )
    trainer.train()
    return trainer


def predict(trainer, texts: list[str], cfg: TrainingConfig | None = None) -> list[int]:
    """Predict 1-5 polarity ratings for raw (already enriched) texts."""
    from datasets import Dataset
    from transformers import AutoTokenizer

    cfg = cfg or TrainingConfig()
    tokenizer = AutoTokenizer.from_pretrained(cfg.model_name, revision=cfg.model_revision)
    ds = Dataset.from_dict({"text": texts}).map(
        lambda b: tokenizer(
            b["text"], padding="max_length", truncation=True, max_length=cfg.max_length
        ),
        batched=True,
    )
    logits = trainer.predict(ds).predictions
    return (np.argmax(logits, axis=1) + 1).tolist()
