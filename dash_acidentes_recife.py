import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import json

st.set_page_config(page_title="Dashboard Acidentes",layout="wide")
#st.image("data/logo1.png",caption="")
st.title("Acidentes Recife - Prefeitura Municipal de Recife")

with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)


st.sidebar.image("data/logo1.png",caption="")

st.sidebar.header("Filtros")

@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path, sep=';')

df_2021 = load_data("data/acidentes2021.csv")
df_2022 = load_data("data/acidentes2022.csv")

df_2021.rename(columns={'natureza_acidente':'natureza'}, inplace = True)


colunas_conv = ['vitimasfatais', 'auto', 'moto', 'ciclom', 'ciclista', 'pedestre', 'onibus', 'caminhao', 'viatura', 'outros', 'vitimas']
for coluna in colunas_conv:
    df_2022[coluna] = df_2022[coluna].str.split(',').str[0].astype(int)
    df_2021[coluna] = df_2021[coluna].fillna(0)

#df = pd.read_csv("data/acidentes2022.csv", sep=';')
df = pd.concat([df_2021, df_2022])

df['data'] = pd.to_datetime(df['data'])
df['mes'] = df['data'].dt.month_name()
df['ano'] = df['data'].dt.year
#st.dataframe(df)
nomes_mes = {"January": "Janeiro","February": "Fevereiro","March": "Março","April": "Abril","May": "Maio","June": "Junho","July": "Julho","August": "Agosto","September": "Setembro","October": "Outubro","November": "Novembro","December": "Dezembro"}
df['mes'] = df['mes'].apply(lambda mes: nomes_mes[mes])
meses_ordem = pd.CategoricalDtype(categories=['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'], ordered=True)
df['mes'] = df['mes'].astype(meses_ordem)
df['mes_num'] = df['data'].dt.month
meses_dict = {1: 'Janeiro',2: 'Fevereiro',3: 'Março',4: 'Abril',5: 'Maio',6: 'Junho',7: 'Julho',8: 'Agosto',9: 'Setembro',10: 'Outubro',11: 'Novembro',12: 'Dezembro'}

categorias = list(df['natureza'].unique())
categorias.append('TODAS')
default_index = categorias.index('TODAS')
categoria = st.sidebar.selectbox('Selecione a natureza do acidente', options = categorias,index=default_index, placeholder="Selecione uma opção:")


if categoria == 'TODAS':
    df = df
else:
    df = df[df['natureza'] == categoria]

anos = list(df['ano'].unique())
anos.append('TODOS ANOS')
default_index_1 = anos.index('TODOS ANOS')
ano = st.sidebar.selectbox('Selecione o ano', options = anos,index=default_index_1, placeholder="Selecione uma opção:")


if ano == 'TODOS ANOS':
    df = df
else:
    df = df[df['ano'] == ano]

selected_range = st.sidebar.select_slider('Selecione um intervalo de meses', options=range(1, 13),value=(1, 12),format_func=lambda x: meses_dict[x])

df = df[(df['mes_num'] >= selected_range[0]) & (df['mes_num'] <= selected_range[1])]

df = df.drop(columns=['hora', 'numero','detalhe_endereco_acidente','complemento', 'num_semaforo', 'sentido_via','velocidade_max_via', 'divisao_via1', 'divisao_via2', 'divisao_via3' ])

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

if categoria == 'COM VÍTIMA':
    df = df[df['natureza'] == 'COM VÍTIMA']

st.subheader(f'Em :blue[{ano}], na cidade do Recife, a quantidade total de veículos envolvidos em acidentes se distribui da seguinte forma:')

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

#Tratamento de dados para o gráfico de Linha

df = df.sort_values(by='mes')
acidentes_por_mes = df.groupby(['mes', 'ano']).size().reset_index(name='quantidade')
acidentes_por_mes['media_movel'] = acidentes_por_mes['quantidade'].rolling(window=2).mean()

#Tratamento de dados para o gráfico Treemap
index_null_tempo = list(df[df['tempo_clima'].isnull()].index)

for index in index_null_tempo:
    date_tempo = df.loc[index, 'data']
    aux_df = df[df['data'].astype(str) == str(date_tempo)].reset_index(drop=True)
    value_mode = aux_df['tempo_clima'].mode()
    
    if len(value_mode) > 0:
        df.loc[index, 'tempo_clima'] = value_mode.iloc[0]

# Preencher valores nulos restantes com "Não especificado"
df['tempo_clima'].fillna("Não especificado", inplace=True)

# Agrupar por 'tempo_clima' e somar 'vitimas'
if categoria == 'VÍTIMA FATAL':
    acidentes_por_clima = df.groupby('tempo_clima')['vitimasfatais'].sum().reset_index()
else:
    acidentes_por_clima = df.groupby('tempo_clima')['vitimas'].sum().reset_index()


#Tratamento de dados para o gráfico de barra Dia útil/FDS
df['dia_da_semana'] = df['data'].dt.day_name()
def classificar_dia(dia):
    if dia in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
        return 'Dia Útil'
    else:
        return 'Final de Semana'
