import json
from contextlib import contextmanager

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

from config import HEADLESS, PARAMS_JSON, USER_AGENT


def credenciais():
    with open(PARAMS_JSON, "r", encoding="utf-8") as f:
        dados = json.load(f)
    return dados["contabilista"], dados["senha_contabilista"]


@contextmanager
def sessao():
    """Abre um navegador Chromium isolado (uma sessão por automação/thread)."""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            args=["--no-sandbox", "--mute-audio", "--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(user_agent=USER_AGENT, accept_downloads=True)
        context.set_default_timeout(10000)
        try:
            yield context
        finally:
            browser.close()


def visivel(page, seletor, timeout=10000):
    """Retorna o locator se ficar visível dentro do timeout, senão None."""
    loc = page.locator(seletor).first
    try:
        loc.wait_for(state="visible", timeout=timeout)
        return loc
    except PlaywrightTimeout:
        return None
