"""Agregações por cartão usando somente informação anterior a cada transação."""

import numpy as np
import pandas as pd

JANELAS_PADRAO = (("1d", 86_400), ("7d", 604_800))


def chave_de_cartao(tabela: pd.DataFrame, colunas: list[str]) -> pd.Series:
    """Numera cada combinação de valores das colunas. Vazio conta como um valor."""
    return tabela.groupby(colunas, dropna=False, observed=True, sort=False).ngroup()


def agregacoes_anteriores(
    tempos: pd.Series,
    valores: pd.Series,
    chave: pd.Series,
    janelas: tuple[tuple[str, int], ...] = JANELAS_PADRAO,
) -> pd.DataFrame:
    """Calcula, para cada transação, o histórico da mesma chave antes dela.

    Transações no mesmo instante não contam como anteriores. isFraud não é
    usado de propósito: o rótulo só é conhecido depois do chargeback.
    """
    t = tempos.to_numpy(dtype="int64")
    v = valores.to_numpy(dtype="float64")
    k = chave.to_numpy(dtype="int64")
    n = len(t)

    qtd_anteriores = np.zeros(n, dtype="int64")
    qtd_janelas = {nome: np.zeros(n, dtype="int64") for nome, _ in janelas}
    media_anterior = np.full(n, np.nan)
    segundos_desde_anterior = np.full(n, np.nan)

    # Ordena por chave e tempo para tratar cada chave como um bloco contínuo.
    ordem = np.lexsort((t, k))
    limites = np.flatnonzero(np.diff(k[ordem])) + 1
    for inicio, fim in zip(np.r_[0, limites], np.r_[limites, n]):
        posicoes = ordem[inicio:fim]
        t_chave = t[posicoes]
        # side="left" conta só tempos estritamente menores, o que exclui empates.
        anteriores = np.searchsorted(t_chave, t_chave, side="left")
        soma_acumulada = np.r_[0.0, np.cumsum(v[posicoes])]

        qtd_anteriores[posicoes] = anteriores
        for nome, segundos in janelas:
            inicio_janela = np.searchsorted(t_chave, t_chave - segundos, side="left")
            qtd_janelas[nome][posicoes] = anteriores - inicio_janela

        tem_historico = anteriores > 0
        media_anterior[posicoes[tem_historico]] = (
            soma_acumulada[anteriores[tem_historico]] / anteriores[tem_historico]
        )
        segundos_desde_anterior[posicoes[tem_historico]] = (
            t_chave[tem_historico] - t_chave[anteriores[tem_historico] - 1]
        )

    saida = {"qtd_anteriores": qtd_anteriores}
    saida.update({f"qtd_{nome}": valores_janela for nome, valores_janela in qtd_janelas.items()})
    saida["media_anterior"] = media_anterior
    saida["razao_valor"] = v / media_anterior
    saida["segundos_desde_anterior"] = segundos_desde_anterior
    return pd.DataFrame(saida, index=tempos.index)