df['tipo_dia'] = df['dia_da_semana'].apply(classificar_dia)
quantidade_acidentes_por_tipo_dia = df['tipo_dia'].value_counts()

#Tratamento de dados para gráfico de mapa
local_path = 'data/bairros.geojson'
with open(local_path, 'r', encoding='utf-8') as file:
    state_geo = json.load(file)
if categoria == 'VÍTIMA FATAL':
    acidentes_por_bairro = df.groupby('bairro')['vitimasfatais'].count()
else:
    acidentes_por_bairro = df.groupby('bairro')['vitimas'].count()
acidentes_por_bairro = acidentes_por_bairro.reset_index()

#Tratamento de dados para gráfico barra - tipo de acidentes
if categoria == 'VÍTIMA FATAL':
    tipo_acidente = df.groupby('tipo')['vitimasfatais'].sum()
else:
    tipo_acidente = df.groupby('tipo')['vitimas'].sum()
    tipo_acidente = tipo_acidente[tipo_acidente > 10]
tipo_acidente = tipo_acidente.sort_values(ascending=True)

#tratamento de dados para gráfico quantidade de vitimas
vitimas = df.groupby('natureza')['vitimas'].sum()
vitimas = vitimas.sort_values(ascending=False)

col9, col10 = st.columns(2, gap="small")
with col9:
    if categoria == 'VÍTIMA FATAL':
        fig_clima = px.treemap(acidentes_por_clima, path=['tempo_clima'], values="vitimasfatais", color_discrete_sequence=px.colors.sequential.Blues_r, title='Considerando o clima no momento do acidente temos a seguinte distribuição:')
    else:
        fig_clima = px.treemap(acidentes_por_clima, path=['tempo_clima'], values="vitimas", color_discrete_sequence=px.colors.sequential.Blues_r, title='Considerando o clima no momento do acidente temos a seguinte distribuição:')

    st.plotly_chart(fig_clima, use_container_width=True, theme="streamlit") 
    

with col10:
    fig_dia = px.bar(x=quantidade_acidentes_por_tipo_dia.index, y=quantidade_acidentes_por_tipo_dia.values, labels={'x': '', 'y': ''}, title='Quantidade de Acidentes por Tipo de Dia')
    fig_dia.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False,showticklabels=False))
    st.plotly_chart(fig_dia, use_container_width=True, theme="streamlit") 

with st.container():
    fig = px.line(acidentes_por_mes, x='mes', y='quantidade', color='ano', labels={'x': '', 'y': ''}, title='Evolução Mensal dos Acidentes de Trânsito em 2022', color_discrete_sequence=px.colors.sequential.Blues_r)
    fig.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False,showticklabels=False))
    fig.add_trace(go.Scatter(x=acidentes_por_mes['mes'], y=acidentes_por_mes['media_movel'], mode='lines', name='Média móvel(2 meses)', line=dict(color='red', dash='dash')))
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")  

col11, col12 = st.columns(2, gap="small")
with col11:
    fig_tipo = px.bar(tipo_acidente, x=tipo_acidente, labels={'x': '', 'y': ''},title='Vítimas por Tipo de Acidente', color_discrete_sequence=px.colors.sequential.Blues_r)
    fig_tipo.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    st.plotly_chart(fig_tipo, use_container_width=True, theme="streamlit") 
    

with col12:
    if categoria == 'VÍTIMA FATAL':
        fig_mapa = px.choropleth(acidentes_por_bairro, geojson=state_geo, color="vitimasfatais", locations="bairro", featureidkey="properties.EBAIRRNOME", projection="mercator")
    else:
        fig_mapa = px.choropleth(acidentes_por_bairro, geojson=state_geo, color="vitimas", locations="bairro", featureidkey="properties.EBAIRRNOME", projection="mercator")
    fig_mapa.update_geos(fitbounds="geojson", visible=False)
    fig_mapa.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, title_text = 'Acidentes por Bairro')
    st.plotly_chart(fig_mapa, use_container_width=True, theme="streamlit") 

# with st.container():
#     nomes_dias = {"Monday": "Segunda", "Tuesday": "Terça", "Wednesday": "Quarta", "Thursday": "Quinta", "Friday": "Sexta", "Saturday": "Sábado", "Sunday": "Domingo"}
#     df['dia_da_semana'] = df['dia_da_semana'].map(nomes_dias)
#     ordenacao = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
#     dados_agrupados = df.groupby(['ano', 'dia_da_semana']).size().reset_index(name='quantidade')
#     fig_dia_semana = px.bar(dados_agrupados, x='dia_da_semana', y='quantidade', color='ano', title="Acidentes por dia da semana", color_discrete_sequence=px.colors.sequential.Blues_r, category_orders={'dia_da_semana': ordenacao})
#     fig_dia_semana.update_layout(xaxis=dict(title='', showgrid=False),yaxis=dict(title='', showgrid=False), barmode = 'group')
#     st.plotly_chart(fig_dia_semana, use_container_width=True, theme="streamlit")
