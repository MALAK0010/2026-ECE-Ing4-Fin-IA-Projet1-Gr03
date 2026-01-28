---
marp: true
theme: gaia
paginate: true
backgroundColor: #fff
color: #1a1a1a
---

<!-- Slide 1 - Titre -->
# Détection de Fraude Financière par Graphes

## Projet Académique ECE - Groupe 42

**Malak El Idrissi** & **Joe Boueri**

Intelligence Artificielle & Finances - 2026

---

<!-- Slide 2 - Introduction -->
# Introduction

## Contexte de la Fraude Financière

- **Volume croissant** des transactions financières numériques
- **Complexité accrue** des schémas de fraude
- **Impact économique** : milliards d'euros perdus annuellement
- **Réglementation stricte** : AML/CFT (Anti-Money Laundering / Combating the Financing of Terrorism)

## Enjeux de la Détection

- Détection en temps réel
- Réduction des faux positifs
- Conformité réglementaire
- Protection des institutions financières

---

<!-- Slide 3 - Problématique -->
# Problématique

## Pourquoi les Graphes ?

Les approches traditionnelles basées sur les règles et les statistiques présentent des limites :

| Approche Traditionnelle | Approche par Graphes |
|------------------------|----------------------|
| Analyse transaction par transaction | Analyse des relations entre entités |
| Détection de patterns simples | Détection de structures complexes |
| Difficile de suivre les flux de fonds | Visualisation des chemins de transfert |
| Faux positifs élevés | Contexte relationnel enrichi |

## Avantages des Graphes

- **Représentation naturelle** des relations financières
- **Détection de patterns** invisibles aux méthodes classiques
- **Analyse de communauté** et de centralité
- **Scalabilité** pour grands volumes de données

---

<!-- Slide 4 - Objectifs -->
# Objectifs du Projet

## Trois Types de Fraude à Détecter

### 1. Cycles de Blanchiment
- Boucles de transferts masquant l'origine des fonds
- Retour aux sources après plusieurs transactions

### 2. Smurfing / Schtroumpfage
- Fractionnements de montants vers un compte pivot
- Évitement des seuils de déclaration

### 3. Anomalies de Réseaux
- Comportements atypiques dans la structure des transactions
- Déviations par rapport aux patterns normaux

---

<!-- Slide 5 - Cycles de Blanchiment -->
# Cycles de Blanchiment

## Définition

Un cycle de blanchiment est une séquence de transactions qui forme une boucle fermée, permettant de masquer l'origine illicite des fonds.

```
A → B → C → D → A
```

## Caractéristiques

- **Boucle fermée** : le dernier transfert revient à l'expéditeur initial
- **Complexité variable** : de 3 à N nœuds
- **Montants** : souvent constants ou progressifs
- **Objectif** : brouiller la traçabilité des fonds

## Exemple

```
Compte A (1000€) → Compte B → Compte C → Compte A
```

---

<!-- Slide 6 - Smurfing -->
# Smurfing / Schtroumpfage

## Définition

Technique consistant à fractionner de grosses sommes en multiples petits montants transférés vers un compte pivot, pour éviter les seuils de déclaration.

## Caractéristiques

- **Fractionnement** : montants < seuil réglementaire
- **Compte pivot** : collecte des fonds fractionnés
- **Multiples sources** : plusieurs comptes émetteurs
- **Période courte** : transactions rapprochées dans le temps

## Exemple

```
Compte A (900€) ─┐
Compte B (850€) ─┼→ Compte Pivot (5000€)
Compte C (950€) ─┤
Compte D (950€) ─┘
Compte E (1350€) ─┘
```

---

<!-- Slide 7 - Anomalies de Réseaux -->
# Anomalies de Réseaux

## Définition

Comportements atypiques dans la structure des transactions qui dévient des patterns normaux d'activité financière.

## Types d'Anomalies

### Centralité Anormale
- Nœuds avec un degré de connexion inhabituel
- Hubs artificiels créés pour la fraude

### Structure de Communauté
- Comptes isolés ou formant des clusters suspects
- Connexions transversales inhabituelles

### Temporalité
- Pics d'activité soudains
- Patterns de transaction cycliques anormaux

