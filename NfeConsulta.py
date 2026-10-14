import os
import shutil

import DatasMes
import database
import ModificaCsv
from config import (
    ano_anterior,
    DESTINO_FISCAL,
    CSV_DIR,
    mes_anterior,
    PASTA_NFE,
    URL_NFE,
    XLS_DIR,
)
from escreveLog import escreveLog
from FuncLogin import login_e_captcha
from util import sessao, visivel

TAMANHO_MINIMO = 20.48
TENTATIVAS = 3


def mainNfe():
    escreveLog("NFE", "INICIANDO...")
    data_inicio, data_fim = DatasMes.gerar_intervalo_datas()
    lista_filiais = database.retornoCnpj()

    try:
        with sessao() as context:
            page = context.new_page()
            login_e_captcha(page, "RPA - NFE")
            loopNfe(context, lista_filiais, data_inicio, data_fim)
        escreveLog("NFE", "...FINALIZANDO")
    except Exception as e:
        escreveLog("NFE", f"...FINALIZANDO COM ERRO: {e}")


def loopNfe(context, lista_filiais, data_inicio, data_fim):
    destino = DESTINO_FISCAL / PASTA_NFE / f"mes_{mes_anterior:02d}_{ano_anterior}"
    destino.mkdir(parents=True, exist_ok=True)

    for grupo, _filial, cnpj, codigo_filial in lista_filiais:
        escreveLog("NFE", f"Cnpj: {cnpj} atualmente sendo executado...")

        for _ in range(TENTATIVAS):
            page = context.new_page()
            try:
                page.goto(URL_NFE)
                dadosConsulta(page, cnpj, data_inicio, data_fim)

                if visivel(page, "xpath=//div[contains(@class, 'ui-dialog-content') and contains(text(), 'Contabilista não representa')]", 5000):
                    escreveLog("NFE", f"Ocorreu um erro no CNPJ: {cnpj} Contabilista nao representa")
                    break

                if visivel(page, "xpath=//div[contains(text(),'Documento deve ser informado')]", 5000):
                    escreveLog("NFE", f"Erro no CNPJ: {cnpj} ao preencher o CNPJ no site")
                    continue

                if visivel(page, "xpath=//div[contains(text(),'Data inválida')]", 5000):
                    escreveLog("NFE", f"Erro no CNPJ: {cnpj} ao preencher as datas no site")
                    continue

                exportar = visivel(page, "xpath=//a[text()='Exportar para Excel']", 10000)
                if not exportar:
                    escreveLog("NFE", "Botao de exportar nao encontrado")
                    break
                escreveLog("NFE", "Dados da Consultado corretos")

                escreveLog("NFE", "Baixando arquivo xls")
                with page.expect_download(timeout=60000) as download_info:
                    exportar.click()
                caminho_xls = XLS_DIR / download_info.value.suggested_filename
                download_info.value.save_as(caminho_xls)

                nome = ModificaCsv.converter_excel_para_csv(caminho_xls, "NFE", grupo, codigo_filial)
                caminho_csv = CSV_DIR / nome

                if not os.path.isfile(caminho_csv):
                    escreveLog("NFE", "Arquivo NAO existe no diretorio")
                    break
                escreveLog("NFE", "Arquivo baixado com sucesso!")

                if os.path.getsize(caminho_csv) > TAMANHO_MINIMO:
                    escreveLog("NFE", "Arquivo NAO esta corrompido")
                    shutil.copy(caminho_csv, destino / nome)
                    escreveLog("NFE", f"Arquivo: {nome} copiado para: {destino}")
                    existe = os.path.isfile(destino / nome)
                    escreveLog("NFE", f"Arquivo {'EXISTE' if existe else 'NAO EXISTE'} no diretorio: {destino / nome}")
                    escreveLog("NFE", f"O cpnj: {cnpj} foi executado com SUCESSO!")
                else:
                    escreveLog("NFE", "Arquivo ESTA corrompido")
                break
            except Exception as e:
                escreveLog("NFE", f"ERRO: {e}")
                break
            finally:
                page.close()


def dadosConsulta(page, cnpj, data_inicio, data_fim):
    page.click('xpath=//*[@id="j_idt14:sorEmissorDest"]/tbody/tr/td[2]/div/div[2]/span')
    page.click("xpath=//label[text()='Inscrição Estadual']")
    page.click("xpath=//li[text()='CNPJ']")
    page.wait_for_timeout(2000)

    campo_cnpj = page.locator(
        "xpath=//div[@class='ui-panel-content ui-widget-content']//input[contains(@class, 'ui-inputmask')]"
    ).first
    campo_cnpj.wait_for(state="visible")
    page.wait_for_timeout(5000)
    campo_cnpj.click()
    campo_cnpj.press_sequentially(cnpj)
    page.wait_for_timeout(3000)

    campo_inicio = page.locator("xpath=(//input[contains(@class, 'hasDatepicker')])[1]")
    campo_inicio.click()
    campo_inicio.press_sequentially(data_inicio)
    escreveLog("NFE", f"Dados da consulta --- Data inicio: {data_inicio}")

    campo_fim = page.locator("xpath=(//input[contains(@class, 'hasDatepicker')])[2]")
    campo_fim.click()
    page.wait_for_timeout(2000)
    campo_fim.press_sequentially(data_fim)
    escreveLog("NFE", f"Dados da consulta --- Data final: {data_fim}")

    page.wait_for_timeout(2000)
    page.click("xpath=//button[.//span[text()='Consultar']]")


if __name__ == "__main__":
    mainNfe()
