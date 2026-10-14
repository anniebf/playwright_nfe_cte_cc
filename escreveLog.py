from datetime import datetime

from config import LOG_DIR

data = datetime.now().isoformat(timespec="minutes").replace(":", "_")


def escreveLog(servico, mensagem):
    linha = (
        datetime.now().isoformat(timespec="minutes").replace(":", "_")
        + ": "
        + mensagem
    )
    with open(LOG_DIR / f"{servico}_log_execucao{data}.txt", "a", encoding="utf-8") as log:
        log.write(linha + "\n")
    print(linha, flush=True)
