import os
import threading
import time

import contaCorrente
import CriaPastas
import CteConsulta
import NfeConsulta
from config import dia, REDE_COMPARTILHAMENTO
from RedeShare import conexao_rede

# Até este dia (inclusive) roda NF-e, CT-e e Conta Corrente; depois, só Conta Corrente
DIA_LIMITE = int(os.getenv("DIA_LIMITE", "13"))
ATRASO_SEGUNDOS = int(os.getenv("ATRASO_MINUTOS", "5")) * 60


def main():
    CriaPastas.criar_diretorio()
    print("Pastas criadas com sucesso.")

    if dia > DIA_LIMITE:
        print(f"Dia {dia} > {DIA_LIMITE}: executando somente Conta Corrente.")
        contaCorrente.mainCC()
        return "Processo concluído com sucesso!"

    print(f"Dia {dia} <= {DIA_LIMITE}: executando NF-e, CT-e e Conta Corrente.")

    nfe = threading.Thread(target=NfeConsulta.mainNfe, name="NFeConsultaThread")
    nfe.start()

    time.sleep(ATRASO_SEGUNDOS)
    cte = threading.Thread(target=CteConsulta.mainCte, name="CteConsultaThread")
    cte.start()

    time.sleep(ATRASO_SEGUNDOS)
    cc = threading.Thread(target=contaCorrente.mainCC, name="ContaCorrenteThread")
    cc.start()

    for t in (nfe, cte, cc):
        t.join()
        print(f"{t.name} concluída.")

    return "Processo concluído com sucesso!"


if __name__ == "__main__":
    with conexao_rede(REDE_COMPARTILHAMENTO):
        print(main())
