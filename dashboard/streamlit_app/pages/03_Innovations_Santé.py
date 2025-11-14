import streamlit as st
import pandas as pd
import plotly.express as px

st.title("💡 Innovations Santé")

innov_df = pd.read_csv("data/innovations.csv")

st.subheader("Nombre d'innovations par pays")
fig = px.bar(innov_df, x="pays", y="nombre", color="pays")
st.plotly_chart(fig, use_container_width=True)
