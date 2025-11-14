import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="OMS vs Forbes Dashboard", layout="wide")
st.title("Dashboard interactif — OMS vs Forbes")

OUT_DIR = "outputs"
RES = os.path.join(OUT_DIR, "analysis_results")

def load_optional(path):
    return pd.read_csv(path) if os.path.exists(path) else None

# Load main CSV
MAIN_CSV = os.path.join("../data/all_articles_processed.csv")
if not os.path.exists(MAIN_CSV):
    MAIN_CSV = os.path.join(OUT_DIR, "all_articles_processed.csv")

if not os.path.exists(MAIN_CSV):
    st.error("Aucun fichier 'all_articles_processed*.csv' trouvé dans /outputs/")
    st.stop()

df = pd.read_csv(MAIN_CSV)
df["preview"] = df.get("preview", df.get("titre", ""))

# Load artifacts
coords = load_optional(os.path.join(RES, "umap_coords_with_meta.csv"))
cov = load_optional(os.path.join(RES, "coverage_combined_forbes.csv"))
sent = load_optional(os.path.join(RES, "document_sentiment.csv"))
fr = load_optional(os.path.join(RES, "framing_forbes.csv"))
pairs = load_optional(os.path.join(RES, "oms_to_forbes_pairs.csv"))
ents = load_optional(os.path.join(RES, "forbes_entities.csv"))

# Sidebar filters
st.sidebar.header("Filtres")
src_opts = ["All"] + sorted(df["source"].dropna().unique().tolist())
sel_source = st.sidebar.selectbox("Source", src_opts)

sent_opts = ["All"]
if sent is not None and "label" in sent.columns:
    sent_opts += sorted(sent["label"].unique().tolist())
sel_sent = st.sidebar.selectbox("Sentiment", sent_opts)

frame_opts = ["All"]
if fr is not None:
    frame_opts += sorted(fr["framing"].unique().tolist())
sel_framing = st.sidebar.selectbox("Framing", frame_opts)

# Apply filters
fdf = df.copy()
if sel_source != "All":
    fdf = fdf[fdf["source"] == sel_source]

if sent is not None and sel_sent != "All":
    t = sent[["global_index", "label"]].rename(columns={"global_index": "idx", "label": "sent_label"})
    fdf = fdf.reset_index().merge(t, left_on='index', right_on='idx', how='left').set_index('index')
    fdf = fdf[fdf["sent_label"] == sel_sent]

if fr is not None and sel_framing != "All":
    t = fr[["global_index", "framing"]].rename(columns={"global_index": "idx"})
    fdf = fdf.reset_index().merge(t, left_on='index', right_on='idx', how='left').set_index('index')
    fdf = fdf[fdf["framing"] == sel_framing]

# --- UMAP Plot ---
st.subheader("Projection UMAP — Visualisation des articles")
if coords is not None:
    fig = px.scatter(
        coords,
        x="umap_x", y="umap_y",
        color="source",
        hover_data=["titre", "preview"],
        height=650,
        title="Projection UMAP — Visualisation des articles"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("UMAP non disponible. Lance l'analyse pour générer umap_coords_with_meta.csv.")

# --- Coverage bar plot ---
st.subheader("Couverture des thèmes OMS par Forbes")
if cov is not None:
    topic_cols = [c for c in cov.columns if c.startswith("covered_topic_")]
    cover_counts = cov[topic_cols].sum().reset_index()
    cover_counts.columns = ["topic", "count"]
    cover_counts["topic"] = cover_counts["topic"].str.replace("covered_topic_", "").astype(int)

    fig = px.bar(cover_counts, x="topic", y="count", title="Nombre d’articles Forbes couvrant chaque thème de l’OMS")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Coverage non disponible.")

# --- Sentiment ---
st.subheader("Répartition du sentiment par source")
if sent is not None:
    merged = sent.merge(df[["source"]], left_on="global_index", right_index=True, how="left")
    fig = px.histogram(merged, x="label", color="source", barmode="group", title="Répartition du sentiment par source")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Sentiment non disponible.")

# --- Framing ---
st.subheader("Répartition des angles (framing) dans les articles Forbes")
if fr is not None:
    counts = fr["framing"].value_counts().reset_index()
    counts.columns = ["framing", "count"]
    fig = px.pie(counts, names="framing", values="count", title="Répartition des angles (framing) dans les articles Forbes")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Framing indisponible.")

# --- Nearest neighbors ---
st.subheader("Correspondances OMS → Forbes")
if pairs is not None:
    if "titre" in df.columns:
        art = df.reset_index().rename(columns={"index": "idx"})
        m = pairs.merge(art[["idx", "titre"]], left_on="oms_index", right_on="idx", how="left").rename(columns={"titre": "oms_title"})
        m = m.merge(art[["idx", "titre"]], left_on="forbes_index", right_on="idx", how="left").rename(columns={"titre": "forbes_title"})
        st.dataframe(m[["oms_index", "oms_title", "forbes_index", "forbes_title", "similarity"]].head(25))
else:
    st.info("Correspondances OMS→Forbes non disponibles.")

# --- Entities ---
st.subheader("Entités les plus citées dans Forbes")
if ents is not None:
    top10 = ents["entity"].value_counts().head(20)
    st.write(top10)
else:
    st.info("Entities non disponibles.")

# --- Table filtered ---
st.subheader("Articles filtrés")
st.dataframe(fdf[["source", "titre", "preview"]].head(50))

# Sidebar files
st.sidebar.markdown("### Fichiers disponibles")
if os.path.exists(RES):
    for f in sorted(os.listdir(RES)):
        st.sidebar.markdown(f"- {f}")
