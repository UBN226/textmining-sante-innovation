import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import seaborn as sns
import matplotlib.pyplot as plt

st.title("🔗 Similarité OMS ↔ Forbes")

oms_df = pd.read_csv("data/oms.csv")
forbes_df = pd.read_csv("data/forbes.csv")

corpus = list(oms_df['text']) + list(forbes_df['text'])
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(corpus)

sim_matrix = cosine_similarity(tfidf_matrix)
plt.figure(figsize=(8,6))
sns.heatmap(sim_matrix[:len(oms_df), len(oms_df):], annot=False)
st.pyplot(plt)
