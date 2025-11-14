import streamlit as st
import pandas as pd
from textblob import TextBlob
import altair as alt

st.title("📊 Polarité du Discours")

# Charger les données
oms_df = pd.read_csv("data/oms.csv")
forbes_df = pd.read_csv("data/forbes.csv")

# Fonction sentiment
def get_sentiment(text):
    return TextBlob(str(text)).sentiment.polarity

oms_df['polarity'] = oms_df['text'].apply(get_sentiment)
forbes_df['polarity'] = forbes_df['text'].apply(get_sentiment)

# Combiner
df = pd.concat([oms_df.assign(source="OMS"), forbes_df.assign(source="Forbes")])

# Barplot polarité moyenne
chart = alt.Chart(df).mark_bar().encode(
    x='source:N',
    y='polarity:Q',
    color='source:N'
)
st.altair_chart(chart, use_container_width=True)
