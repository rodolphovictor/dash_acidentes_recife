import streamlit as st
import pandas as pd
import plotly.express as px

df = pd.read_csv("acidentes2022.csv", sep=';')

st.set_page_config(page_title="Dashboard Acidentes",layout="wide")
st.subheader("Acidentes Recife 2022 - Prefeitura Municipal de Recife")

with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)


st.sidebar.image("data/logo1.png",caption="SEGD")

st.sidebar.header("Filtros")


