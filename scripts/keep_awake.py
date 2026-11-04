"""Mantém os dashboards publicados acordados.

O Streamlit Community Cloud hiberna apps sem tráfego e mostra uma página
"This app has gone to sleep" com um botão para acordar. Um simples `curl`
não acorda o app (ele roda via WebSocket depois que a página carrega), então
este script abre cada URL num navegador headless (Playwright), clica no botão
de acordar se ele aparecer e espera o app terminar de carregar.

Uso: python scripts/keep_awake.py
Sai com código 1 se algum app não carregar, para o workflow ficar vermelho.
"""

import sys

from playwright.sync_api import TimeoutError as PWTimeout
from playwright.sync_api import sync_playwright

APPS = {
    "Streamlit Community Cloud": {
        "url": "https://vigilancia-genomica-app-vvnutarygmjpgvncuxkvrw.streamlit.app",
        # texto que só aparece depois que o app carregou de verdade
        "ready_text": "Vigilância Epidemiológica",
    },
    "Posit Connect Cloud": {
        "url": "https://connect.posit.cloud/bestaceleste/content/019fb8f5-6865-c13d-1c62-a77447b59fe9",
        "ready_text": None,  # só garante que a página abriu e o app foi requisitado
    },
}

WAKE_BUTTON = "text=/get this app back up/i"


def visit(page, name, url, ready_text):
    print(f"[{name}] abrindo {url}")
    page.goto(url, wait_until="domcontentloaded", timeout=60_000)

    # A página do Streamlit é um shell; o conteúdo pode estar dentro de um iframe.
    try:
        page.wait_for_timeout(5_000)
        for frame in page.frames:
            button = frame.locator(WAKE_BUTTON)
            if button.count() > 0:
                print(f"[{name}] app hibernando -> clicando em acordar")
                button.first.click()
                break
    except PWTimeout:
        pass

    if ready_text is None:
        page.wait_for_timeout(20_000)
        print(f"[{name}] ok (página carregada)")
        return True

    # O boot depois de hibernar pode levar 1-3 minutos.
    deadline_ms = 240_000
    step_ms = 10_000
    waited = 0
    while waited < deadline_ms:
        for frame in page.frames:
            try:
                if frame.get_by_text(ready_text, exact=False).count() > 0:
                    print(f"[{name}] ok (app carregado em ~{waited // 1000}s)")
                    return True
            except Exception:
                continue
        page.wait_for_timeout(step_ms)
        waited += step_ms

    print(f"[{name}] FALHOU: texto '{ready_text}' não apareceu em {deadline_ms // 1000}s")
    return False


def main():
    ok = True
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, cfg in APPS.items():
            page = browser.new_page()
            try:
                ok &= visit(page, name, cfg["url"], cfg["ready_text"])
            except Exception as exc:  # noqa: BLE001
                print(f"[{name}] FALHOU: {exc}")
                ok = False
            finally:
                page.close()
        browser.close()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
