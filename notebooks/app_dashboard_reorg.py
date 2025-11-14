import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="whitegrid")

st.set_page_config(page_title="OMS vs Forbes Afrique — Dashboard", layout="wide")

OUT_DIR = "./outputs"
RES_DIR = os.path.join(OUT_DIR, "analysis_results")

def load_csv(name):
    p = os.path.join(RES_DIR, name)
    return pd.read_csv(p) if os.path.exists(p) else None

coords = load_csv("umap_coords_with_meta.csv")
cov = load_csv("coverage_combined_forbes.csv")
sim = load_csv("semantic_similarity_forbes.csv")
lex = load_csv("lexical_coverage_forbes.csv")
sent = load_csv("document_sentiment.csv")
fr = load_csv("framing_forbes.csv")
ents = load_csv("forbes_entities.csv")
ents_oms = load_csv("oms_entities.csv")

# Load main articles file optionally
main_df = pd.read_csv("../data/all_articles_processed.csv")

st.markdown(
    """
    <style>
    .big-title {font-size:42px; font-weight:700; color:#ffffff; margin-bottom:0.2rem;}
    .sub-title {font-size:14px; color:#cbd5e0; margin-top:0; margin-bottom:1.2rem;}
    .kpi-card {background:#0f1724; border-radius:10px; padding:18px; box-shadow: 0 4px 14px rgba(2,6,23,0.6);}
    .kpi-value {font-size:28px; color:#ffffff; font-weight:700;}
    .kpi-label {font-size:12px; color:#94a3b8;}
    </style>
    """, unsafe_allow_html=True
)
st.markdown("<div class='big-title'>Analyse comparative — OMS vs Forbes Afrique</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Couverture médiatique, thématiques, framing & similarités sémantiques</div>", unsafe_allow_html=True)
st.markdown("---")

page = st.sidebar.selectbox("Aller à", ["Accueil", "Thématiques & Couverture", "Analyse sémantique (UMAP)", "Entités & Acteurs", "Sentiment & Framing", "Export graphiques"])

def safe_len(df, cond=None):
    try:
        if df is None: return "N/A"
        if cond is None: return len(df)
        return int(df[df['source'].str.contains(cond, na=False)].shape[0])
    except Exception:
        return "N/A"

if page == "Accueil":
    st.header("Accueil — Résumé exécutif")

    n_oms = safe_len(coords, "WHO") if coords is not None else (safe_len(main_df, "WHO") if main_df is not None else "N/A")
    n_forbes = safe_len(coords, "Forbes") if coords is not None else (safe_len(main_df, "Forbes") if main_df is not None else "N/A")

    pct_covered = "N/A"
    if cov is not None:
        topic_cols = [c for c in cov.columns if c.startswith("covered_topic_")]
        total_topics = max(1, len(topic_cols))
        covered = int((cov[topic_cols].sum() > 0).sum())
        pct_covered = f"{covered}/{total_topics} thèmes"

    framing_dom = "N/A"
    if fr is not None and 'framing' in fr.columns and not fr['framing'].empty:
        framing_dom = str(fr['framing'].mode().iloc[0])

    c1, c2, c3, c4 = st.columns([1.2,1.2,1.2,1.2])
    with c1:
        st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Articles OMS (approx.)</div><div class='kpi-value'>{n_oms}</div><div class='kpi-label'>Nombre d'articles issus du corpus OMS</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Articles Forbes (approx.)</div><div class='kpi-value'>{n_forbes}</div><div class='kpi-label'>Nombre d'articles provenant de Forbes</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Thèmes OMS couverts (Forbes)</div><div class='kpi-value'>{pct_covered}</div><div class='kpi-label'>Nombre de thèmes OMS avec au moins 1 article Forbes</div></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Framing dominant (Forbes)</div><div class='kpi-value'>{framing_dom}</div><div class='kpi-label'>Angle éditorial le plus fréquent</div></div>", unsafe_allow_html=True)

    st.markdown("### Statistiques rapides")
    s1, s2, s3 = st.columns(3)
    if sent is not None and 'label' in sent.columns:
        s_counts = sent['label'].value_counts()
        s1.metric("POSITIF", int(s_counts.get("POS", 0)))
        s2.metric("NEGATIF", int(s_counts.get("NEG", 0)))
        s3.metric("NEUTRE", int(s_counts.get("NEU", 0)))
    else:
        s1.write("Sentiment non disponible")
        s2.write("")
        s3.write("")

    st.markdown("### Thèmes Forbes les plus couverts")
    if cov is not None:
        topic_cols = [c for c in cov.columns if c.startswith("covered_topic_")]
        cover_counts = cov[topic_cols].sum().sort_values(ascending=False)
        df_cover = pd.DataFrame({"topic": cover_counts.index.str.replace("covered_topic_",""), "count": cover_counts.values})
        fig = px.bar(df_cover.head(8), x="topic", y="count", title="Top thèmes (Forbes) — nombre d'articles")
        fig.update_layout(title_font=dict(size=16), xaxis_title="ID thématique OMS", yaxis_title="Nombre d'articles Forbes")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Coverage non disponible — exécute `make_all.py` pour générer les fichiers d'analyse.")

    st.markdown("---")
    st.markdown("### Entités — aperçu rapide")
    if ents is not None:
        df_top = ents['entity'].value_counts().head(8).reset_index()
        df_top.columns = ['entity','count']
        figE = px.bar(df_top, x='count', y='entity', orientation='h', title='Top entités — Forbes (aperçu)')
        st.plotly_chart(figE, use_container_width=True)
    else:
        st.info("Entités Forbes non disponibles — exécute `make_all.py` puis `export_charts.py`.")


