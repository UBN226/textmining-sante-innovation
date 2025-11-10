"""
Phase 2 — NLP (nettoyage, TF-IDF, sentiment, résumé)
Entrée  : outputs/raw_articles_oms_forbes.csv (créé par phase1_scrape.py)
Sorties : 
  outputs/cleaned_texts.csv
  outputs/tfidf_top_terms.csv
  outputs/sentiment_scores.csv
  outputs/summary.txt
"""

import os, re, json
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import nltk

# Télécharger les ressources NLTK si nécessaire
nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)
nltk.download("vader_lexicon", quiet=True)

from nltk.sentiment import SentimentIntensityAnalyzer

INPUT_CSV  = "outputs/raw_articles_oms_forbes.csv"
OUT_CLEAN  = "outputs/cleaned_texts.csv"
OUT_TFIDF  = "outputs/tfidf_top_terms.csv"
OUT_SENT   = "outputs/sentiment_scores.csv"
OUT_SUM    = "outputs/summary.txt"

LANG = "french"       # corpus majoritairement FR (peut mélanger un peu d'EN)
MIN_TOK = 2

os.makedirs("outputs", exist_ok=True)

# --------- Nettoyage / normalisation ----------

def normalize_text(s, lang=LANG, min_tok=MIN_TOK):
    """Nettoyage simplifié + stopwords + stemming Snowball (FR)."""
    if not isinstance(s, str):
        s = str(s or "")
    s = s.lower()
    s = re.sub(r"https?://\S+", " ", s)            # URLs
    s = re.sub(r"[^a-zàâäçéèêëîïôöùûüÿœæ\s-]", " ", s)  # garder lettres + accents + espaces
    s = re.sub(r"\s+", " ", s).strip()
    toks = s.split()
    sw = set(stopwords.words(lang)) if lang in stopwords.fileids() else set()
    toks = [t for t in toks if (t not in sw and len(t) >= min_tok)]
    stem = SnowballStemmer(lang) if lang in ["french","english","spanish","german","italian"] else None
    if stem:
        toks = [stem.stem(t) for t in toks]
    return " ".join(toks)

# --------- Chargement ---------

df = pd.read_csv(INPUT_CSV)
assert {"source","title","text"}.issubset(df.columns), "Colonnes manquantes dans le CSV d'entrée."

# Nettoyage
df["clean_text"] = df["text"].astype(str).apply(normalize_text)
df = df[df["clean_text"].str.len() > 0].reset_index(drop=True)
df.to_csv(OUT_CLEAN, index=False)
print(f"✅ {OUT_CLEAN} sauvegardé ({len(df)} lignes)")

# --------- TF-IDF (top termes) ----------

# On prend un TF-IDF 1-2 grams pour capter quelques expressions
vec = TfidfVectorizer(max_df=0.9, min_df=2, ngram_range=(1,2))
X = vec.fit_transform(df["clean_text"].values)
vocab = np.array(vec.get_feature_names_out())

# termes les plus importants (moyenne TF-IDF)
means = X.mean(axis=0).A1
top_idx = np.argsort(means)[::-1][:50]
top_terms = pd.DataFrame({
    "term": vocab[top_idx],
    "tfidf_mean": means[top_idx]
})
top_terms.to_csv(OUT_TFIDF, index=False)
print(f"✅ {OUT_TFIDF} (top 50 TF-IDF)")

# --------- Sentiment (baseline VADER) ----------
sia = SentimentIntensityAnalyzer()
sent = df["clean_text"].apply(lambda s: sia.polarity_scores(s))
sent_df = pd.DataFrame(list(sent))
sent_df = pd.concat([df[["source","title"]], sent_df], axis=1)
sent_df.to_csv(OUT_SENT, index=False)
print(f"✅ {OUT_SENT} (scores VADER: neg/neu/pos/compound)")

# --------- Résumé extractif (type TextRank simplifié) ----------

def textrank_summary(paragraphs, top_k=5):
    """Résumé extractif par centralité : TF-IDF + similarité cosinus + score de centralité."""
    docs = [p for p in paragraphs if isinstance(p, str) and len(p.split()) > 3]
    if not docs:
        return ""
    v = TfidfVectorizer(max_df=0.95, min_df=2, ngram_range=(1,2))
    M = v.fit_transform(docs)
    sim = cosine_similarity(M)
    # score = somme des similarités (on ignore la diagonale)
    scores = sim.sum(axis=1) - np.diag(sim)
    best = np.argsort(scores)[::-1][:top_k]
    best_sorted = sorted(best)  # conserver l'ordre d'apparition
    return "\n\n".join(docs[i] for i in best_sorted)

# résumé par source, à partire du texte brut pour garder les phrases intactes
summaries = []
for src, sub in df.groupby("source"):
    paras = sub["text"].astype(str).tolist()
    s = textrank_summary(paras, top_k=5)
    summaries.append(f"=== {src} ===\n{s}")

full_summary = "\n\n".join(summaries)
with open(OUT_SUM, "w", encoding="utf-8") as f:
    f.write(full_summary)

print(f"✅ {OUT_SUM} (résumé extractif multi-source)")
