# make_sentiment.py
import os, pandas as pd, numpy as np
OUT_DIR = "outputs"
ARTS = os.path.join("../data/all_articles_processed.csv")

df = pd.read_csv(ARTS)
texts = df.get("texte_clean_bert", df.get("texte_clean_tfidf", df.get("texte",""))).fillna("").astype(str)

# Use transformers pipeline (downloads model if needed)
try:
    from transformers import pipeline
    model_name = "nlptown/bert-base-multilingual-uncased-sentiment"  # general multilingual sentiment
    print("Chargement du modèle de sentiment:", model_name)
    pipe = pipeline("sentiment-analysis", model=model_name, device=-1)  # CPU
except Exception as e:
    print("Impossible de charger transformers pipeline:", e)
    print("Retour: fallback simple (label NEU pour textes vides).")
    pipe = None

records = []
for i, t in enumerate(texts):
    txt = str(t)[:1000]  # tronquer si très long
    if not txt.strip():
        records.append({"global_index": int(i), "label": "NEU", "score": 0.0})
        continue
    if pipe is None:
        records.append({"global_index": int(i), "label": "NEU", "score": 0.0})
    else:
        try:
            out = pipe(txt)[0]
            label = out.get("label", "")
            score = float(out.get("score", 0.0))
            # normalize some model labels to POS/NEG/NEU if needed
            if label.lower().startswith("very positive") or "5" in label or "POS" in label.upper():
                lab = "POS"
            elif label.lower().startswith("very negative") or "1" in label or "NEG" in label.upper():
                lab = "NEG"
            else:
                # some models yield stars or neutral labels; map roughly
                if "negative" in label.lower():
                    lab = "NEG"
                elif "positive" in label.lower():
                    lab = "POS"
                else:
                    lab = "NEU"
            records.append({"global_index": int(i), "label": lab, "score": score})
        except Exception as e:
            records.append({"global_index": int(i), "label": "NEU", "score": 0.0})

sent_df = pd.DataFrame(records)
os.makedirs(os.path.join(OUT_DIR,"analysis_results"), exist_ok=True)
sent_df.to_csv(os.path.join(OUT_DIR,"analysis_results","document_sentiment.csv"), index=False)
print("Saved document_sentiment.csv (rows):", len(sent_df))
