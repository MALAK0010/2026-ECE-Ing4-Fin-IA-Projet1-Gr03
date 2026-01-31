---
marp: false
theme: gaia
paginate: true
backgroundColor: #fff
footer: "Groupe 42 - IA & Finances 2026"
style: |
  section { font-size: 25px; }
  h1 { color: #003366; font-size: 45px; }
  h2 { color: #00509d; font-size: 35px; }
  h3 { color: #c1121f; font-size: 28px; }
  table { font-size: 20px; width: 100%; }
  code { font-size: 18px; }
  .columns { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; }
  .red { color: #c1121f; font-weight: bold; }
  .green { color: #386641; font-weight: bold; }
---

# 🔍 Détection de Fraude Financière par Graphes

### Projet Académique ECE - Groupe 42
[cite_start]**Membres :** Malak El Idrissi & Joe Boueri [cite: 3, 98]

**Moteur :** IA Exploratoire & Symbolique
[cite_start]**Date :** 02 Février 2026 [cite: 4]

---

# Introduction

<div class="columns">
<div>

### Contexte
- [cite_start]**Volume massif** : transactions numériques[cite: 8].
- [cite_start]**Complexité** : schémas de fraude évolutifs[cite: 9].
- [cite_start]**Impact** : <span class="red">Milliards d'euros</span> perdus[cite: 10].
- [cite_start]**Régulation** : Normes AML/CFT strictes[cite: 10].
</div>
<div>

### Enjeux
- Détection en **temps réel**.
- Réduction des **faux positifs**.
- **Conformité** bancaire.
- [cite_start]Protection institutionnelle. [cite: 11]
</div>
</div>

---

# Problématique

### [cite_start]Pourquoi l'Analyse de Graphes ? [cite: 14]

| Approche Traditionnelle | Approche par Graphes |
|:---|:---|
| [cite_start]Analyse isolée (ligne par ligne) [cite: 16] | [cite_start]**Vision relationnelle** (réseau) [cite: 16] |
| Patterns simples (seuils) | **Structures complexes** (cycles) |
| Flux difficiles à tracer | **Chemins de transfert** clairs |
| Taux d'alerte élevé | **Contexte enrichi** |

---

# Objectifs : Les 3 Types de Fraude

<div class="columns">
<div>

### 1. Cycles (Blanchiment) 🔄
[cite_start]Boucles de transferts pour masquer l'origine des fonds. [cite: 20, 21]
### 2. Smurfing (Schtroumpfage) 💰
[cite_start]Fractionnement vers un compte pivot sous les seuils. [cite: 23, 24]
</div>
<div>

### 3. Anomalies de Réseau 🚨
[cite_start]Comportements atypiques et déviations structurelles. [cite: 42, 44]
[cite_start]*(Ex: Hubs artificiels, clusters isolés)*. [cite: 48]
</div>
</div>

---

# 1. Cycles de Blanchiment

### [cite_start]Structure : $A \rightarrow B \rightarrow C \rightarrow D \rightarrow A$ [cite: 30]

- [cite_start]**Définition** : Boucle fermée masquant l'illicite. [cite: 29]
- [cite_start]**Risque** : Plus le cycle est long, plus l'origine est "lavée". [cite: 32]
- [cite_start]**Logique** : L'argent revient au point de départ. [cite: 32]

**Exemple détecté :** `Compte A (1000€) → B → C → Compte A`

---

# 2. Smurfing / Schtroumpfage

### [cite_start]Structure : Multiples sources → Compte Pivot [cite: 36, 39]

- [cite_start]**Tactique** : Montants < seuils de déclaration. [cite: 38]
- [cite_start]**Détection** : Concentration rapide de fonds fractionnés. [cite: 40]

<div style="text-align: center; background: #f0f0f0; padding: 10px; border-radius: 10px;">
A (900€) + B (850€) + C (950€) ➜ <b>Compte Pivot (Total: 2700€)</b>
</div>

---

# 3. Anomalies de Réseaux

### [cite_start]Détection via Métriques de Graphes [cite: 50, 51]

- [cite_start]**Centralité de Degré** : Identification des "Hubs" (comptes pivots). [cite: 46, 47]
- [cite_start]**Betweenness** : Contrôle des flux entre différentes communautés. [cite: 7]
- [cite_start]**Communautés** : Groupes de comptes qui ne traitent qu'entre eux. [cite: 45]

---

# Approche Algorithmique

- [cite_start]**Algorithme de Johnson** : Recherche de cycles élémentaires ($O((V+E)(c+1))$). [cite: 52, 53]
- [cite_start]**Algorithme de Louvain** : Détection de communautés par modularité. [cite: 56]
- [cite_start]**PageRank** : Calcul de l'importance relative des comptes dans le réseau. [cite: 8]

---

# Architecture Technique

<div class="columns">
<div>

### [cite_start]Stack [cite: 59]
- [cite_start]**Python 3.10+** (Langage) [cite: 61]
- [cite_start]**NetworkX** (Graphes) [cite: 63]
- [cite_start]**Pandas/NumPy** (Data) [cite: 65]
- **Matplotlib** (Visu)
</div>
<div>

### [cite_start]Structure `src/` [cite: 67]
- [cite_start]`fraud_detector.py` (Moteur) [cite: 69]
- `data_generator.py` (Synthèse)
- `plotter.py` (Graphiques)
- `main.py` (Execution)
</div>
</div>

---

# Résultats & Performance

### [cite_start]<span class="green">Succès de la détection</span> [cite: 79]

- [cite_start]**Vitesse** : <span class="green">2.67 secondes</span> pour l'analyse complète. [cite: 11]
- [cite_start]**Cycles** : **50 cycles** identifiés sur dataset de test. [cite: 11]
- [cite_start]**Précision** : **> 85%** sur les données synthétiques. [cite: 84]

| Métrique | Valeur |
|:---|:---|
| Temps de traitement | ~3s (10k tx) |
| F1-Score | **0.80** |

---

# Conclusion & Perspectives

- [cite_start]✅ ** Johnson & Louvain** : Opérationnels et performants. [cite: 90, 92]
- ✅ **Alertes** : Scoring de risque automatique implémenté.

### [cite_start]Futur [cite: 94]
- [cite_start]Intégration de **GNN** (Graph Neural Networks). [cite: 95]
- [cite_start]Analyse en **temps réel** via streaming. [cite: 95]

---

# Merci de votre attention !

### Questions ? ❓

**Malak El Idrissi & Joe Boueri**
[cite_start]ECE - 2026 [cite: 98, 99]

---