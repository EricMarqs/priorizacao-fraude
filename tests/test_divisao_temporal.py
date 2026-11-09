"""Testes da divisão temporal. Cada passo tem o seu grupo de testes."""

import sys
from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from divisao_temporal import calcular_cortes, dividir_por_tempo  # noqa: E402

ARQUIVO = RAIZ / "data" / "processed" / "treino.parquet"


# Passo 1: calcular_cortes


def test_passo1_separa_60_e_80_por_cento():
    tempos = pd.Series(range(1, 101))
    corte_treino, corte_validacao = calcular_cortes(tempos)
    assert (tempos <= corte_treino).sum() == 60
    assert (tempos <= corte_validacao).sum() == 80


def test_passo1_segundo_corte_acumula_as_fracoes():
    tempos = pd.Series(range(1, 101))
    corte_treino, corte_validacao = calcular_cortes(tempos, fracao_treino=0.5, fracao_validacao=0.25)
    assert (tempos <= corte_treino).sum() == 50
    assert (tempos <= corte_validacao).sum() == 75


def test_passo1_nao_depende_da_ordem_das_linhas():
    tempos = pd.Series(range(1, 101))
    embaralhados = tempos.sample(frac=1, random_state=0)
    assert calcular_cortes(embaralhados) == pytest.approx(calcular_cortes(tempos))


# Passo 2: dividir_por_tempo


@pytest.fixture
def tabela():
    return pd.DataFrame(
        {
            "TransactionDT": [1, 2, 3, 3, 4, 5, 6, 6],
            "TransactionAmt": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0],
        }
    )


def test_passo2_coloca_cada_linha_no_periodo_certo(tabela):
    treino, validacao, teste = dividir_por_tempo(tabela, 3, 5)
    assert treino["TransactionDT"].tolist() == [1, 2, 3, 3]
    assert validacao["TransactionDT"].tolist() == [4, 5]
    assert teste["TransactionDT"].tolist() == [6, 6]


def test_passo2_nao_perde_nem_repete_linhas(tabela):
    partes = dividir_por_tempo(tabela, 3, 5)
    assert sum(len(parte) for parte in partes) == len(tabela)
    juntas = pd.concat(partes)
    assert not juntas.index.duplicated().any()


def test_passo2_instantes_iguais_ficam_no_mesmo_periodo(tabela):
    treino, validacao, _ = dividir_por_tempo(tabela, 3, 5)
    assert not set(treino["TransactionDT"]) & set(validacao["TransactionDT"])
    assert (treino["TransactionDT"] == 3).sum() == 2


def test_passo2_mantem_as_outras_colunas(tabela):
    for parte in dividir_por_tempo(tabela, 3, 5):
        assert list(parte.columns) == list(tabela.columns)


# Passo 3: os dois passos juntos, na base real. Lê só TransactionDT.


@pytest.mark.skipif(not ARQUIVO.exists(), reason="base processada não encontrada")
def test_passo3_base_real_tem_os_tamanhos_da_d8():
    tempos = pd.read_parquet(ARQUIVO, columns=["TransactionDT"])
    corte_treino, corte_validacao = calcular_cortes(tempos["TransactionDT"])
    treino, validacao, teste = dividir_por_tempo(tempos, corte_treino, corte_validacao)
    assert (len(treino), len(validacao), len(teste)) == (354_324, 118_108, 118_108)
    assert treino["TransactionDT"].max() < validacao["TransactionDT"].min()
    assert validacao["TransactionDT"].max() < teste["TransactionDT"].min()
