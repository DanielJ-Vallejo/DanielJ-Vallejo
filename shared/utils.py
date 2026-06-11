"""General-purpose utilities shared across portfolio projects."""

from __future__ import annotations

import json
import random
import time
from contextlib import contextmanager
from pathlib import Path

import numpy as np


def set_seed(seed: int = 42) -> None:
    """Seed python and numpy RNGs (and torch, when available)."""
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch

        torch.manual_seed(seed)
    except ImportError:
        pass


@contextmanager
def timer(label: str = "block"):
    """Context manager printing the wall-clock time of a code block."""
    t0 = time.perf_counter()
    yield
    print(f"[{label}] {time.perf_counter() - t0:.2f}s")


def save_json(data: dict, path: str | Path) -> None:
    """Write a dict as pretty-printed UTF-8 JSON, creating parent dirs."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_json(path: str | Path) -> dict:
    """Read a UTF-8 JSON file into a dict."""
    return json.loads(Path(path).read_text(encoding="utf-8"))