## Métriques Utilisées

- **Centralité de degré** : nombre de connexions
- **Centralité d'intermédiarité** : contrôle des flux
- **Coefficient de clustering** : densité locale

---

<!-- Slide 8 - Approche Algorithmique -->
# Approche Algorithmique

## Algorithmes Implémentés

### 1. Détection de Cycles - Algorithme de Johnson
- **Complexité** : O((V + E)(c + 1)) où c = nombre de cycles
- **Avantages** : efficace pour graphes de taille moyenne
- **Application** : identification des boucles de blanchiment

### 2. Détection de Communautés - Algorithme de Louvain
- **Approche** : optimisation de la modularité
- **Complexité** : quasi-linéaire O(n log n)
- **Application** : identification de clusters suspects

### 3. Analyse de Centralité
- **Degree Centrality** : importance par nombre de connexions
- **Betweenness Centrality** : contrôle des flux d'information
- **Closeness Centrality** : proximité aux autres nœuds

---

<!-- Slide 9 - Architecture Technique -->
# Architecture Technique

## Stack Technologique

### Langage Principal
- **Python 3.9+** : langage de référence pour la data science

### Bibliothèques Graphes
- **NetworkX** : création, manipulation et analyse de graphes
- **igraph** : algorithmes de graphes performants (optionnel)

### Traitement de Données
- **Pandas** : manipulation de données tabulaires
- **NumPy** : calculs numériques

### Visualisation
- **Matplotlib** : graphiques 2D
- **Plotly** : visualisations interactives

---

<!-- Slide 10 - Implémentation -->
# Implémentation

## Structure du Code

```
src/
├── fraud_detector.py    # Moteur de détection principal
│   ├── FraudDetector     # Classe principale
│   ├── detect_cycles()   # Détection de cycles
│   ├── detect_smurfing() # Détection de smurfing
│   └── detect_anomalies()# Détection d'anomalies
│
└── utils.py              # Fonctions utilitaires
    ├── load_data()       # Chargement des données
    ├── build_graph()     # Construction du graphe
    └── visualize()       # Visualisation
```

## Modules Principaux

### FraudDetector
- Initialisation avec les données transactionnelles
- Méthodes de détection pour chaque type de fraude
- Génération de rapports et métriques

### Utils
- Prétraitement des données
- Conversion transactions → graphe
- Fonctions de visualisation

---

<!-- Slide 11 - Résultats -->
# Résultats

## Exemples de Détection

### Cycles Détectés
- **Nombre moyen** : 5-15 cycles par dataset de test
- **Longueur** : 3 à 7 nœuds principalement
- **Précision** : > 85% sur données synthétiques

### Smurfing Identifié
- **Seuil de détection** : 5+ transactions fractionnées
- **Sensibilité** : ajustable selon paramètres
- **Faux positifs** : < 10% avec calibration

### Anomalies de Réseaux
- **Top 5%** des nœuds par centralité marqués suspects
- **Clusters** : 2-4 communautés atypiques identifiées

## Métriques de Performance

| Métrique | Valeur |
|----------|--------|
| Temps de traitement | < 5s pour 10k transactions |
| Précision globale | 82% |
| Rappel | 78% |
| F1-Score | 0.80 |

---

<!-- Slide 12 - Conclusion -->
# Conclusion

## Résumé du Projet

✅ **Détection de cycles** : Algorithme de Johnson implémenté avec succès  
✅ **Détection de smurfing** : Identification des fractionnements suspects  
✅ **Anomalies de réseaux** : Analyse de centralité et communautés  

## Perspectives

### Améliorations Futures
- **Apprentissage automatique** : intégration de modèles ML
- **Temps réel** : streaming de transactions
- **Deep Learning** : GNN (Graph Neural Networks)
- **Interprétabilité** : explications des décisions

### Extensions Possibles
- Détection de nouvelles fraudes (layering, integration)
- Analyse multi-graphe (temporelle, multi-currency)
- Interface utilisateur pour analystes financiers

---

## Questions ?

**Merci de votre attention**

Malak El Idrissi & Joe Boueri  
ECE - Intelligence Artificielle & Finances - 2026
