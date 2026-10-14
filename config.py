import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# Pastas locais (no Docker, monte volumes nelas)
DOWNLOADS_DIR = Path(os.getenv("DOWNLOADS_DIR", BASE_DIR / "downloads"))
XLS_DIR = DOWNLOADS_DIR / "xls"
CSV_DIR = DOWNLOADS_DIR / "csv"
PDF_DIR = DOWNLOADS_DIR / "pdf"
LOG_DIR = Path(os.getenv("LOG_DIR", BASE_DIR / "log"))

# Destinos finais (equivalentes a S:\Automacao\bot\FISCAL e \\xmlfiscal\...\Conta Corrente)
REDE_COMPARTILHAMENTO = r"\\xmlfiscal.bomfuturo.local\bfspedfiscal$"
DESTINO_FISCAL = Path(REDE_COMPARTILHAMENTO) / "SPED_rpa"
DESTINO_CC = DESTINO_FISCAL / "Conta Corrente"
PASTA_NFE = "Consulta_de_NF-e_EmitidaRecebida"
PASTA_CTE = "Consulta_de_CT-e_EmitidaRecebida"

# Credenciais do contabilista (equivalente ao params.json da rede)
PARAMS_JSON = Path(os.getenv("PARAMS_JSON", BASE_DIR / "params.json"))

HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)

URL_LOGIN = "https://www.sefaz.mt.gov.br/acesso/pages/login/login.xhtml"
URL_NFE = "https://www.sefaz.mt.gov.br/nfe/pages/consultaemitidasrecebidas/consultaemitidasrecebidas.xhtml"
URL_CTE = "https://www.sefaz.mt.gov.br/cte/portal/consultaremitidorecebido"
URL_CC = "https://www.sefaz.mt.gov.br/ccfiscal/lancamento/consulta"

# Datas
hoje = datetime.now()
dia = hoje.day
mes_atual = hoje.month
ano_atual = hoje.year

if mes_atual == 1:
    mes_anterior, ano_anterior = 12, ano_atual - 1
else:
    mes_anterior, ano_anterior = mes_atual - 1, ano_atual

for pasta in (XLS_DIR, CSV_DIR, PDF_DIR, LOG_DIR):
    pasta.mkdir(parents=True, exist_ok=True)
