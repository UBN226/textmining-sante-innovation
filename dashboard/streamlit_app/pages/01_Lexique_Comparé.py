import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.title("📖 Lexique Comparé OMS vs Forbes")

# Charger les données
oms_df = pd.read_csv("data/oms.csv")
forbes_df = pd.read_csv("data/forbes.csv")

st.subheader("Nuages de mots")
col1, col2 = st.columns(2)

with col1:
    st.write("OMS")
    text_oms = " ".join(oms_df['text'].astype(str))
    wc_oms = WordCloud(width=400, height=300).generate(text_oms)
    plt.imshow(wc_oms, interpolation="bilinear")
    plt.axis("off")
    st.pyplot(plt)

with col2:
    st.write("Forbes")
    text_forbes = " ".join(forbes_df['text'].astype(str))
    wc_forbes = WordCloud(width=400, height=300).generate(text_forbes)
    plt.imshow(wc_forbes, interpolation="bilinear")
    plt.axis("off")
    st.pyplot(plt)
