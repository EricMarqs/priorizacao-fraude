"""Testes da métrica de valor capturado. Cada passo tem o seu grupo de testes."""

import sys
from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from metricas import quantidade_de_revisoes, selecionar_revisadas, valor_capturado  # noqa: E402


def test_quantidade_arredonda_para_cima():
    assert quantidade_de_revisoes(118_108, 0.03) == 3_544


def test_quantidade_nao_soma_uma_revisao_por_erro_de_ponto_flutuante():
    assert quantidade_de_revisoes(100, 0.07) == 7


# Passo 1: selecionar_revisadas


def test_passo1_escolhe_as_maiores_pontuacoes():
    pontuacoes = pd.Series([0.1, 0.9, 0.5, 0.7], index=["a", "b", "c", "d"])
    assert set(selecionar_revisadas(pontuacoes, 0.5)) == {"b", "d"}


def test_passo1_respeita_a_capacidade_arredondada_para_cima():
    pontuacoes = pd.Series(range(10))
    assert len(selecionar_revisadas(pontuacoes, 0.21)) == 3


def test_passo1_empate_fica_com_a_linha_que_aparece_primeiro():
    pontuacoes = pd.Series([5.0, 5.0, 5.0, 1.0])
    assert set(selecionar_revisadas(pontuacoes, 0.5)) == {0, 1}


# Passo 2: valor_capturado


@pytest.fixture
def exemplo():
    # O índice não começa em zero, como acontece na validação.
    indice = [1000, 1001, 1002, 1003]
    return {
        "rotulos": pd.Series([1, 0, 1, 1], index=indice),
        "pontuacoes": pd.Series([0.9, 0.8, 0.1, 0.7], index=indice),
        "valores": pd.Series([100.0, 999.0, 300.0, 100.0], index=indice),
    }


def test_passo2_conta_so_o_valor_das_fraudes_revisadas(exemplo):
    assert valor_capturado(**exemplo, capacidade=0.5) == pytest.approx(20.0)


def test_passo2_revisando_tudo_captura_100(exemplo):
    assert valor_capturado(**exemplo, capacidade=1.0) == pytest.approx(100.0)


def test_passo2_sem_fraude_revisada_captura_zero():
    indice = [7, 8, 9, 10]
    assert valor_capturado(
        rotulos=pd.Series([0, 1, 1, 1], index=indice),
        pontuacoes=pd.Series([0.9, 0.1, 0.2, 0.3], index=indice),
        valores=pd.Series([50.0, 10.0, 10.0, 10.0], index=indice),
        capacidade=0.25,
    ) == pytest.approx(0.0)
