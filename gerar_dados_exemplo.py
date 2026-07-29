"""
Gera um CSV de exemplo com a MESMA FORMA dos dados do seu pipeline de
curadoria (compostos NMDA/GluN2B, Ki/IC50, pKa predito, MW, docking).
Os VALORES são sintéticos (não é o seu dataset real) -- é só para você
ter algo para rodar agora. Troque pelo seu CSV real depois (mesma
estrutura de colunas, é só trocar o caminho do arquivo no app.py).
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
n = 250

subtipos = rng.choice(["GluN2A", "GluN2B", "GluN2C", "GluN2D"], size=n, p=[0.35, 0.4, 0.15, 0.10])

df = pd.DataFrame({
    "compound_id": [f"CMP-{i:04d}" for i in range(1, n + 1)],
    "receptor_subtype": subtipos,
    "MW": rng.normal(380, 60, n).round(2),
    "LogP": rng.normal(2.8, 1.1, n).round(2),
    "pKa_predito": rng.normal(7.4, 1.6, n).round(2),
    "Ki_nM": rng.lognormal(mean=4.5, sigma=1.3, size=n).round(1),
    "IC50_nM": rng.lognormal(mean=5.0, sigma=1.2, size=n).round(1),
    "docking_score": rng.normal(-8.2, 1.4, n).round(2),
    "fonte_literatura": rng.choice(["PubChem", "ChEMBL", "BindingDB", "literatura primária"], size=n),
})

df.to_csv("dados_exemplo_compostos.csv", index=False)
print(f"Gerado dados_exemplo_compostos.csv com {n} linhas.")
