"""Train BETO on the MeIA 2025 dataset and write the official run file.

Requires a GPU (or Google Colab). Usage::

    python scripts/train_meia.py [--output-dir results]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from sentiment_analysis.config import TEST_FILE, TRAIN_FILE, TrainingConfig  # noqa: E402
from sentiment_analysis.data import format_predictions, load_reviews  # noqa: E402
from sentiment_analysis.train import predict, train  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="results")
    args = parser.parse_args()

    for f in (TRAIN_FILE, TEST_FILE):
        if not f.exists():
            sys.exit(
                f"Dataset not found: {f}\n"
                "Place the MeIA 2025 xlsx files under data/raw/sentiment-analysis/ "
                "(they are not redistributed with this repository)."
            )

    df_train = load_reviews(TRAIN_FILE, with_labels=True)
    df_test = load_reviews(TEST_FILE, with_labels=False)
    print(f"train: {len(df_train)} reviews | test: {len(df_test)} reviews")

    cfg = TrainingConfig(output_dir=args.output_dir)
    trainer = train(df_train, cfg)

    preds = predict(trainer, df_test["text"].tolist(), cfg)
    out = PROJECT_ROOT / "reports" / "runs" / "MeIA-BETO.Run.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(format_predictions(preds), encoding="utf-8")
    print(f"Run file written to {out}")


if __name__ == "__main__":
    main()
