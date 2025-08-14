# Bio Analytics — Mini Prototype (Power BI + Python)

**Objectif.** Mini-prototype analytique autour de l’agriculture **Bio** en France (périmètre **National**, années **2008–2024**).  
Vue direction avec **Power BI**, plus un script **Python** pour préparer deux fichiers agrégés (CSV) utilisés par le rapport.

**Source des données.** Export public de l’**Agence BIO** (France) — statistiques nationales.  
Fichier exemple inclus : `Export Productions Bio - National.xlsx`  
Référence : https://www.agencebio.org/api/production/export?level=france

---

## 📁 Contenu du dépôt

```

.
├─ Bio.pbix                          # Rapport Power BI (pages Executive + Model Monitor)
├─ Export Productions Bio - National.xlsx   # Export national (exemple)
├─ predictions\_bio\_poc.csv           # Série annuelle avec: value, pred\_linear, residual, yoy, z-scores, flags d’anomalie
├─ model\_summary\_bio\_poc.csv         # Slope/an, backtest MAE/MAPE, prévision 2025 (par indicateur)
├─ action\_traitement.py              # Script Python (préparation / export des CSV)
└─ README.md

```

> Les deux CSV sont déjà prêts à l’emploi et alimentent directement le PBIX.

---

## 🚀 Utilisation

1. Ouvrir **Power BI Desktop** et charger `Bio.pbix`.  
2. Segment **Année** pour choisir la période d’analyse.  
3. **Page Executive**  
   - 3 KPI : **croissance sur la période sélectionnée** (Δ% = Année max vs Année min)  
   - Courbe **YoY** (animaux / végétal / entreprises) avec ligne de base 0 %  
   - Anneaux : **part moyenne (%)** par type sur la période  
4. **Page Model Monitor**  
   - **Observé vs tendance linéaire (OLS)**, **anomalies** (z-score |z|>1,5)  
   - **Backtest** (MAE / MAPE) et **prévision 2025** (linéaire + naïve)  
   - Hypothèse : **Echelle géographique = National**

**Remarque de lecture.** Les KPI affichent la **variation globale** entre l’Année min et l’Année max de la sélection, tandis que la courbe montre la **variation annuelle (YoY)**.

---

## 🧩 Script Python (facultatif)

`action_traitement.py` illustre la préparation des agrégats :  
- agrégation annuelle (National)  
- tendance linéaire (OLS), résidu, z‐score (résidu & YoY), flags d’anomalie  
- backtest (MAE / MAPE)  
- export vers `predictions_bio_poc.csv` et `model_summary_bio_poc.csv`

> L’exécution du script n’est pas requise pour consulter le rapport : les CSV fournis sont déjà générés.

---

## 🔒 Données & conformité

- Dépôt limité à des **données agrégées / exemples**.  
- Ne pas publier de données sensibles/soumises à droits.  
- Si vous référencez la source : **Agence BIO (France)** — export national.

---

## 📄 Licence

Sous **Licence MIT** (version française).  
Voir le fichier `LICENSE` si présent dans le dépôt.

---

## 📬 Contact

Prototype réalisé par **<Li>** — **<lijiale524@gmail.com / [linkdin](https://www.linkedin.com/in/li-jiale-d%C3%A9veloppeur-num%C3%A9rique/)>**.
```


---
