"""Treino do LightGBM com parada definida pelo fim do próprio treino (D14)."""

import lightgbm as lgb
import pandas as pd

from divisao_temporal import calcular_cortes, dividir_por_tempo

PARAMETROS = {
    "objective": "binary",
    "metric": "average_precision",
    "learning_rate": 0.05,
    "num_leaves": 63,
    "min_child_samples": 100,
    "feature_fraction": 0.8,
    "bagging_fraction": 0.8,
    "bagging_freq": 1,
    "seed": 42,
    "deterministic": True,
    "force_row_wise": True,
    "num_threads": 4,
    "verbose": -1,
}


def treinar_lightgbm(
    treino: pd.DataFrame,
    colunas: list[str],
    parametros: dict = PARAMETROS,
    coluna_tempo: str = "TransactionDT",
    coluna_alvo: str = "isFraud",
) -> tuple[lgb.Booster, int]:
    """Escolhe o número de árvores nos últimos 20% do treino e retreina no treino inteiro."""
    corte_parada, _ = calcular_cortes(treino[coluna_tempo], fracao_treino=0.8, fracao_validacao=0.2)
    ajuste, parada, _ = dividir_por_tempo(treino, corte_parada, treino[coluna_tempo].max(), coluna_tempo)
    busca = lgb.train(
        parametros,
        lgb.Dataset(ajuste[colunas], ajuste[coluna_alvo]),
        num_boost_round=5000,
        valid_sets=[lgb.Dataset(parada[colunas], parada[coluna_alvo])],
        callbacks=[lgb.early_stopping(100, verbose=False)],
    )
    final = lgb.train(
        parametros, lgb.Dataset(treino[colunas], treino[coluna_alvo]), num_boost_round=busca.best_iteration
    )
    return final, busca.best_iteration
