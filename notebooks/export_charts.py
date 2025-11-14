import os, pandas as pd, numpy as np
import plotly.express as px
from pathlib import Path

OUT_DIR = Path("outputs")
RES_DIR = OUT_DIR / "analysis_results"

def load_csv(name):
    p = RES_DIR / name
    return pd.read_csv(p) if p.exists() else None

coords = load_csv("umap_coords_with_meta.csv")
cov = load_csv("coverage_combined_forbes.csv")
ents = load_csv("forbes_entities.csv")
ents_oms = load_csv("oms_entities.csv")
sent = load_csv("document_sentiment.csv")

RES_DIR.mkdir(parents=True, exist_ok=True)
exported = []
if coords is not None:
    fig = px.scatter(coords, x='umap_x', y='umap_y', color='source', title='Projection UMAP — Visualisation des articles')
    out = RES_DIR / 'umap_sources.png'; fig.write_image(str(out)); exported.append(str(out))
if cov is not None:
    topic_cols = [c for c in cov.columns if c.startswith('covered_topic_')]
    cover_counts = cov[topic_cols].sum().reset_index(); cover_counts.columns=['metric','count']; cover_counts['topic']=cover_counts['metric'].str.replace('covered_topic_','').astype(int)
    fig2 = px.bar(cover_counts.sort_values('count',ascending=False), x='topic', y='count', title="Nombre d'articles Forbes couvrant chaque thème de l'OMS")
    out2 = RES_DIR / 'coverage_bar.png'; fig2.write_image(str(out2)); exported.append(str(out2))
if ents is not None:
    df_top = ents['entity'].value_counts().head(50).reset_index(); df_top.columns=['entity','count']
    fig3 = px.bar(df_top, x='count', y='entity', orientation='h', title='Top entités — Forbes')
    out3 = RES_DIR / 'top_entities_forbes.png'; fig3.write_image(str(out3)); exported.append(str(out3))
if sent is not None:
    fig5 = px.histogram(sent, x='label', title='Répartition du sentiment (tous articles)')
    out5 = RES_DIR / 'sentiment_hist.png'; fig5.write_image(str(out5)); exported.append(str(out5))

print("Exported:", exported)
