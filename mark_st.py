import pandas as pd
import yfinance as yf
import pandas_datareader as pdr
import numpy as np
import matplotlib.pyplot as mplt
import seaborn as sn
import datetime
import streamlit as st
import os
import plotly.express as px
import plotly.colors as pcolors
import plotly.graph_objects as go
from scipy.optimize import minimize

# ---------------- Anotações ---------------- # 
# arrumar datas nas tabelas
# ver se consegue tirar o 'empty' da tabela
# streamlit run mark_st.py
# https://www.youtube.com/watch?v=Y1E73SQPD1U
# https://www.youtube.com/watch?v=BchQuTJvRAs
# https://www.linkedin.com/pulse/modern-portfolio-theory-python-building-optimal-web-app-phuaphan-oyhhc/
# https://modern-portfolio-theory.streamlit.app

# ---------------- Arquivos ---------------- # 
# tickers acoes existentes (o ideal seria fazer um web scrapping na B3 ou consumir uma api da B3, pq com um arquivo fica muito travado)
# https://www.dadosdemercado.com.br/bolsa/acoes , att: Cotações atualizadas no fechamento de 24/11/2023.
yf.pdr_override() #corrige problemas da bibliotece do pandas_datareader
acoes = pd.read_excel(os.path.join('C:/Users/Computadores Gamer/OneDrive/Área de Trabalho/python/acoes_listas.xlsx'))['Código']


# ---------------- Inicial ---------------- # 
st.set_page_config(page_title='Markowitz', layout='centered')
st.header('Teoria Moderna de Portfólio - Markowitz')
st.write('---')


# ---------------- Barra lateral ---------------- # 
# parametros de data
st.sidebar.header('Parâmetros')
data_i = st.sidebar.date_input('Data inicial', format='YYYY-MM-DD', value=None)
data_f = st.sidebar.date_input('Data final',  format='YYYY-MM-DD', value=None)

# seleção de ações
selecionar_acoes = st.sidebar.multiselect('Selecione ações', sorted(acoes + '.SA'))


# ---------------- Gráficos e tabelas de preços ---------------- # 
# grafico e tabela de 'Preço das ações'
st.set_option('deprecation.showPyplotGlobalUse', False)

st.subheader('Preço das ações')
tabela = pd.DataFrame()
for i in selecionar_acoes:
    tabela[f'{i}'] = round(yf.download(i, start=data_i, end=data_f)['Adj Close'].resample('M').last(),2)
# st.write(tabela.head())

grafico = px.line(tabela)
grafico.update_layout(width=800, height=300)
st.plotly_chart(grafico)


# grafico e tabela de 'Preço das ações normalizado' 
st.subheader('Preço das ações normalizado')
tabela_norm = pd.DataFrame()
for i in tabela.columns:
    tabela_norm[f'{i}_normal'] = round(tabela[i] / tabela[i].iloc[0],2) # pega dado da tabela anterior
# st.write(tabela_norm.head())
    
grafico2 = px.line(tabela_norm)
grafico2.update_layout(width=800, height=300)
st.plotly_chart(grafico2)


# ---------------- Retornos Contínuos e Matriz de Covariância ---------------- #
# ln(retorno_t / retorno_t-1)
tabela_retorn = tabela_norm.pct_change().dropna()
media_retor = tabela_retorn.mean()
media_retor.columns = ['Média dos retornos contínuos']
cov_retor = tabela_retorn.cov() # para o modelo de markowitz é bom ter acoes com alta correlação negativa ! ver video: https://www.youtube.com/watch?v=Y1E73SQPD1U
st.write(media_retor)

heatmap_retorn = px.imshow(cov_retor, text_auto=True)
st.plotly_chart(heatmap_retorn)

# grafico3 = px.line(tabela_norm)
# grafico3.update_layout(width=800, height=300)
# st.plotly_chart(grafico3)



# ---------------- Simulação ---------------- #
numero_portfolios = 1000
tabela_retorn_esperados = np.zeros(numero_portfolios)







