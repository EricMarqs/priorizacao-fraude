"""Testes das agregações: o foco é garantir que só o passado seja usado."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from variaveis import agregacoes_anteriores, chave_de_cartao  # noqa: E402

DIA = 86_400


def calcular(tempos, valores, chave, indice=None):
    indice = range(len(tempos)) if indice is None else indice
    return agregacoes_anteriores(
        pd.Series(tempos, index=indice), pd.Series(valores, index=indice, dtype="float64"), pd.Series(chave, index=indice)
    )


def test_primeira_transacao_nao_tem_historico():
    r = calcular([10, 20], [5, 7], [1, 1])
    assert r.loc[0, "qtd_anteriores"] == 0
    assert np.isnan(r.loc[0, "media_anterior"])
    assert np.isnan(r.loc[0, "segundos_desde_anterior"])


def test_conta_media_razao_e_tempo_desde_a_anterior():
    r = calcular([10, 20, 50], [10, 30, 40], [1, 1, 1])
    assert r["qtd_anteriores"].tolist() == [0, 1, 2]
    assert r.loc[2, "media_anterior"] == pytest.approx(20.0)
    assert r.loc[2, "razao_valor"] == pytest.approx(2.0)
    assert r.loc[2, "segundos_desde_anterior"] == 30


def test_mesmo_instante_nao_conta_como_anterior():
    r = calcular([10, 20, 20, 30], [1, 2, 3, 4], [1, 1, 1, 1])
    assert r["qtd_anteriores"].tolist() == [0, 1, 1, 3]
    assert r.loc[2, "media_anterior"] == pytest.approx(1.0)
    assert r.loc[2, "segundos_desde_anterior"] == 10


def test_chaves_nao_se_misturam():
    r = calcular([10, 20, 30], [1, 2, 3], [1, 2, 1])
    assert r["qtd_anteriores"].tolist() == [0, 0, 1]


def test_janela_de_um_dia():
    r = calcular([0, DIA, DIA + 1, 3 * DIA], [1, 1, 1, 1], [1, 1, 1, 1])
    # [t - 1 dia, t): quem está exatamente a 1 dia ainda conta.
    assert r["qtd_1d"].tolist() == [0, 1, 1, 0]


def test_alterar_o_futuro_nao_muda_o_passado():
    tempos = [10, 20, 30, 40, 50]
    original = calcular(tempos, [1, 2, 3, 4, 5], [1, 1, 1, 1, 1])
    alterado = calcular(tempos, [1, 2, 3, 400, 500], [1, 1, 1, 1, 1])
    # As linhas 3 e 4 mudaram de valor. As anteriores não podem mudar em nada.
    pd.testing.assert_frame_equal(original.iloc[:3], alterado.iloc[:3])
    assert original.loc[3, "media_anterior"] == alterado.loc[3, "media_anterior"]


def test_valor_da_propria_transacao_nao_entra_na_media():
    a = calcular([10, 20], [100, 1], [1, 1])
    b = calcular([10, 20], [100, 9999], [1, 1])
    assert a.loc[1, "media_anterior"] == b.loc[1, "media_anterior"] == pytest.approx(100.0)


def test_mantem_o_alinhamento_com_linhas_fora_de_ordem():
    r = calcular([30, 10, 20], [3, 1, 2], [1, 1, 1], indice=[100, 200, 300])
    assert r.loc[100, "qtd_anteriores"] == 2
    assert r.loc[200, "qtd_anteriores"] == 0
    assert r.loc[300, "qtd_anteriores"] == 1


def test_chave_de_cartao_trata_vazio_como_um_valor():
    tabela = pd.DataFrame({"a": [1, 1, 1, 2], "b": [5.0, np.nan, np.nan, 5.0]})
    chave = chave_de_cartao(tabela, ["a", "b"])
    assert chave.iloc[1] == chave.iloc[2]
    assert chave.nunique() == 3
    assert chave.notna().all() and (chave >= 0).all()
