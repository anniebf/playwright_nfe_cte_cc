import os
import shutil

import DatasMes
import database
from config import ano_anterior, dia, DESTINO_CC, mes_anterior, PDF_DIR, URL_CC
from escreveLog import escreveLog
from FuncLogin import login_e_captcha
from util import sessao, visivel


def mainCC():
    escreveLog("CC", "INICIANDO...")
    try:
        mes_passado, ano_passado = DatasMes.dataContaCorrente()
        lista_insc = database.retornoInscEstd()
        escreveLog("CC", f"Competência da consulta: {mes_passado:02d}/{ano_passado}")

        with sessao() as context:
            page = context.new_page()
            if not login_e_captcha(page, "RPA - CC ", servico_log="CC"):
                raise RuntimeError("Não foi possível efetuar o login.")
            concluidas, falhas = loopCC(
                context, lista_insc, mes_passado, ano_passado
            )
        escreveLog(
            "CC",
            f"FINALIZANDO: {concluidas} consulta(s) concluída(s), {falhas} falha(s).",
        )
    except Exception as e:
        escreveLog("CC", f"FINALIZANDO COM ERRO: {e}")


def loopCC(context, lista_insc, mes_passado, ano_passado):
    concluidas = 0
    falhas = 0

    for insc in lista_insc:
        inscricao = insc[0].strip()
        escreveLog("CC", f"Iniciando consulta da inscrição estadual {inscricao}.")
        page = None
        try:
            page = context.new_page()
            page.goto(URL_CC)
            if dadosInscEstd(page, insc, mes_passado, ano_passado):
                concluidas += 1
                escreveLog("CC", f"Consulta da inscrição estadual {inscricao} concluída.")
            else:
                falhas += 1
                escreveLog("CC", f"Consulta da inscrição estadual {inscricao} não concluída.")
        except Exception as e:
            falhas += 1
            escreveLog("CC", f"Erro na inscrição estadual {inscricao}: {e}")
        finally:
            if page is not None:
                page.close()

    return concluidas, falhas


def dadosInscEstd(page, insc, mes_passado, ano_passado):
    inscricao = insc[0].strip()
    cod_filial = insc[2]
    grupo = insc[3]

    page.fill("[name='numeroPessoaContribuinte']", inscricao, timeout=30000)
    page.select_option("[name='mesInicio']", value=str(mes_passado))
    page.select_option("[name='anoInicio']", value=str(ano_passado))
    page.click("[name='bttnPesquisar']")
    page.wait_for_timeout(5000)

    erro = visivel(page, "xpath=//*[contains(text(), 'Erro inesperado')]", 5000)
    if erro:
        escreveLog("CC", f"ERRO: {erro.inner_text()}")
        return False

    page.click("[name='botaoConfirmar']")
    page.wait_for_timeout(5000)

    prefixo = "CONTA_CORRENTE" if dia < 22 else "CONTA_CORRENTE_APOS_SPED"
    nome = f"{prefixo}_{mes_anterior}.{ano_anterior}_EMP_{grupo}_FILIAL_{cod_filial}.pdf"
    caminho_pdf = PDF_DIR / nome

    escreveLog("CC", f"Gerando PDF: {nome}")
    page.pdf(path=str(caminho_pdf), print_background=True, landscape=True, scale=0.4)

    if os.path.exists(caminho_pdf):
        destino = DESTINO_CC / f"mes_{mes_anterior:02d}_{ano_anterior}"
        destino.mkdir(parents=True, exist_ok=True)
        shutil.copy(caminho_pdf, destino / nome)
        escreveLog("CC", f"PDF copiado para {destino / nome}")
        return True

    escreveLog("CC", f"ERRO: PDF não foi encontrado após a geração: {caminho_pdf}")
    return False


if __name__ == "__main__":
    mainCC()
