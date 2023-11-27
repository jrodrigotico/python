import pandas as pd
import yfinance as yf
import pandas_datareader as pdr
import numpy as np
import matplotlib.pyplot as mplt
import seaborn as sn
import datetime
import streamlit as st

# streamlit run markowitz_streamlit.py

# pagina
st.set_page_config(page_title='Markowitz', layout='centered')
st.header('Risco de carteira de ações - Teoria de Carteira de Markowitz')

yf.pdr_override() #corrige problemas da bibliotece do pandas_datareader

# definicao das datas e das acoes
# encontrar forma de deixar dinamico o numero de acoes e a peridiocidade do resample
# mudar o tipo de grafico de seaborn pq o streamlit nao aceita
data_i = '2020-01-01'
data_f = '2023-01-01'
ibov = ['^BOVSP']
acao_1 = ['ITUB3.SA']
acao_2 = ['CSNA3.SA']
acao_3 = ['VALE3.SA']
acao_4 = ['PETR3.SA']

acoes = [acao_1, acao_2,acao_3, acao_4]

tabela = pd.DataFrame()
for i in acoes:
    tabela[f'{i[0][:5]}'] = round(yf.download((i), start = data_i, end=data_f)['Adj Close'].resample('M').last(),4)
    # print(tabela.head(5))

mplt.figure(figsize=(8,8))
mplt.plot(tabela)
mplt.show()
st.pyplot()