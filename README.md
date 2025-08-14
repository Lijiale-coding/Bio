# Bio Analytics — Mini Prototype (Power BI + Python)

**Objectif.** Un mini prototype analytique autour de l’agriculture **Bio** en France (périmètre **National**, années **2008–2024**).
Il combine **Power BI** (vue direction & dashboard) et **Python** (tendance linéaire, anomalies, backtest, prévision 2025).

**Jeu de données.** Agrégation issue d’un export public de l’**Agence BIO** (France) – statistiques nationales.
Fichier utilisé : `Export Productions Bio - National.xlsx` (provenant du site Agence BIO / éventuellement relayé sur data.gouv.fr).

> Remplacer ce libellé par l’URL exacte de l’export si nécessaire.

---

## 🔎 Ce que montre le prototype

**Page 1 – Vue « Executive »**

* **3 KPI** : **Croissance sur la période sélectionnée** (Δ% = `Année max` vs `Année min`)

  * Entreprises (aval)
  * Exploitations bio **animales**
  * Exploitations bio **végétales**
* **Courbe YoY** (animaux / végétal / entreprises) avec ligne de base **0 %**.
* **3 anneaux** : **part moyenne (%) par type** sur la période.

**Page 2 – Model Monitor**

* **Valeur observée vs tendance linéaire (OLS)**
* **Anomalies** (|z| > 1,5) sur **résiduel** et **YoY**
* **Backtest** (MAE / MAPE) + **prévision 2025** (linéaire & naïve)
* Hypothèses de calcul clairement rappelées : **Echelle géographique = National**.

---

## 📁 Arborescence

```
.
├─ Bio.pbix                          # Rapport Power BI (exemple)
├─ Export Productions Bio - National.xlsx
├─ predictions_bio_poc.csv           # Valeur, tendance, résidu, YoY, z-scores, flags anomalies
├─ model_summary_bio_poc.csv         # Slope/an, backtest MAE/MAPE, forecast 2025 (par indicateur)
├─ action_traitement.py              # Script Python (génération CSV / POC)
├─ notebooks/
│  └─ poc_forecast.ipynb             # Notebook de la POC (tendance/retour arrière/anomalies)
├─ pdf/
│  ├─ Executive-2p.pdf
│  └─ Model-Monitor-2p.pdf
└─ README.md
```

> Pour un travail collaboratif, on peut sauvegarder en **.pbip** (projet Power BI) afin d’avoir `Report/`, `Dataset/model.tmdl`, `Queries/` diff-ables.

---

## 🚀 Ouverture & utilisation

1. Ouvrir **Power BI Desktop** et charger `Bio.pbix`.
2. Utiliser le **segment Année** (table `Years`) pour fixer la **période d’analyse**.
3. Lire les KPI comme **Δ% sur la période sélectionnée** (de `Année min` à `Année max`).
4. La courbe montre le **YoY** annuel ; les anneaux montrent la **part moyenne** sur la période.

**Périmètre permanent** : *National*. Les totaux sont d’abord agrégés **par année**, puis les indicateurs (Δ%, YoY, résidu) sont calculés sur ces agrégats annuels.

---

## 📐 Mesures DAX (extraits)

**Années de la période (respectent le segment `Years`)**

```DAX
Année min (sél.) := MINX(ALLSELECTED('Years'[Année]), 'Years'[Année])
Année max (sél.) := MAXX(ALLSELECTED('Years'[Année]), 'Years'[Année])
```

**Croissance sur la période – exemple « Exploitations animales »**
(du végétal/entreprises : remplacer simplement la table/colonne)

```DAX
Exploitations animales – Croissance % (période) :=
VAR y0 = [Année min (sél.)]
VAR y1 = [Année max (sél.)]
RETURN
IF(
    y0 = y1, BLANK(),
    VAR v0 = CALCULATE(
        SUM('Productions animales'[Nombre de fermes]),
        FILTER(ALL('Productions animales'),
               'Productions animales'[Année] = y0 &&
               'Productions animales'[Echelle géographique] = "National"))
    VAR v1 = CALCULATE(
        SUM('Productions animales'[Nombre de fermes]),
        FILTER(ALL('Productions animales'),
               'Productions animales'[Année] = y1 &&
               'Productions animales'[Echelle géographique] = "National"))
    RETURN DIVIDE(v1 - v0, v0)
)
```

> Variante possible : **CAGR** (taux de croissance annuel composé) si l’on souhaite une métrique « annualisée ».

---

## 🧪 Méthode Python (POC)

* **Agrégation** annuelle (National) pour *animales*, *végétales* et *entreprises aval*
* **Tendance linéaire (OLS)** : `y = a + b·Année` (`numpy.polyfit`)
* **Résidu & anomalies** : `residual = y - ŷ`, **z-score** sur résidu & YoY, seuil |z| > 1,5
* **Backtest** : roulants – entraîne sur  t années, prédit *t+1* → **MAE / MAPE**
* **Prévision 2025** : extrapolation linéaire + **naïve** (dernier point)
* **Sorties** :

  * `predictions_bio_poc.csv` – pour les visuels (courbe, points anomalie, tableau)
  * `model_summary_bio_poc.csv` – pour les KPI de la page « Model Monitor »

**Reproduire**

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |  macOS/Linux: source .venv/bin/activate
pip install -r env/requirements.txt   # pandas, numpy, matplotlib
jupyter lab                           # ouvrir notebooks/poc_forecast.ipynb
```

---

## 🔒 Données & conformité

* Le dépôt ne contient que des **données agrégées / exemples**.
* Ne pas publier de données **sensibles** ou **soumises à droits** ; stocker toute donnée brute privée hors dépôt.
* Si vous référencez la source, indiquer **Agence BIO (France)** – export national (éventuellement via **data.gouv.fr**).

---

## 📄 Licence

Proposé sous **MIT** (modifiable selon vos besoins).

```
MIT License © 2025 <Votre Nom>
```

---

## 📬 Contact

Prototype réalisé par **<Votre Nom>** — **\<votre e-mail / LinkedIn>**.
Deux PDF fournis : **Executive (2p)** et **Model Monitor (2p)**.

---

*(Remplace `<Votre Nom>` et ajoute le lien exact de l’export Agence BIO si tu souhaites pointer vers la page source.)*
