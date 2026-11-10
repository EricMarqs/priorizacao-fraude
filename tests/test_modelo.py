import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from modelo import PARAMETROS, treinar_lightgbm


def _tabela(n=2000, semente=0):
    gerador = np.random.default_rng(semente)
    x = gerador.normal(size=n)
    return pd.DataFrame(
        {
            "TransactionDT": np.arange(n),
            "x": x,
            "isFraud": (x + gerador.normal(scale=0.5, size=n) > 1.5).astype("int8"),
        }
    )


def test_retorna_modelo_e_numero_de_arvores():
    parametros = {**PARAMETROS, "min_child_samples": 20, "num_threads": 1}
    modelo, arvores = treinar_lightgbm(_tabela(), ["x"], parametros)
    assert arvores >= 1
    assert modelo.num_trees() == arvores


def test_modelo_final_e_reproduzivel():
    parametros = {**PARAMETROS, "min_child_samples": 20, "num_threads": 1}
    tabela = _tabela()
    a, _ = treinar_lightgbm(tabela, ["x"], parametros)
    b, _ = treinar_lightgbm(tabela, ["x"], parametros)
    assert np.allclose(a.predict(tabela[["x"]]), b.predict(tabela[["x"]]))
