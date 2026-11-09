"""Divisão temporal da base em treino, validação e teste (decisão D8)."""

import pandas as pd


def calcular_cortes(
    tempos: pd.Series,
    fracao_treino: float = 0.6,
    fracao_validacao: float = 0.2,
) -> tuple[float, float]:
    """Retorna os dois instantes que separam treino, validação e teste.

    Até corte_treino, inclusive, a transação é de treino.
    Depois de corte_treino e até corte_validacao, inclusive, é de validação.
    Depois de corte_validacao, é de teste.
    """
    # Passo 1: escreva aqui o cálculo dos dois cortes e retorne os dois.
    corte_treino = tempos.quantile(fracao_treino)
    corte_validacao = tempos.quantile(fracao_validacao + fracao_treino)
    return corte_treino, corte_validacao


def dividir_por_tempo(
    tabela: pd.DataFrame,
    corte_treino: float,
    corte_validacao: float,
    coluna_tempo: str = "TransactionDT",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Retorna as linhas de treino, validação e teste, nessa ordem."""
    # Passo 2: escreva aqui a separação das linhas usando os dois cortes.
    treino = tabela[tabela[coluna_tempo] <= corte_treino]
    validacao = tabela[(tabela[coluna_tempo] > corte_treino) & (tabela[coluna_tempo] <= corte_validacao)]
    teste = tabela[tabela[coluna_tempo] > corte_validacao]
    return treino, validacao, teste         

