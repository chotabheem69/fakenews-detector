"""
Fine-Tuning BERT for Fake News Sequence Classification.
======================================================
This script implements end-to-end fine-tuning of BERT (Bidirectional Encoder Representations
from Transformers) on the IEEE DataPort / Kaggle / ISOT Fake News Dataset.

Architecture:
  Input Tokens -> BERT Base (12-layers, 768-dim) -> [CLS] Token Pooler -> Dropout(0.3) -> Linear(768, 2) -> Logits (Real vs Fake)

Usage:
  python train_bert.py --data_path data/fake_news_dataset.csv --epochs 3 --batch_size 16
"""

import os
import argparse
import logging
from pathlib import Path
from typing import Tuple, List

import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TrainBERT")

def train_bert_model(data_path: str, output_dir: str, epochs: int = 3, batch_size: int = 16, lr: float = 2e-5):
    """
    Fine-tunes BERT on fake news dataset.
    """
    try:
        import torch
        from torch.utils.data import Dataset, DataLoader
        from transformers import (
            AutoTokenizer, 
            AutoModelForSequenceClassification, 
            get_linear_schedule_with_warmup
        )
        from torch.optim import AdamW
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
    except ImportError:
        logger.error(
            "Missing PyTorch or Transformers! Install them via:\n"
            "pip install torch transformers scikit-learn numpy pandas"
        )
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using compute device: {device}")

    # 1. Load or Generate Dataset
    texts = []
    labels = [] # 0: Fake, 1: Real

    csv_path = Path(data_path)
    if csv_path.exists():
        import pandas as pd
        logger.info(f"Loading dataset from: {csv_path}")
        df = pd.read_csv(csv_path)
        
        # Harmonize column names (IEEE DataPort / Kaggle format)
        title_col = next((c for c in df.columns if c.lower() in ["title", "headline"]), None)
        text_col = next((c for c in df.columns if c.lower() in ["text", "content", "body"]), None)
        label_col = next((c for c in df.columns if c.lower() in ["label", "target", "class", "verdict"]), None)

        if text_col and label_col:
            for _, row in df.iterrows():
                t = str(row[title_col]) if title_col else ""
                b = str(row[text_col])
                full = f"{t}. {b}".strip()
                if len(full) > 20:
                    texts.append(full)
                    # Convert label to 0 (Fake) or 1 (Real)
                    raw_lbl = str(row[label_col]).strip().lower()
                    if raw_lbl in ["1", "real", "true", "reliable"]:
                        labels.append(1)
                    else:
                        labels.append(0)
            logger.info(f"Loaded {len(texts)} samples from CSV (Real: {sum(labels)}, Fake: {len(labels) - sum(labels)}).")
        else:
            logger.warning(f"Could not automatically detect text and label columns in {df.columns}. Generating synthetic dataset.")
            csv_path = None

    if not csv_path or len(texts) == 0:
        logger.info("Using built-in IEEE DataPort Fake News dataset collection...")
        try:
            from backend.models.dataset_manager import load_ieee_dataset
            records = load_ieee_dataset()
            for r in records:
                full = f"{r['title']}. {r['text']}".strip()
                texts.append(full)
                labels.append(1 if r["label"] == 1 else 0)
            logger.info(f"Loaded {len(texts)} samples from IEEE DataPort dataset (Real: {sum(labels)}, Fake: {len(labels) - sum(labels)}).")
        except Exception as e:
            logger.warning(f"Could not load dataset manager: {e}. Using fallback synthetic samples.")
            sample_data = [
                ("NASA confirms discovery of water ice deposits inside deep lunar craters by Chandrayaan.", 1),
                ("World Health Organization issues global guidance on seasonal influenza vaccination.", 1),
                ("Federal Reserve announces benchmark interest rate decision following policy meeting.", 1),
                ("Peer-reviewed study published in Nature links Mediterranean diet to cardiac health.", 1),
                ("European Space Agency launches automated environmental monitoring satellite.", 1),
                ("SHOCKING: Drinking boiled onion juice cures diabetes in 24 hours, Big Pharma in panic!", 0),
                ("BOMBSHELL: Secret lunar alien base exposed by anonymous insider before video deleted!", 0),
                ("Scientists admit Earth is secretly hollow and populated by lizard elites!", 0),
                ("5G radiation transmits mind-controlling nano-chips directly to cell phones!", 0),
                ("Miracle magnetic patch melts 30 pounds of belly fat overnight with zero diet!", 0)
            ] * 20
            texts = [item[0] for item in sample_data]
            labels = [item[1] for item in sample_data]

    # Split train and validation
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    # 2. Tokenizer & Dataset Class
    model_name = "distilbert-base-uncased" # Fast, high performance BERT variant
    logger.info(f"Loading tokenizer: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    class FakeNewsDataset(Dataset):
        def __init__(self, encodings, labels):
            self.encodings = encodings
            self.labels = labels

        def __getitem__(self, idx):
            item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
            item['labels'] = torch.tensor(self.labels[idx])
            return item

        def __len__(self):
            return len(self.labels)

    logger.info("Tokenizing training and validation sequences...")
    train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=256)
    val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=256)

    train_dataset = FakeNewsDataset(train_encodings, train_labels)
    val_dataset = FakeNewsDataset(val_encodings, val_labels)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)

    # 3. Model Architecture
    logger.info("Initializing BERT with Sequence Classification Head (num_labels=2)...")
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
    model.to(device)

    # 4. Optimizer and Learning Rate Scheduler
    optimizer = AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    total_steps = len(train_loader) * epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer, 
        num_warmup_steps=int(total_steps * 0.1), 
        num_training_steps=total_steps
    )

    # 5. Training Loop
    logger.info(f"Starting Training for {epochs} epochs...")
    for epoch in range(epochs):
        model.train()
        total_train_loss = 0

        for batch in train_loader:
            optimizer.zero_grad()
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            total_train_loss += loss.item()

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()

        avg_train_loss = total_train_loss / len(train_loader)

        # Validation
        model.eval()
        predictions = []
        true_labels = []

        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)

                outputs = model(input_ids, attention_mask=attention_mask)
                logits = outputs.logits
                preds = torch.argmax(logits, dim=1).cpu().numpy()
                predictions.extend(preds)
                true_labels.extend(labels.cpu().numpy())

        acc = accuracy_score(true_labels, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(true_labels, predictions, average='binary')

        logger.info(
            f"Epoch {epoch+1}/{epochs} - "
            f"Loss: {avg_train_loss:.4f} | "
            f"Val Accuracy: {acc*100:.2f}% | "
            f"Precision: {precision:.4f} | "
            f"Recall: {recall:.4f} | "
            f"F1-Score: {f1:.4f}"
        )

    # 6. Save Model & Tokenizer
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Saving fine-tuned BERT checkpoint to: {output_path}")
    model.save_pretrained(str(output_path))
    tokenizer.save_pretrained(str(output_path))
    logger.info("✓ Training and model export completed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tune BERT for Fake News Detection")
    parser.add_argument("--data_path", type=str, default="data/ieee_fake_news_dataset.csv", help="Path to IEEE DataPort CSV")
    parser.add_argument("--output_dir", type=str, default="saved_models/bert_fake_news", help="Directory to save model")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size")
    parser.add_argument("--lr", type=float, default=2e-5, help="Learning rate")
    args = parser.parse_args()

    train_bert_model(
        data_path=args.data_path,
        output_dir=args.output_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr
    )

