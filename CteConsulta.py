import os
import shutil

from CriaPastas import criar_diretorio
import DatasMes
import database
import ModificaCsv
from config import (
    REDE_COMPARTILHAMENTO,
    ano_anterior,
    CSV_DIR,
    DESTINO_FISCAL,
    mes_anterior,
    PASTA_CTE,
    URL_CTE,
    XLS_DIR,
)
from escreveLog import escreveLog
from FuncLogin import login_e_captcha
from util import sessao, visivel
from RedeShare import conexao_rede
TAMANHO_MINIMO = 20.48


def mainCte():
    escreveLog("CTE", "INICIANDO...")
    data_inicio, data_fim = DatasMes.gerar_intervalo_datas()
    lista_filiais = database.retornoCnpj()

    try:
        with sessao() as context:
            page = context.new_page()
            login_e_captcha(page, "RPA - CTE")
            loopCTE(context, lista_filiais, data_inicio, data_fim)
        escreveLog("CTE", "FINALIZANDO...")
    except Exception as e:
        escreveLog("CTE", f"FINALIZANDO COM ERRO: {e}")


def loopCTE(context, lista_filiais, data_inicio, data_fim):
    destino = DESTINO_FISCAL / PASTA_CTE / f"mes_{mes_anterior:02d}_{ano_anterior}"
    destino.mkdir(parents=True, exist_ok=True)
    escreveLog("CTE", f"Pasta de destino: {destino}")

    for grupo, _filial, cnpj, codigo_filial in lista_filiais:
        escreveLog("CTE", f"Cnpj: {cnpj} atualmente sendo executado...")
        page = context.new_page()
        try:
            page.goto(URL_CTE)
            escreveLog("CTE", "--Prenchimento dos dados do cte")

            page.select_option("#tipoConsulta", index=3)
            escreveLog("CTE", "Inscrição Estadual selecionada")
            page.wait_for_timeout(2000)

            page.select_option("#idenTomador", value="2")
            page.wait_for_timeout(3000)

            campo_cnpj = page.locator("#campoCnpjTomador")
            campo_cnpj.click()
            campo_cnpj.press_sequentially(cnpj)
            escreveLog("CTE", "CNPJ preenchido")
            page.wait_for_timeout(2000)

            inicio = page.locator('xpath=//*[@id="tabelaFiltro"]/table/tbody/tr[1]/td[2]/input[1]')
            inicio.click()
            inicio.press_sequentially(data_inicio)

            fim = page.locator('xpath=//*[@id="tabelaFiltro"]/table/tbody/tr[1]/td[2]/input[2]')
            fim.click()
            page.wait_for_timeout(2000)
            fim.press_sequentially(data_fim)
            escreveLog("CTE", "Datas preenchidas")

            page.wait_for_timeout(2000)
            page.click("#btnConsultar")
            page.wait_for_timeout(5000)

            sem_registro = visivel(page, "xpath=/html/body/center/form/table[2]/tbody/tr/td", 10000)
            if sem_registro and sem_registro.inner_text() == "Não foram encontrados registros para a consulta solicitada.":
                escreveLog("CTE", "Não foram encontrados registros para a consulta solicitada.")
                continue

            erro = visivel(page, "xpath=/html/body/center/table[3]/tbody/tr/td/ul/li", 10000)
            if erro:
                texto = erro.inner_text()
                if texto in (
                    "Acesso não permitido. Problemas com o banco de dados (null)",
                    "Não foi possível encontrar o contribuinte pelo seu documento de identificação representado pelo contabilista.",
                ):
                    escreveLog("CTE", texto)
                    continue
            else:
                escreveLog("CTE", "Dados inserido com sucesso")

            exportar = visivel(page, "#btnGerarExcelConsulta", 10000)
            if not exportar:
                escreveLog("CTE", "Nennhum arquivo encontrado para realizar o download")
                continue

            escreveLog("CTE", "Baixando arquivo xls")
            with page.expect_download(timeout=60000) as download_info:
                exportar.click()
            caminho_xls = XLS_DIR / download_info.value.suggested_filename
            download_info.value.save_as(caminho_xls)
            escreveLog("CTE", "Arquivo baixado com sucesso!")

            nome = ModificaCsv.converter_excel_para_csv(caminho_xls, "CTE", grupo, codigo_filial)
            caminho_csv = CSV_DIR / nome

            if not os.path.isfile(caminho_csv):
                escreveLog("CTE", "Arquivo NAO existe no diretorio")
            elif os.path.getsize(caminho_csv) > TAMANHO_MINIMO:
                escreveLog("CTE", "Arquivo NAO esta corrompido")
                with conexao_rede(REDE_COMPARTILHAMENTO):
       
                        shutil.copy(caminho_csv, destino / nome)
                escreveLog("CTE", f"Arquivo: {nome} copiado para: {destino}")
            else:
                escreveLog("CTE", "Arquivo ESTA corrompido")
        except Exception as e:
            escreveLog("CTE", f"ERRO: {e}")
        finally:
            page.close()


if __name__ == "__main__":
    mainCte()
