import os

import pandas as pd

from config import ano_atual, CSV_DIR, mes_atual


def converter_excel_para_csv(caminho_xls, consulta, grupo, filial):
    nome_arquivo = f"{consulta}_GRUPO-{grupo}_FILIAL-{str(filial).strip()}_{mes_atual:02d}.{ano_atual}.csv"
    destino = CSV_DIR / nome_arquivo

    pd.read_excel(caminho_xls).to_csv(destino, index=False)
    df = pd.read_csv(destino, index_col=None)

    # Exclui as 5 primeiras linhas
    df = df.iloc[5:]
    df.to_csv(destino, header=False, index=False, sep=";")

    os.remove(caminho_xls)
    return nome_arquivo
