import pandas as pd
import streamlit as st
import os
import numpy as np
import plotly.figure_factory as ff
import plotly.express as px
import seaborn as sb
import random
import matplotlib.pyplot as plt
import requests


# farei a extração de dados da bolsa de valores usando o Alpha 
# https://www.alphavantage.co
# chave API: F47ANAM7WG9WXWNK
# https://www.youtube.com/watch?v=cQazjgxDI_U
# farei primeiro um dashboard que trará o retorno contínuo das ações que eu selecionar e plotar um grafico de linhas 
# pensar em como fazer uma composição de carteiras usando teoria de carteiras de Markowitz
# fazer no streamlit


# dados API
ticker = 'PETR4.SA'
api_key = 'F47ANAM7WG9WXWNK'

url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={api_key}'
resposta = requests.get(url)
dados = resposta.json()
dados


# filtros data
data_i = '2010-02-05'
data_f = '2023-11-06'


df = pd.DataFrame.from_dict(dados, orient='index').reset_index() # o 'orient' garante que as chaves do dicionario sejam usadas como indices das linhas e os valores do dicionario serao os valores das coluans
df.columns = ['date','open','high','low','close','volume']
df = df.astype({'date':'datetime64[ns]'})
df = df.astype({'close':'float'})
df = df.loc[(df['date'] >= data_i) & (df['date'] <= data_f)]
print(df)