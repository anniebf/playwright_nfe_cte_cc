from config import (
    ano_anterior,
    DESTINO_CC,
    DESTINO_FISCAL,
    mes_anterior,
    PASTA_CTE,
    PASTA_NFE,
    REDE_COMPARTILHAMENTO,
)
from RedeShare import conexao_rede


def criar_diretorio():
    pasta_mes = f"mes_{mes_anterior:02d}_{ano_anterior}"

    caminhos = [
        DESTINO_FISCAL / PASTA_CTE / pasta_mes,
        DESTINO_FISCAL / PASTA_NFE / pasta_mes,
        DESTINO_CC / pasta_mes,
    ]
    for caminho in caminhos:
        existia = caminho.exists()
        caminho.mkdir(parents=True, exist_ok=True)
        print(f"Pasta {'já existe' if existia else 'criada'}: {caminho}")

if __name__ == "__main__":
    with conexao_rede(REDE_COMPARTILHAMENTO):
        criar_diretorio()