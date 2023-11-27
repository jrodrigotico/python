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

# diretorio


# streamlit run markowitz_streamlit.py
yf.pdr_override() #corrige problemas da bibliotece do pandas_datareader

# tickers acoes existentes (o ideal seria fazer um web scrapping na B3 ou consumir uma api da B3, pq com um arquivo fica muito travado)
# https://www.dadosdemercado.com.br/bolsa/acoes , att: Cotações atualizadas no fechamento de 24/11/2023.
acoes = pd.read_excel(os.path.join('C:/Users/Computadores Gamer/OneDrive/Área de Trabalho/python/acoes_listas.xlsx'))['Código']


# pagina
st.set_page_config(page_title='Markowitz', layout='centered')
st.header('Risco de carteira de ações - Teoria de Carteira de Markowitz')


#### barra lateral
st.sidebar.header('Parâmetros')
selecionar_acoes = st.sidebar.multiselect('Selecione ações', sorted(acoes + '.SA'))


# parametros de data
data_i = st.sidebar.date_input('Data inicial', format='YYYY-MM-DD', value=None)
data_f = st.sidebar.date_input('Data final',  format='YYYY-MM-DD', value=None)


# definicao das datas e das acoes
# encontrar forma de deixar dinamico o numero de acoes e a peridiocidade do resample
st.set_option('deprecation.showPyplotGlobalUse', False)

tabela = pd.DataFrame()
for i in selecionar_acoes:
    tabela_acao = yf.download(i, start=data_i, end=data_f)['Adj Close'].resample('M').last()
    tabela = pd.concat([tabela, tabela_acao], axis=1) # por coluna

mplt.figure(figsize=(10,10))
mplt.plot(tabela)
mplt.show()
st.pyplot()