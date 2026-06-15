"""Pruebas offline: datos, segmentos SQL, modelo, recomendación y figura."""

import os
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from churn import analisis, consultas, modelo, visual
from churn.datos import construir_db, generar


def test_generar():
    df = generar()
    assert len(df) == 2000
    assert set(df["churn"].unique()) <= {0, 1}
    assert 0 < df["churn"].mean() < 1          # hay churn, pero no todos


def test_determinista():
    assert generar().equals(generar())


def test_consultas(tmp_path):
    con = sqlite3.connect(construir_db(str(tmp_path / "c.db")))
    for sql in consultas.CONSULTAS.values():
        columnas, filas = consultas.correr(con, sql)
        assert columnas and filas
    con.close()


def test_modelo_auc():
    res = modelo.entrenar(generar())
    assert res["auc"] > 0.70                    # el modelo discrimina


def test_recomendacion():
    rec = analisis.recomendacion(generar())
    assert rec["segmento_riesgo_n"] > 0
    assert "Recomendación" in rec["texto"]


def test_visual(tmp_path):
    con = sqlite3.connect(construir_db(str(tmp_path / "c.db")))
    ruta = visual.fig_churn_por_contrato(con, str(tmp_path / "f.png"))
    assert os.path.exists(ruta)
    con.close()
