"""
Smoke test de CI: executa cada app Streamlit de ponta a ponta via
streamlit.testing.v1.AppTest (não apenas verifica se o processo sobe).

Isso roda o script de verdade -- incluindo a chamada à API do InfoDengue
em app_vigilancia_real.py -- então pega tanto erro de código quanto
mudança de formato/indisponibilidade da API externa.

Checa tanto exceções não tratadas (at.exception) quanto st.error()
renderizado na tela: app_vigilancia_real.py captura falha de rede por
cidade com try/except e mostra um st.error() em vez de estourar, então
uma checagem só de at.exception não pegaria a API fora do ar.
"""
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

# Desde o Streamlit 1.66, AppTest.from_file() resolve caminhos relativos a
# partir do arquivo que o chama (scripts/), não do diretório atual.
RAIZ = Path(__file__).resolve().parent.parent
APPS = [str(RAIZ / "app.py"), str(RAIZ / "app_vigilancia_real.py")]

falhou = False
for caminho in APPS:
    at = AppTest.from_file(caminho, default_timeout=30).run()
    problemas = list(at.exception) + list(at.error)
    if problemas:
        falhou = True
        print(f"FALHOU: {caminho}")
        for problema in problemas:
            print(f"  {problema}")
    else:
        print(f"OK: {caminho}")

sys.exit(1 if falhou else 0)
