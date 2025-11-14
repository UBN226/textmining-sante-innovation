import os
import numpy as np
import pandas as pd

OUT_DIR = "outputs"
ARTS = os.path.join("../data/all_articles_processed.csv")


df = pd.read_csv(ARTS).reset_index()  # keep original index as global_index
print("Loaded articles:", df.shape)

# 1) Try to load embeddings.npy
emb_path = os.path.join("outputs","analysis_results","embeddings.npy")
if not os.path.exists(emb_path):
    emb_path = os.path.join("embeddings.npy")  # fallback top-level
if os.path.exists(emb_path):
    emb = np.load(emb_path)
    print("Loaded embeddings from", emb_path, "shape=", emb.shape)
else:
    # Fallback: compute SBERT embeddings
    print("embeddings.npy not trouvé. Calcul des embeddings SBERT (peut prendre du temps)...")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-mpnet-base-v2")   # bon compromis
    texts = df.get("texte_clean_bert", df.get("texte_clean_tfidf", df.get("texte",""))).fillna("").astype(str).tolist()
    emb = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    # optional: save embeddings for réemploi
    os.makedirs(os.path.join(OUT_DIR,"analysis_results"), exist_ok=True)
    np.save(os.path.join(OUT_DIR,"analysis_results","embeddings.npy"), emb)
    print("Saved embeddings to outputs/analysis_results/embeddings.npy")

# 2) Compute UMAP
print("Calcul UMAP...")
import umap.umap_ as umap
reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, metric="cosine", random_state=42)
umap2 = reducer.fit_transform(emb)
print("UMAP shape:", umap2.shape)

# 3) Save coords + meta
coords = pd.DataFrame(umap2, columns=["umap_x","umap_y"])
# attach article fields (make sure same ordering: embeddings were computed on df)
# if embeddings were computed from a different order, adapt accordingly
meta_cols = []
for c in ["source","titre","preview","date","texte_clean_bert"]:
    if c in df.columns:
        coords[c] = df[c].astype(str).values
        meta_cols.append(c)
coords["global_index"] = df["index"].astype(int).values  # original index
out_dir = os.path.join(OUT_DIR,"analysis_results")
os.makedirs(out_dir, exist_ok=True)
coords.to_csv(os.path.join(out_dir,"umap_coords_with_meta.csv"), index=False)
print("Saved UMAP coords to", os.path.join(out_dir,"umap_coords_with_meta.csv"))
