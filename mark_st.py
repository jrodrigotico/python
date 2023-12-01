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
# st.write(selecionar_acoes)


# ---------------- Gráficos e tabelas de preços ---------------- # 
# grafico e tabela de 'Preço das ações'
st.set_option('deprecation.showPyplotGlobalUse', False)

# st.subheader('Preço das ações')
tabela = pd.DataFrame()
for i in selecionar_acoes:
    tabela[f'{i}'] = round(yf.download(i, start=data_i, end=data_f)['Adj Close'].resample('M').last(),2)
# st.write(tabela.head())

# grafico = px.line(tabela)
# grafico.update_layout(width=800, height=300)
# st.plotly_chart(grafico)


# grafico e tabela de 'Preço das ações normalizado' 
st.subheader('Preço das ações normalizado')
tabela_norm = pd.DataFrame()
for i in tabela.columns:
    tabela_norm[f'{i}_normal'] = round(tabela[i] / tabela[i].iloc[0],2) # pega dado da tabela anterior
# st.write(tabela_norm.head())
    
grafico2 = px.line(tabela_norm)
grafico2.update_layout(width=800, height=800)
st.plotly_chart(grafico2)


# ---------------- Retornos Contínuos e Matriz de Covariância ---------------- #
# ln(retorno_t / retorno_t-1)
tabela_retorn = tabela_norm.pct_change().dropna()
media_retor = tabela_retorn.mean()
media_retor.columns = ['Média dos retornos contínuos']
matriz_cov = tabela_retorn.cov() # para o modelo de markowitz é bom ter acoes com alta correlação negativa ! ver video: https://www.youtube.com/watch?v=Y1E73SQPD1U
st.write(media_retor)

heatmap_retorn = px.imshow(matriz_cov, text_auto=True)
st.plotly_chart(heatmap_retorn)

# grafico3 = px.line(tabela_norm)
# grafico3.update_layout(width=800, height=300)
# st.plotly_chart(grafico3)


# ---------------- Simulação ---------------- #
numero_portfolios = st.sidebar.number_input('Insira o número de portfolios')

def parametros_portofolio (numero_portfolios):
    
    tabela_retorn_esperados = np.zeros(numero_portfolios)
    tabela_volatilidades_esperadas = np.zeros(numero_portfolios)
    tabela_sharpe = np.zeros(numero_portfolios)
    tabela_pesos = np.zeros((numero_portfolios, len(selecionar_acoes)))
    
    for i in range(numero_portfolios):
        pesos_random = np.random.random(len(selecionar_acoes))
        pesos_random /= np.sum(pesos_random)
        tabela_pesos[i,:] = pesos_random
        tabela_retorn_esperados[i] = np.sum(media_retor * pesos_random * 252)
        tabela_volatilidades_esperadas[i] =  np.sqrt(np.dot(pesos_random.T, np.dot(matriz_cov * 252, pesos_random)))
        tabela_sharpe[i] = tabela_retorn_esperados[i] / tabela_volatilidades_esperadas[i]
        
    indice_sharpe_max = tabela_sharpe.argmax()
    carteira_max_retorno = tabela_pesos[indice_sharpe_max]
    st.write(carteira_max_retorno)
 


if st.sidebar.button('Run'):
    parametros_portofolio (int(numero_portfolios))



# ---------------- Restrições e fronteira eficiente ---------------- #


    







# if st.sidebar.button('Gerar gráfico'):
#     fig, ax = mplt.subplots()
#     ax.scatter(tabela_volatilidades_esperadas, tabela_retorn_esperados, c=tabela_sharpe)
#     ax.scatter(tabela_volatilidades_esperadas[indice_sharpe_max], tabela_retorn_esperados[indice_sharpe_max], c = 'red')
#     ax.plot(eixo_x_fronteira, fronteira_eficiente_y)

#     mplt.show()
