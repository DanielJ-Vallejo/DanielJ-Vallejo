"""Configuration for the BETO fine-tuning pipeline."""

from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PROJECT_ROOT.parent
DATA_DIR = REPO_ROOT / "data" / "raw" / "sentiment-analysis"

TRAIN_FILE = DATA_DIR / "MeIA_2025_train.xlsx"
TEST_FILE = DATA_DIR / "MeIA_2025_test_wo_labels.xlsx"


@dataclass(frozen=True)
class TrainingConfig:
    """Hyperparameters used for the final MeIA 2025 submission."""

    model_name: str = "dccuchile/bert-base-spanish-wwm-uncased"  # BETO
    # Revisión fijada del modelo: reproducibilidad + seguridad de cadena de
    # suministro (evita descargar pesos alterados; ver bandit B615 / CWE-494).
    model_revision: str = "d1c9c4565c9d6731e57ed7f027b802697bad861e"
    num_labels: int = 5
    max_length: int = 256
    batch_size: int = 16
    num_epochs: int = 8
    learning_rate: float = 2e-5
    weight_decay: float = 0.1
    warmup_ratio: float = 0.1
    hidden_dropout: float = 0.4
    attention_dropout: float = 0.3
    frozen_layers: int = 6          # freeze the first N encoder layers
    val_fraction: float = 0.1
    random_state: int = 42
    output_dir: str = "results"
