# app.py
import streamlit as st

st.set_page_config(
    page_title="Observatoire Text Mining OMS vs Forbes",
    layout="wide",
    page_icon="📊"
)

# 🎨 Styles supplémentaires
st.markdown("""
<style>
.big-title {
    font-size:42px !important;
    color: #2E86C1;
    font-weight: bold;
}
.sub-title {
    font-size:22px !important;
    color: #34495E;
}
.card {
    background-color: #FDFEFE;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# 🎉 Titre principal
st.markdown('<div class="big-title">📊 Observatoire Textuel OMS vs Forbes Afrique</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Analyse interactive des discours médiatiques et innovations en santé</div>', unsafe_allow_html=True)
st.markdown("---")

# 📊 Statistiques clés avec colonnes
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="card"><h3>📄 Articles OMS</h3><p style="font-size:28px; color:#2E86C1;">120</p></div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card"><h3>📰 Articles Forbes</h3><p style="font-size:28px; color:#D35400;">80</p></div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="card"><h3>💡 Innovations Identifiées</h3><p style="font-size:28px; color:#27AE60;">45</p></div>', unsafe_allow_html=True)

st.markdown("---")

# 🌟 Présentation
st.markdown("""
Bienvenue dans ce tableau de bord interactif sur la santé et l'innovation en Afrique.  
Utilisez le menu latéral pour naviguer entre les différentes analyses : **Lexique comparé**, **Polarité du discours**, **Innovations santé**, **Similarité OMS ↔ Forbes**, et **Résumé global**.

Vous découvrirez :
- Les différences de vocabulaire entre OMS et Forbes.
- Les sentiments exprimés dans les articles.
- Les innovations santé par pays et secteur.
- La proximité entre les discours OMS et Forbes.
""")

# 🎨 Animation légère
st.balloons()

# Navigation
page = st.sidebar.selectbox(
    "Navigation",
    ["Accueil", 
     "Lexique Comparé", 
     "Polarité du Discours", 
     "Innovations Santé", 
     "Similarité OMS ↔ Forbes", 
     "Résumé Global"]
)

if page == "Accueil":
    st.header("🏠 Accueil")
    st.success("Choisissez une section dans le menu latéral pour explorer les données.")
