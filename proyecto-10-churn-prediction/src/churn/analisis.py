# -*- coding: utf-8 -*-
"""De los datos a una recomendación de retención con valor cuantificado."""
from __future__ import annotations

import pandas as pd


def recomendacion(df: pd.DataFrame) -> dict:
    """Identifica el segmento de mayor riesgo y estima el valor de retenerlo."""
    riesgo = df[(df["tipo_contrato"] == "mes a mes")
                & (df["llamadas_soporte"] >= 3)]
    n = int(len(riesgo))
    tasa = float(riesgo["churn"].mean()) if n else 0.0
    se_irian = int(round(n * tasa))
    # ingreso mensual en riesgo de perderse en ese segmento
    ingreso_riesgo = float(riesgo.loc[riesgo["churn"] == 1, "cargo_mensual"].sum())
    # si una campaña retiene el 30% de los que se irían
    rescate_mensual = round(ingreso_riesgo * 0.30)
    tasa_global = round(float(df["churn"].mean()) * 100, 1)

    texto = (
        f"Churn global: {tasa_global}%. El segmento de mayor riesgo es "
        f"'mes a mes' con 3+ llamadas a soporte: {n} clientes y "
        f"{round(tasa * 100)}% de abandono (~{se_irian} se irían).\n"
        f"Recomendación: campaña proactiva a ese segmento (oferta de contrato "
        f"anual + atención prioritaria). Reteniendo solo el 30% de los que se "
        f"irían, se rescatan ~${rescate_mensual:,.0f} MXN/mes de ingreso "
        f"recurrente — mucho más barato que adquirir clientes nuevos."
    )
    return {
        "churn_global_pct": tasa_global,
        "segmento_riesgo_n": n,
        "segmento_riesgo_churn_pct": round(tasa * 100, 1),
        "rescate_mensual_mxn": rescate_mensual,
        "texto": texto,
    }
