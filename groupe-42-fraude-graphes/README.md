# Projet : Détection de Fraude Financière par Graphes (Sujet 42) 

## 📋 Présentation du Groupe
* **Numéro de groupe** : 42
* **Membres du groupe** : 
    * El Idrissi Malak (@MALAK0010)
    * Boueri Joe (@Boueri)

---

## 🎯 Description du Problème
Ce projet s'inscrit dans le cadre du cours d'IA Exploratoire et Symbolique. L'objectif est d'utiliser la **programmation par contraintes et les algorithmes de graphes** pour identifier des comportements frauduleux dans les flux transactionnels. 

Nous nous concentrons sur la détection de structures suspectes telles que :
* **Cycles de blanchiment** : Identification de boucles de transferts masquant l'origine des fonds.
* **Smurfing (Schtroumpfage)** : Détection de fractionnements de montants vers un compte pivot.
* **Anomalies de réseaux** : Analyse de la structure des transactions pour isoler des comportements atypiques.

---

## 🛠️ Organisation du Travail
Conformément aux consignes de structure obligatoire, le travail est organisé dans ce sous-répertoire :

* **`src/`** : Code source Python (NetworkX, Pandas) documenté.
* **`docs/`** : Documentation technique et analyse des résultats.
* **`slides/`** : Support de présentation pour la soutenance finale.
* **`README.md`** : Ce fichier de présentation incluant les procédures.

---

## 🚀 Installation et Utilisation
### Prérequis
* Python 3.10 ou supérieur
* `pip install networkx pandas matplotlib`

### Procédure d'installation
1. Clonez le fork : `git clone [URL_DE_TON_FORK]`
2. Accédez au dossier du groupe : `cd groupe-XX-fraude-graphes`

### Tests
Pour lancer l'analyse de détection sur les données de test :
```bash
python src/fraud_detector.py
