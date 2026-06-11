"""Central configuration for the fraud detection pipeline."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SimulationConfig:
    """Parameters of the synthetic transaction generator."""

    n_customers: int = 1000
    n_terminals: int = 300
    n_days: int = 120
    start_date: str = "2025-04-01"
    radius: float = 5.0          # customers use terminals within this distance
    random_state: int = 42

    # Fraud scenario parameters. Compromise rates are *per entity per day*
    # so the fraud volume stays realistic (~1-2%) at any network size.
    amount_fraud_threshold: float = 220.0   # scenario 1: any tx above this is fraud
    terminal_compromise_rate: float = 0.0005  # scenario 2: P(terminal compromised) per day
    terminal_compromise_duration: int = 14    # days a compromised terminal stays risky
    customer_compromise_rate: float = 0.0015  # scenario 3: P(card details leaked) per day
    customer_compromise_duration: int = 14
    customer_fraud_amount_factor: float = 5.0


@dataclass(frozen=True)
class FeatureConfig:
    """Windows used for behavioural aggregates."""

    customer_windows: tuple = (1, 7, 30)   # days
    terminal_windows: tuple = (1, 7, 30)   # days
    terminal_delay: int = 7                # label availability delay (days)


@dataclass(frozen=True)
class TrainConfig:
    """Time-aware split: train, delay gap (labels not yet known), test."""

    train_duration: int = 60   # days
    delay_duration: int = 7    # days between train end and test start
    test_duration: int = 30    # days
    random_state: int = 42
    top_k: int = 20            # daily alert budget for Card Precision@k


@dataclass
class PipelineConfig:
    simulation: SimulationConfig = field(default_factory=SimulationConfig)
    features: FeatureConfig = field(default_factory=FeatureConfig)
    training: TrainConfig = field(default_factory=TrainConfig)


INPUT_FEATURES = [
    "TX_AMOUNT",
    "TX_DURING_WEEKEND",
    "TX_DURING_NIGHT",
    "CUSTOMER_ID_NB_TX_1DAY_WINDOW",
    "CUSTOMER_ID_AVG_AMOUNT_1DAY_WINDOW",
    "CUSTOMER_ID_NB_TX_7DAY_WINDOW",
    "CUSTOMER_ID_AVG_AMOUNT_7DAY_WINDOW",
    "CUSTOMER_ID_NB_TX_30DAY_WINDOW",
    "CUSTOMER_ID_AVG_AMOUNT_30DAY_WINDOW",
    "TERMINAL_ID_NB_TX_1DAY_WINDOW",
    "TERMINAL_ID_RISK_1DAY_WINDOW",
    "TERMINAL_ID_NB_TX_7DAY_WINDOW",
    "TERMINAL_ID_RISK_7DAY_WINDOW",
    "TERMINAL_ID_NB_TX_30DAY_WINDOW",
    "TERMINAL_ID_RISK_30DAY_WINDOW",
]

TARGET = "TX_FRAUD"