# PAGE: Thématiques & Couverture
if page == "Thématiques & Couverture":
    st.header("Thématiques & Couverture OMS → Forbes")
    st.markdown("Interprétation : ce module montre quels thèmes identifiés dans le corpus OMS sont repris par Forbes (lexicalement et sémantiquement).")
    if cov is not None:
        st.subheader("Nombre d'articles Forbes par thème OMS")
        topic_cols = [c for c in cov.columns if c.startswith("covered_topic_")]
        cover_counts = cov[topic_cols].sum().reset_index()
        cover_counts.columns = ["metric","count"]
        cover_counts['topic'] = cover_counts['metric'].str.replace("covered_topic_","").astype(int)
        fig = px.bar(cover_counts.sort_values("count", ascending=False), x="topic", y="count", title="Nombre d'articles Forbes couvrant chaque thème de l'OMS")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Coverage non disponible.")
    if lex is not None or sim is not None:
        st.subheader("Heatmap Moyenne lexicale et sémantique par thème")
        # build df_metrics if possible
        rows = []
        topic_ids = set()
        if lex is not None:
            topic_ids |= {int(c.replace('lex_topic_','')) for c in lex.columns if c.startswith('lex_topic_')}
        if sim is not None:
            topic_ids |= {int(c.replace('sim_topic_','')) for c in sim.columns if c.startswith('sim_topic_')}
        topic_ids = sorted(topic_ids)
        for t in topic_ids:
            mean_lex = lex[f'lex_topic_{t}'].mean() if (lex is not None and f'lex_topic_{t}' in lex.columns) else np.nan
            mean_sim = sim[f'sim_topic_{t}'].mean() if (sim is not None and f'sim_topic_{t}' in sim.columns) else np.nan
            rows.append({'topic':t,'mean_lex':mean_lex,'mean_sim':mean_sim})
        if rows:
            df_metrics = pd.DataFrame(rows).set_index('topic').fillna(0)
            fig = px.imshow(df_metrics, labels=dict(x="Métrique", y="Thème"), x=df_metrics.columns, y=df_metrics.index, title="Moyenne lexicale et sémantique par thématique OMS")
            st.plotly_chart(fig, use_container_width=True)
    if sim is not None:
        st.subheader("Distribution de la similarité sémantique par thème (Forbes)")
        sim_cols = [c for c in sim.columns if c.startswith('sim_topic_')]
        if sim_cols:
            sim_long = sim.melt(id_vars=['global_index'], value_vars=sim_cols, var_name='topic', value_name='sim')
            sim_long['topic'] = sim_long['topic'].str.replace('sim_topic_','').astype(int)
            fig = px.box(sim_long, x='topic', y='sim', title='Distribution de la similarité sémantique par thématique OMS')
            st.plotly_chart(fig, use_container_width=True)
    st.markdown("Statistiques :")
    if sim is not None:
        st.write("Similarité moyenne (Forbes → OMS) :", sim[[c for c in sim.columns if c.startswith('sim_topic_')]].mean().mean())
    if cov is not None:
        st.write("Thèmes couverts (count>0) :", (cov[[c for c in cov.columns if c.startswith('covered_topic_')]].sum()>0).sum())

