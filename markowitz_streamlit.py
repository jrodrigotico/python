import pandas as pd
import yfinance as yf
import pandas_datareader as pdr
import numpy as np
import matplotlib.pyplot as mplt
import seaborn as sn
import datetime
import streamlit as st
import os

# diretorio


# streamlit run markowitz_streamlit.py
yf.pdr_override() #corrige problemas da bibliotece do pandas_datareader

# tickers acoes existentes (o ideal seria fazer um web scrapping na B3 ou consumir uma api da B3, pq com um arquivo fica muito travado)
acoes = pd.read_excel(os.path.join('C:/Users/Computadores Gamer/OneDrive/Área de Trabalho/python/acoes_listas.xlsx'))['Código']


# pagina
st.set_page_config(page_title='Markowitz', layout='centered')
st.header('Risco de carteira de ações - Teoria de Carteira de Markowitz')


#### barra lateral
st.sidebar.header('Parâmetros')
selecionar_acoes = st.sidebar.multiselect('Selecione ações', sorted(acoes + '.SA'))


# parametros de data
st.sidebar.date_input('Data inicial', format='YYYY-MM-DD', value=None)
st.sidebar.date_input('Data final',  format='YYYY-MM-DD', value=None)

# data_i = '2020-01-01'
# data_f = '2023-01-01'



# definicao das datas e das acoes
# encontrar forma de deixar dinamico o numero de acoes e a peridiocidade do resample
# mudar o tipo de grafico de seaborn pq o streamlit nao aceita
# ibov = ['^BOVSP']
# acao_1 = ['ITUB3.SA']
# acao_2 = ['CSNA3.SA']
# acao_3 = ['VALE3.SA']
# acao_4 = ['PETR3.SA']
# st.set_option('deprecation.showPyplotGlobalUse', False)
# acoes = [acao_1, acao_2,acao_3, acao_4]

# tabela = pd.DataFrame()
# for i in acoes:
#     tabela[f'{i[0][:5]}'] = round(yf.download((i), start = data_i, end=data_f)['Adj Close'].resample('M').last(),4)
#     # print(tabela.head(5))

# mplt.figure(figsize=(10,10))
# mplt.plot(tabela)
# mplt.show()
# st.pyplot()