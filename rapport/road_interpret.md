# 📘 Guide d’interprétation — Analyses & Dashboard OMS vs Forbes

Ce guide explique comment lire et interpréter :

1. les sorties du notebook `analysis_oms_forbs.ipynb`  
2. les visualisations du dashboard Streamlit  
3. la logique globale derrière les analyses  

---

# 1. Interprétation des sorties du notebook

## 1.1 Nettoyage (`texte_clean_tfidf`, `texte_clean_bert`)
Deux versions du texte :
- `texte_clean_tfidf` → adapté à TF-IDF (analyse lexicale)
- `texte_clean_bert` → adapté aux embeddings (analyse sémantique)

**Interprétation :**  
Le TF-IDF permet de comparer les mots → vision superficielle.  
BERT permet de comparer les idées → vision profonde.

---

## 1.2 Topics OMS (thèmes extraits)
Le notebook détecte les thèmes dominants dans le corpus OMS.

**Interprétation :**
Ces thèmes sont les **priorités sanitaires**.  
Ils servent de boussole pour mesurer la couverture Forbes.

---

## 1.3 Lexical coverage
Mesure de similarité TF-IDF entre Forbes et les thèmes OMS.

**Si valeur élevée :** Forbes utilise un vocabulaire proche  
**Si faible :** Forbes ne parle pas du sujet

---

## 1.4 Semantic similarity
Mesure BERT → plus fiable.

**Interprétation :**  
Indique si Forbes parle des **mêmes idées**, même si le vocabulaire change.

---

## 1.5 Nearest-neighbor mapping OMS → Forbes
Pour chaque article OMS → l’article Forbes le plus proche.

**Interprétation :**
Permet de voir quels sujets OMS trouvent (ou non) un écho médiatique dans Forbes.

---

## 1.6 Entities extraction
Liste des acteurs cités (pays, entreprises, institutions).

**Interprétation :**
- OMS cite → institutions publiques  
- Forbes cite → acteurs privés (entreprises, investisseurs)

Révèle la nature des priorités éditoriales.

---

# 2. Interprétation des graphiques du dashboard

## 2.1 UMAP (Projection 2D)
Carte des articles OMS + Forbes.

**Interprétation :**
- Groupes → thématiques cohérentes  
- Si Forbes est loin de OMS → peu d’alignement thématique  
- Si proche → Forbes couvre ce thème OMS

---

## 2.2 Barplot Coverage Forbes → Thèmes OMS
Nombre d’articles Forbes liés à chaque thème OMS.

**Interprétation :**
- Grandes barres → thèmes attractifs pour Forbes  
- Barres basses → thèmes ignorés

---

## 2.3 Histogrammes de sentiment
Mesure POS / NEG / NEU.

**OMS :** “ton de crise” → tendance NEG  
**Forbes :** “ton business” → tendance POS

---

## 2.4 Framing pie chart
Répartition des angles éditoriaux.

**Interprétation :**
- Économique → logique business  
- Sanitaire → approche santé publique  
- Mixte → approche hybride

---

## 2.5 Forbes-OMS pairs (correspondances)
Table indiquant l’article Forbes le plus proche de chaque article OMS.

**Interprétation :**
- Si similarité forte → bonne couverture médiatique  
- Si faible / vide → angle OMS non repris par Forbes

---

## 2.6 Wordcloud / entités
Acteurs privés les plus cités.

**Interprétation :**
Montre les influences, sponsors, partenaires, leaders de santé.

---

# 3. Idée générale derrière les analyses

### 🎯 But : mesurer si les **priorités de santé publique** (OMS) sont **traitées** ou **ignorées** dans la **médiatisation économique** (Forbes).

- TF-IDF → correspondance de vocabulaire  
- BERT → correspondance d’idées  
- Topics OMS → structure des priorités  
- Coverage → quels sujets sont repris  
- Framing → comment Forbes parle de la santé  
- Sentiment → ton médiatique  
- UMAP → vision globale de la proximité  

L’ensemble permet d’évaluer :
- la représentation médiatique de la santé en Afrique  
- l’écart OMS ↔ Forbes  
- les zones ignorées par les médias économiques  

---

# ✔ Conclusion du guide
L’analyse révèle deux visions complémentaires de la santé :
- **OMS :** urgence, protection, population  
- **Forbes :** innovation, marché, opportunités  