# PAGE: UMAP
if page == "Analyse sémantique (UMAP)":
    st.header("Projection UMAP — Articles OMS + Forbes")
    st.markdown("Interprétation : les points proches sont sémantiquement proches. Les couleurs indiquent la source ou le framing.")
    if coords is None:
        st.info("UMAP non disponible. Exécute le script de génération (`make_all.py`) pour créer `umap_coords_with_meta.csv`.")
    else:
        color_choice = st.selectbox("Colorer par", ["source","framing","sentiment"], index=0)
        hover = []
        for c in ["titre","preview","source","date"]:
            if c in coords.columns: hover.append(c)
        fig = px.scatter(coords, x='umap_x', y='umap_y', color=(coords[color_choice] if color_choice in coords.columns else 'source'), hover_data=hover, title="Projection UMAP — Visualisation des articles", height=700)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("Statistiques UMAP :")
        st.write("Nombre de points affichés :", len(coords))
        # simple clustering estimate
        if len(coords) > 10:
            try:
                from sklearn.cluster import KMeans
                k = min(8, max(2, len(coords)//20))
                km = KMeans(n_clusters=k, random_state=42).fit(coords[['umap_x','umap_y']])
                coords['cluster_km'] = km.labels_
                counts = coords['cluster_km'].value_counts().sort_index()
                st.write("Estim. clusters (KMeans):", counts.to_dict())
            except Exception:
                pass

# PAGE: Entités & Acteurs
if page == "Entités & Acteurs":
    st.header("Entités nommées — OMS vs Forbes")
    st.markdown("Wordclouds et barplots des entités les plus citées dans chaque source.")
    # Wordclouds
    try:
        from wordcloud import WordCloud
        have_wc = True
    except Exception:
        have_wc = False
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top entités — OMS")
        if ents_oms is not None:
            top_oms = ents_oms['entity'].value_counts().head(50)
            if have_wc:
                wc = WordCloud(width=400, height=300).generate_from_frequencies(top_oms.to_dict())
                plt.imshow(wc, interpolation='bilinear'); plt.axis('off')
                st.pyplot(plt.gcf()); plt.clf()
            else:
                st.bar_chart(top_oms.head(20))
        else:
            st.info("Fichier d'entités OMS non disponible.")
    with col2:
        st.subheader("Top entités — Forbes")
        if ents is not None:
            top_forbes = ents['entity'].value_counts().head(50)
            if have_wc:
                wc = WordCloud(width=400, height=300).generate_from_frequencies(top_forbes.to_dict())
                plt.imshow(wc, interpolation='bilinear'); plt.axis('off')
                st.pyplot(plt.gcf()); plt.clf()
            else:
                st.bar_chart(top_forbes.head(20))
        else:
            st.info("Fichier d'entités Forbes non disponible.")
    st.subheader("Graphiques — Top entités (barplots)")
    if ents is not None:
        df_top = ents['entity'].value_counts().head(20).reset_index()
        df_top.columns = ['entity','count']
        fig = px.bar(df_top, x='count', y='entity', orientation='h', title='Top entités — Forbes', height=600)
        st.plotly_chart(fig, use_container_width=True)
    if ents_oms is not None:
        df_top2 = ents_oms['entity'].value_counts().head(20).reset_index()
        df_top2.columns = ['entity','count']
        fig2 = px.bar(df_top2, x='count', y='entity', orientation='h', title='Top entités — OMS', height=600)
        st.plotly_chart(fig2, use_container_width=True)
    # NER distribution
    st.markdown("Distribution des types d'entités (ORG / PER / GPE / etc.)")
    if ents is not None and 'label' in ents.columns:
        st.write(ents['label'].value_counts())

# PAGE: Sentiment & Framing
if page == "Sentiment & Framing":
    st.header("Analyse du sentiment et des angles éditoriaux (framing)")
    if sent is None:
        st.info("Fichier de sentiment non disponible.")
    else:
        st.subheader("Répartition du sentiment par source")
        if main_df is not None:
            merged = sent.merge(main_df[['source']], left_on='global_index', right_index=True, how='left')
            fig = px.histogram(merged, x='label', color='source', barmode='group', title='Répartition du sentiment par source')
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig = px.histogram(sent, x='label', title='Répartition du sentiment (tous articles)')
            st.plotly_chart(fig, use_container_width=True)
    if fr is None:
        st.info("Fichier de framing non disponible.")
    else:
        st.subheader("Répartition des angles éditoriaux (Forbes)")
        counts = fr['framing'].value_counts().reset_index()
        counts.columns = ['framing','count']
        fig = px.pie(counts, names='framing', values='count', title='Répartition des angles (framing) dans les articles Forbes')
        st.plotly_chart(fig, use_container_width=True)
    # sentiment par thème (if mapping exists)
    if sim is not None and cov is not None:
        st.subheader("Sentiment moyen par thème (Forbes)")
        st.write("Cette section nécessite une table de mapping 'forbes article index' -> 'topic id'. Si disponible, elle sera utilisée.")

# PAGE: Export graphiques
if page == "Export graphiques":
    st.header("Exporter les graphiques en PNG pour le rapport")
    st.markdown("Les graphiques disponibles seront exportés dans `outputs/analysis_results/` avec des noms standardisés.")
    if st.button("Exporter tout (UMAP, coverage, entities, sentiment, framing)"):
        os.makedirs(RES_DIR, exist_ok=True)
        exported = []
        try:
            # UMAP
            if coords is not None:
                fig = px.scatter(coords, x='umap_x', y='umap_y', color='source', title='Projection UMAP — Visualisation des articles')
                out = os.path.join(RES_DIR, 'umap_sources.png'); fig.write_image(out); exported.append(out)
            if cov is not None:
                topic_cols = [c for c in cov.columns if c.startswith('covered_topic_')]
                cover_counts = cov[topic_cols].sum().reset_index(); cover_counts.columns=['metric','count']; cover_counts['topic']=cover_counts['metric'].str.replace('covered_topic_','').astype(int)
                fig2 = px.bar(cover_counts.sort_values('count',ascending=False), x='topic', y='count', title="Nombre d’articles Forbes couvrant chaque thème de l’OMS")
                out2 = os.path.join(RES_DIR, 'coverage_bar.png'); fig2.write_image(out2); exported.append(out2)
            if ents is not None:
                df_top = ents['entity'].value_counts().head(50).reset_index(); df_top.columns=['entity','count']
                fig3 = px.bar(df_top, x='count', y='entity', orientation='h', title='Top entités — Forbes')
                out3 = os.path.join(RES_DIR, 'top_entities_forbes.png'); fig3.write_image(out3); exported.append(out3)
            if ents_oms is not None:
                df_top2 = ents_oms['entity'].value_counts().head(50).reset_index(); df_top2.columns=['entity','count']
                fig4 = px.bar(df_top2, x='count', y='entity', orientation='h', title='Top entités — OMS')
                out4 = os.path.join(RES_DIR, 'top_entities_oms.png'); fig4.write_image(out4); exported.append(out4)
            if sent is not None:
                fig5 = px.histogram(sent, x='label', title='Répartition du sentiment (tous articles)')
                out5 = os.path.join(RES_DIR, 'sentiment_hist.png'); fig5.write_image(out5); exported.append(out5)
            st.success(f'Export terminé: {len(exported)} fichiers. Exemple: {exported[:3]}')
        except Exception as e:
            st.error("Erreur durant l'export: " + str(e))
            raise

st.markdown("---")

