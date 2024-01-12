import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard Acidentes",layout="wide")
st.title("Acidentes Recife 2022 - Prefeitura Municipal de Recife")

with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)


st.sidebar.image("data/logo1.png",caption="")

st.sidebar.header("Filtros")

df = pd.read_csv("acidentes2022.csv", sep=';')
df = df.drop(columns=['hora', 'numero','detalhe_endereco_acidente','complemento', 'num_semaforo', 'sentido_via','velocidade_max_via', 'divisao_via1', 'divisao_via2', 'divisao_via3' ])

colunas_drop = ['vitimasfatais', 'auto', 'moto', 'ciclom', 'ciclista', 'pedestre', 'onibus', 'caminhao', 'viatura', 'outros', 'vitimas']
for coluna in colunas_drop:
    df[coluna] = df[coluna].str.split(',').str[0].astype(int)

soma_vitimasfatais = df['vitimasfatais'].sum()
soma_auto = df['auto'].sum()
soma_moto = df['moto'].sum()
soma_ciclom = df['ciclom'].sum()
soma_ciclista = df['ciclista'].sum()
soma_pedestre = df['pedestre'].sum()
soma_onibus = df['onibus'].sum()
soma_caminhao = df['caminhao'].sum()
soma_viatura = df['viatura'].sum()
soma_outros = df['outros'].sum()

st.subheader('Em :blue[2022], na cidade do Recife, a quantidade total de veículos envolvidos em acidentes se distribui da seguinte forma:')

col1, col2, col3, col4 = st.columns(4, gap="small")
with col1:
    st.metric(label="Carros", value=soma_auto)

with col2:
    st.metric(label="Motos", value=soma_moto)

with col3:
    st.metric(label="Onibus", value=soma_onibus)

with col4:
    st.metric(label="Viaturas", value=soma_viatura)
    
col5, col6, col7, col8 = st.columns(4, gap="small")
with col5:
    st.metric(label="Ciclistas", value=soma_ciclista)

with col6:
    st.metric(label="Caminhão", value=soma_caminhao)

with col7:
    st.metric(label="Ciclomotores", value=soma_ciclom)

with col8:
    st.metric(label="Outros", value=soma_outros)

st.markdown(f"<h4>Além dos <span style='font-size:1.5em;'>{soma_pedestre}</span> pedestres que também se envolveram em acidentes em 2022 no Recife.</h4>", unsafe_allow_html=True)

df['data'] = pd.to_datetime(df['data'])
df['mes'] = df['data'].dt.month_name()
nomes_mes = {"January": "Janeiro","February": "Fevereiro","March": "Março","April": "Abril","May": "Maio","June": "Junho","July": "Julho","August": "Agosto","September": "Setembro","October": "Outubro","November": "Novembro","December": "Dezembro"}
df['mes'] = df['mes'].apply(lambda mes: nomes_mes[mes])
meses_ordem = pd.CategoricalDtype(categories=['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'], ordered=True)
df['mes'] = df['mes'].astype(meses_ordem)
df = df.sort_values(by='mes')
acidentes_por_mes = df['mes'].value_counts().sort_index()
media_acidentes_por_mes = acidentes_por_mes.rolling(window=2).mean()
fig = px.line(x=acidentes_por_mes.index, y=acidentes_por_mes.values, labels={'x': '', 'y': ''}, title='Evolução Mensal dos Acidentes de Trânsito em 2022', color_discrete_sequence=px.colors.sequential.Blues_r)
fig.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False,showticklabels=False))
fig.add_trace(go.Scatter(x=acidentes_por_mes.index, y=media_acidentes_por_mes.values,
                         mode='lines', name='Média móvel(2 meses)', line=dict(color='red', dash='dash')))
st.plotly_chart(fig, use_container_width=True, theme="streamlit")  



