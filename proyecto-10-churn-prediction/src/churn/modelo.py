# -*- coding: utf-8 -*-
"""Modelo de predicción de churn (regresión logística, interpretable).

Se elige regresión logística porque sus coeficientes se leen directamente como
los "drivers" del abandono — útil para la recomendación de negocio, no solo para
predecir.
"""
from __future__ import annotations

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

_CONTRATO_COD = {"mes a mes": 0, "anual": 1, "bianual": 2}
FEATURES = ["tenure_meses", "contrato_cod", "cargo_mensual",
            "servicios_extra", "llamadas_soporte", "factura_electronica"]


def _matriz(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    x["contrato_cod"] = x["tipo_contrato"].map(_CONTRATO_COD)
    return x[FEATURES]


def entrenar(df: pd.DataFrame, semilla: int = 42) -> dict:
    """Entrena y evalúa; devuelve métricas, modelo y drivers ordenados."""
    x, y = _matriz(df), df["churn"]
    x_tr, x_te, y_tr, y_te = train_test_split(
        x, y, test_size=0.25, random_state=semilla, stratify=y)
    escala = StandardScaler().fit(x_tr)
    modelo = LogisticRegression(max_iter=1000).fit(escala.transform(x_tr), y_tr)
    proba = modelo.predict_proba(escala.transform(x_te))[:, 1]
    auc = roc_auc_score(y_te, proba)
    drivers = sorted(zip(FEATURES, modelo.coef_[0]),
                     key=lambda t: abs(t[1]), reverse=True)
    return {
        "modelo": modelo,
        "escala": escala,
        "auc": round(float(auc), 3),
        "drivers": [(f, round(float(c), 2)) for f, c in drivers],
    }
