import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

# --- 1) Chemin du fichier source (adapter si besoin) ---
src = Path("Export Productions Bio - National.xlsx")

# --- 2) Chargement des feuilles ---
veg = pd.read_excel(src, sheet_name='Productions végétales')
ani = pd.read_excel(src, sheet_name='Productions animales')
aval = pd.read_excel(src, sheet_name="Entreprises de l'aval")

# --- 3) Ne garder que le niveau National ---
veg_nat = veg[veg['Echelle géographique'] == 'National'].copy()
ani_nat = ani[ani['Echelle géographique'] == 'National'].copy()
aval_nat = aval[aval['Echelle géographique'] == 'National'].copy()

# --- 4) Agrégation annuelle (somme) ---
veg_year = (veg_nat.groupby('Année', as_index=False)
            .agg({'Surface bio (en ha)': 'sum',
                  'Surface en conversion (en ha)': 'sum',
                  'Nombre de fermes': 'sum'})
            .sort_values('Année'))

ani_year = (ani_nat.groupby('Année', as_index=False)
            .agg({'Animaux ou ruches bio': 'sum',
                  'Animaux ou ruches en conversion': 'sum',
                  'Nombre de fermes': 'sum'})
            .sort_values('Année'))

aval_year = (aval_nat.groupby('Année', as_index=False)
             .agg({"Nombre d'entreprises": 'sum'})
             .sort_values('Année'))

# --- 5) Préparer les séries à modéliser ---
series_defs = [
    ("Surface bio (ha)", veg_year[['Année', 'Surface bio (en ha)']].rename(columns={'Surface bio (en ha)':'value'})),
    ("Surface en conversion (ha)", veg_year[['Année', 'Surface en conversion (en ha)']].rename(columns={'Surface en conversion (en ha)':'value'})),
    ("Animaux/ruches bio", ani_year[['Année', 'Animaux ou ruches bio']].rename(columns={'Animaux ou ruches bio':'value'})),
    ("Entreprises aval (nbr)", aval_year[['Année', "Nombre d'entreprises"]].rename(columns={"Nombre d'entreprises":'value'})),
]

# --- 6) Fonctions utilitaires ---
def ajuster_tendance_lineaire(df):
    """
    Ajuste une régression linéaire (y ~ année) et calcule :
      - valeur prédite (pred_linear)
      - baseline naïve (pred_naive = valeur de l'année précédente)
      - résidus et z-score des résidus
      - YoY et z-score du YoY
      - prévision 2025 par la tendance et baseline naïve
    Retourne (dataframe_avec_indicateurs, forecast2025_linear, forecast2025_naive, coefficients)
    """
    d = df.dropna().copy().sort_values('Année')
    x = d['Année'].astype(float).values
    y = d['value'].astype(float).values

    # Régression linéaire OLS via polyfit (degré 1)
    coef = np.polyfit(x, y, 1)  # [pente, intercept]
    pred_lin = np.polyval(coef, x)
    residual = y - pred_lin

    # z-score des résidus
    if residual.std(ddof=1) > 0:
        z = (residual - residual.mean()) / residual.std(ddof=1)
    else:
        z = np.zeros_like(residual)

    # Baseline naïve = valeur de l'année précédente
    pred_naive = np.insert(y[:-1], 0, np.nan)

    # YoY (taux de croissance annuel)
    yoy = np.insert(np.diff(y) / y[:-1], 0, np.nan)
    yoy_std = np.nanstd(yoy, ddof=1)
    yoy_z = (yoy - np.nanmean(yoy)) / (yoy_std if yoy_std > 0 else 1.0)

    out = d.copy()
    out['pred_linear'] = pred_lin
    out['pred_naive'] = pred_naive
    out['residual'] = residual
    out['residual_z'] = z
    out['yoy'] = yoy
    out['yoy_z'] = yoy_z

    # Prévisions 2025
    f2025_lin = float(np.polyval(coef, 2025.0))
    f2025_naive = float(y[-1]) if len(y) > 0 else np.nan

    return out, f2025_lin, f2025_naive, coef

def backtest_roulant(df, min_points=6):
    """
    Walk-forward : pour chaque année i (après un minimum d'historique),
    on ajuste sur les années <= i-1 puis on prédit l'année i.
    Renvoie MAE, MAPE et le nombre d'années testées.
    """
    d = df.dropna().sort_values('Année').copy()
    xs = d['Année'].values.astype(float)
    ys = d['value'].values.astype(float)
    preds, trues = [], []

    for i in range(min_points, len(xs)):
        coef = np.polyfit(xs[:i], ys[:i], 1)
        yhat = np.polyval(coef, xs[i])
        preds.append(yhat)
        trues.append(ys[i])

    if not preds:
        return np.nan, np.nan, 0

    preds = np.array(preds); trues = np.array(trues)
    mae = float(np.mean(np.abs(trues - preds)))
    mape = float(np.mean(np.abs(trues - preds) / np.maximum(trues, 1e-9)))
    n = len(trues)
    return mae, mape, n

# --- 7) Boucle sur les indicateurs ---
rows = []
summ_rows = []

for name, dfm in series_defs:
    out, f25_lin, f25_naive, coef = ajuster_tendance_lineaire(dfm)
    mae, mape, n = backtest_roulant(dfm, min_points=min(6, max(3, len(dfm)-8)))
    out['metric'] = name
    # Règle simple d'anomalie : |z| > 1.5
    out['is_anomaly_resid'] = (np.abs(out['residual_z']) > 1.5).astype(int)
    out['is_anomaly_yoy'] = (np.abs(out['yoy_z']) > 1.5).astype(int)
    rows.append(out)
    summ_rows.append({
        "metric": name,
        "slope_per_year": float(coef[0]),
        "forecast_2025_linear": f25_lin,
        "forecast_2025_naive": f25_naive,
        "backtest_MAE": mae,
        "backtest_MAPE": mape,
        "backtest_n_years": n
    })

pred_df = pd.concat(rows, ignore_index=True)
summary_df = pd.DataFrame(summ_rows)

# --- 8) Exports (UTF-8 avec BOM pour Excel) ---
pred_path = Path("predictions_bio_poc.csv")
sum_path  = Path("model_summary_bio_poc.csv")
pred_df.to_csv(pred_path, index=False, encoding="utf-8-sig")
summary_df.to_csv(sum_path, index=False, encoding="utf-8-sig")

print("OK. Fichiers exportés :")
print(" -", pred_path)
print(" -", sum_path)
