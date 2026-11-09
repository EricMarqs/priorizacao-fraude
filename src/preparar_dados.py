"""Une as tabelas de treino do IEEE-CIS e salva em parquet, com tipos reduzidos.

Entrada:  data/raw/train_transaction.csv, data/raw/train_identity.csv (somente leitura)
Saída:    data/processed/treino.parquet
"""

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
RAW = RAIZ / "data" / "raw"
PROCESSED = RAIZ / "data" / "processed"


def reduzir_tipos(df: pd.DataFrame) -> pd.DataFrame:
    """Diminui o tamanho das colunas sem alterar os valores."""
    for col in df.select_dtypes("float64").columns:
        df[col] = pd.to_numeric(df[col], downcast="float")
    for col in df.select_dtypes("int64").columns:
        df[col] = pd.to_numeric(df[col], downcast="integer")
    for col in df.select_dtypes(include=["object", "str"]).columns:
        if df[col].nunique() < 0.5 * len(df):
            df[col] = df[col].astype("category")
    return df


def main() -> None:
    transacoes = reduzir_tipos(pd.read_csv(RAW / "train_transaction.csv"))
    identidade = reduzir_tipos(pd.read_csv(RAW / "train_identity.csv"))

    print(f"transaction: {transacoes.shape[0]} linhas, {transacoes.shape[1]} colunas")
    print(f"identity:    {identidade.shape[0]} linhas, {identidade.shape[1]} colunas")

    treino = transacoes.merge(identidade, on="TransactionID", how="left")
    print(f"juntado:     {treino.shape[0]} linhas, {treino.shape[1]} colunas")

    if treino.shape[0] != transacoes.shape[0]:
        raise ValueError("A junção mudou o número de linhas da tabela de transações.")

    PROCESSED.mkdir(parents=True, exist_ok=True)
    treino.to_parquet(PROCESSED / "treino.parquet", index=False)
    print(f"salvo em {PROCESSED / 'treino.parquet'}")


if __name__ == "__main__":
    main()