Ce guide permet d’interpréter clairement toutes les sorties du projet.
# 📘 Guide d’interprétation — Analyses & Dashboard OMS vs Forbes

Ce guide explique comment lire et interpréter :

1. les sorties du notebook `analysis_oms_forbs.ipynb`  
2. les visualisations du dashboard Streamlit  
3. la logique globale derrière les analyses  

---

# 1. Interprétation des sorties du notebook

## 1.1 Nettoyage (`texte_clean_tfidf`, `texte_clean_bert`)
Deux versions du texte :
- `texte_clean_tfidf` → adapté à TF-IDF (analyse lexicale)
- `texte_clean_bert` → adapté aux embeddings (analyse sémantique)

**Interprétation :**  
Le TF-IDF permet de comparer les mots → vision superficielle.  
BERT permet de comparer les idées → vision profonde.

---

## 1.2 Topics OMS (thèmes extraits)
Le notebook détecte les thèmes dominants dans le corpus OMS.

**Interprétation :**
Ces thèmes sont les **priorités sanitaires**.  
Ils servent de boussole pour mesurer la couverture Forbes.

---

## 1.3 Lexical coverage
Mesure de similarité TF-IDF entre Forbes et les thèmes OMS.

**Si valeur élevée :** Forbes utilise un vocabulaire proche  
**Si faible :** Forbes ne parle pas du sujet

---

## 1.4 Semantic similarity
Mesure BERT → plus fiable.

**Interprétation :**  
Indique si Forbes parle des **mêmes idées**, même si le vocabulaire change.

---

## 1.5 Nearest-neighbor mapping OMS → Forbes
Pour chaque article OMS → l’article Forbes le plus proche.

**Interprétation :**
Permet de voir quels sujets OMS trouvent (ou non) un écho médiatique dans Forbes.

---

## 1.6 Entities extraction
Liste des acteurs cités (pays, entreprises, institutions).

**Interprétation :**
- OMS cite → institutions publiques  
- Forbes cite → acteurs privés (entreprises, investisseurs)

Révèle la nature des priorités éditoriales.

---

# 2. Interprétation des graphiques du dashboard

## 2.1 UMAP (Projection 2D)
Carte des articles OMS + Forbes.

**Interprétation :**
- Groupes → thématiques cohérentes  
- Si Forbes est loin de OMS → peu d’alignement thématique  
- Si proche → Forbes couvre ce thème OMS

---

## 2.2 Barplot Coverage Forbes → Thèmes OMS
Nombre d’articles Forbes liés à chaque thème OMS.

**Interprétation :**
- Grandes barres → thèmes attractifs pour Forbes  
- Barres basses → thèmes ignorés

---

## 2.3 Histogrammes de sentiment
Mesure POS / NEG / NEU.

**OMS :** “ton de crise” → tendance NEG  
**Forbes :** “ton business” → tendance POS

---

## 2.4 Framing pie chart
Répartition des angles éditoriaux.

**Interprétation :**
- Économique → logique business  
- Sanitaire → approche santé publique  
- Mixte → approche hybride

---

## 2.5 Forbes-OMS pairs (correspondances)
Table indiquant l’article Forbes le plus proche de chaque article OMS.

**Interprétation :**
- Si similarité forte → bonne couverture médiatique  
- Si faible / vide → angle OMS non repris par Forbes

---

## 2.6 Wordcloud / entités
Acteurs privés les plus cités.

**Interprétation :**
Montre les influences, sponsors, partenaires, leaders de santé.

---

# 3. Idée générale derrière les analyses

### 🎯 But : mesurer si les **priorités de santé publique** (OMS) sont **traitées** ou **ignorées** dans la **médiatisation économique** (Forbes).

- TF-IDF → correspondance de vocabulaire  
- BERT → correspondance d’idées  
- Topics OMS → structure des priorités  
- Coverage → quels sujets sont repris  
- Framing → comment Forbes parle de la santé  
- Sentiment → ton médiatique  
- UMAP → vision globale de la proximité  

L’ensemble permet d’évaluer :
- la représentation médiatique de la santé en Afrique  
- l’écart OMS ↔ Forbes  
- les zones ignorées par les médias économiques  

---

# ✔ Conclusion du guide
L’analyse révèle deux visions complémentaires de la santé :
- **OMS :** urgence, protection, population  
- **Forbes :** innovation, marché, opportunités  

Ce guide permet d’interpréter clairement toutes les sorties du projet.
