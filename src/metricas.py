"""Métricas de negócio para capacidade limitada de revisão."""

import math

import pandas as pd


def quantidade_de_revisoes(total: int, capacidade: float) -> int:
    """Quantas transações cabem na capacidade, arredondando para cima."""
    # round evita que um erro mínimo de ponto flutuante acrescente uma revisão.
    return math.ceil(round(capacidade * total, 9))


def selecionar_revisadas(pontuacoes: pd.Series, capacidade: float) -> pd.Index:
    """Retorna o índice das transações com as maiores pontuações.

    Em caso de empate, ganha a linha que aparece primeiro.
    """
    quantidade = quantidade_de_revisoes(len(pontuacoes), capacidade)
    # Passo 1: escreva aqui a escolha das linhas e retorne o índice delas.
    return pontuacoes.nlargest(quantidade).index


def valor_capturado(
    rotulos: pd.Series,
    pontuacoes: pd.Series,
    valores: pd.Series,
    capacidade: float,
) -> float:
    """Retorna a porcentagem (0 a 100) do valor fraudado que foi revisado.

    rotulos: 1 para fraude e 0 para legítima.
    pontuacoes: quanto maior, mais prioridade na revisão.
    valores: valor de cada transação.
    As três séries têm o mesmo índice.
    """
    # Passo 2: escreva aqui o cálculo, usando selecionar_revisadas.
    seleionadas = selecionar_revisadas(pontuacoes, capacidade)
    valor_total_fraude = valores[rotulos == 1].sum()
    valor_revisado_fraude = valores[seleionadas][rotulos[seleionadas] == 1].sum()
    return (valor_revisado_fraude / valor_total_fraude) * 100  

