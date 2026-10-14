from playwright.sync_api import TimeoutError as PlaywrightTimeout

from anticaptcha import anticaptchaTurnstile
from config import URL_LOGIN
from escreveLog import escreveLog
from util import credenciais, visivel

JS_TOKEN = """token => {
    const cf = document.querySelector('input[name="cf-turnstile-response"]');
    if (cf) {
        cf.value = token;
        cf.dispatchEvent(new Event('input', { bubbles: true }));
        cf.dispatchEvent(new Event('change', { bubbles: true }));
    }
}"""


def _resolver_captcha(page, automacao, servico_log=None):
    servico_log = servico_log or automacao
    for tentativa in range(3):
        try:
            page.context.clear_cookies()
            page.reload()
            print(f"Tentativa {tentativa + 1} de 3...")

            page.wait_for_selector("#captcha-container", timeout=20000)

            token = anticaptchaTurnstile(automacao)
            if not token:
                raise Exception("Falha ao obter token do AntiCaptcha")

            page.evaluate(JS_TOKEN, token)
            page.wait_for_timeout(4000)
            page.click("#captcha-container")

            status = visivel(page, "#status", 5000)
            if status:
                classes = (status.get_attribute("class") or "").split()
                texto = status.inner_text().strip()
                if "error" in classes or texto == "Não foi possível confirmar. Recarregue a página para tentar novamente.":
                    escreveLog(servico_log, "Captcha inválido, tentando novamente...")
                    page.reload()
                    continue
            else:
                page.reload()

            escreveLog(servico_log, "Captcha resolvido com sucesso!")
            return
        except Exception as e:
            print(f"Erro na tentativa {tentativa + 1}: {e}")
            escreveLog(servico_log, f"Erro na tentativa {tentativa + 1} do captcha: {e}")
            if tentativa == 2:
                escreveLog(servico_log, "Número máximo de tentativas do captcha atingido.")


def login_e_captcha(page, automacao, servico_log=None):
    """Abre a página de login, resolve o captcha e entra como contabilista."""
    usuario, senha = credenciais()
    servico_log = servico_log or automacao
    try:
        page.goto(URL_LOGIN)
        _resolver_captcha(page, automacao, servico_log)

        escreveLog(servico_log, "Iniciando login.")
        try:
            page.click('[id="formLogin:selectTipoUsuario_label"]')
        except PlaywrightTimeout as e:
            page.screenshot(path="tela.png")
            escreveLog(servico_log, f"Erro ao selecionar tipo de usuário: {e}")
            return False

        page.click('[id="formLogin:selectTipoUsuario_1"]')
        page.wait_for_timeout(2000)

        login_ok = False
        for x in range(5):
            try:
                escreveLog(servico_log, f"Iniciando tentativa {x + 1} do login.")
                page.fill('[id="formLogin:inputLogin"]', usuario)
                page.fill('[id="formLogin:inputSenha"]', senha)
                page.wait_for_timeout(2000)
                page.click("xpath=//button[contains(., 'Efetuar Login')]")
                escreveLog(servico_log, "Credenciais enviadas.")

                # erro de login: tenta novamente
                if visivel(page, ".ui-messages-error", 10000):
                    continue

                # sessão duplicada: substitui e acessa
                if visivel(page, "xpath=//*[contains(@id, 'superPanelMensagem')]", 10000):
                    page.fill("input[type='password'].ui-password", senha)
                    page.click("input.btnPadrao[value='Substituir']")
                    login_ok = True
                    break

                if visivel(page, "#tst", 10000):
                    login_ok = True
                    break
            except Exception as e:
                escreveLog(servico_log, f"Erro na tentativa {x + 1} do login: {e}")

        if not login_ok:
            escreveLog(servico_log, "Login não confirmado após 5 tentativas.")
            return False

        escreveLog(servico_log, "Login efetuado com sucesso!")
        return True
    except Exception as e:
        escreveLog(servico_log, f"Erro ao efetuar login: {e}")
        return False
