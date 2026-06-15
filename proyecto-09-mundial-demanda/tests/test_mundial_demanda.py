"""Pruebas offline: generación de datos, consultas SQL y la recomendación."""

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mundial_demanda import analisis, consultas
from mundial_demanda.datos import FIN, INICIO, construir_db, generar

DIAS = (FIN - INICIO).days + 1


def _con(tmp_path):
    return sqlite3.connect(construir_db(str(tmp_path / "t.db")))


def test_generar_estructura():
    d = generar()
    assert set(d) == {"hoteles", "partidos", "ocupacion"}
    assert len(d["hoteles"]) == 30                       # 3 ciudades x 10 hoteles
    assert len(d["ocupacion"]) == len(d["hoteles"]) * DIAS
    assert all(0 <= fila[2] <= 100 for fila in d["ocupacion"])  # ocupación %


def test_determinista():
    assert generar()["ocupacion"] == generar()["ocupacion"]


def test_consultas_corren(tmp_path):
    con = _con(tmp_path)
    for sql in consultas.CONSULTAS.values():
        columnas, filas = consultas.correr(con, sql)
        assert columnas and filas
    con.close()


def test_dia_partido_tiene_mas_demanda(tmp_path):
    con = _con(tmp_path)
    _, filas = consultas.correr(con, consultas.PARTIDO_VS_NORMAL)
    por_tipo = {f[0]: f for f in filas}
    assert por_tipo["Día de partido"][1] > por_tipo["Día normal"][1]
    con.close()


def test_recomendacion(tmp_path):
    con = _con(tmp_path)
    rec = analisis.recomendacion(con)
    assert rec["subida_recomendada_pct"] > 0
    assert rec["ingreso_extra_mxn"] > 0
    assert "Recomendación" in rec["texto"]
    con.close()
