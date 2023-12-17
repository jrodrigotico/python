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
# fonte dos tickers e segmento = Economática 14/12/2023, a empresa Allos foi classificado como 'Outros' no Subsetor Bovespa


# ---------------- Arquivos ---------------- # 
# tickers acoes existentes (o ideal seria fazer um web scrapping na B3 ou consumir uma api da B3, pq com um arquivo fica muito travado)
# https://www.dadosdemercado.com.br/bolsa/acoes , att: Cotações atualizadas no fechamento de 24/11/2023.
yf.pdr_override() #corrige problemas da bibliotece do pandas_datareader
acoes = pd.read_csv('https://raw.githubusercontent.com/jrodrigotico/python/projeto_acoes/base_completa_acoes_subsetor.csv', sep=';')[['Código','Subsetor Bovespa']]
acoes = acoes[acoes['Código'].apply(lambda x: len(str(x))==5)]
# acoes = acoes.loc[(acoes['ticker_numero'] != 'CÓDIGO') & (acoes['LISTAGEM'].notna())].iloc[:,range(0,2)]


# ---------------- Inicial ---------------- # 
st.set_page_config(page_title='Markowitz', layout='centered')
st.header('Teoria Moderna de Portfólio - Markowitz')
st.write('---')


# ---------------- Barra lateral ---------------- # 
# parametros de data
st.sidebar.header('Parâmetros')
data_i = st.sidebar.date_input('Data inicial', format='YYYY-MM-DD', value=None)
data_i = pd.Timestamp(data_i)

data_f = st.sidebar.date_input('Data final',  format='YYYY-MM-DD', value=None)
data_f = pd.Timestamp(data_f)

# seleção de subsetor da empresa
subsetor = st.sidebar.multiselect('Selecione o subsetor', sorted(acoes['Subsetor Bovespa'].unique()))

# dados cdi (taxa livre de risco)
# DI - Depósito Interfinanceiro - Taxas - DI PRÉ - Over
# SELIC
# 16/01/2013 até 30/11/2023 , fonte B3
selic = pd.read_csv('https://raw.githubusercontent.com/jrodrigotico/python/projeto_acoes/selic.csv', sep=';')
# selecionar_cdi = st.sidebar.multiselect('Selecionar período CDI')
# filtro_cdi = cdi.loc[(cdi['Data']>=data_i) & (cdi['Data']=<data_f)]

# seleção de ações
# acoes filtradas pelo subsetor
filtro_subsetor = acoes.loc[acoes['Subsetor Bovespa'].isin(subsetor)].iloc[:,0] # esse iloc retorna as acoes de determinado subsetor que foi anteriormente selecionado, é zero pq o 0 representa a coluna de códigos que é o que eu desejo que retorne
selecionar_acoes = st.sidebar.multiselect('Selecione ações', sorted(filtro_subsetor + '.SA'))


# ---------------- Gráficos e tabelas de preços ---------------- # 
# grafico e tabela de 'Preço das ações'
st.set_option('deprecation.showPyplotGlobalUse', False)

# st.subheader('Preço das ações')
# tabela = pd.DataFrame() 
# for i in selecionar_acoes:
#     tabela[f'{i}'] = round(yf.download(i, start=data_i, end=data_f)['Adj Close'].resample('M').last(),2)
# st.write(tabela.head())

tabelas_acoes = []  
tabela_norm = pd.DataFrame()

if selecionar_acoes:
    for i in selecionar_acoes:
        tabela_acao = round(yf.download(i, start=data_i, end=data_f)["Adj Close"].rename(i),2)
        tabelas_acoes.append(tabela_acao)
    tabela = pd.concat(tabelas_acoes, axis=1)

    st.subheader('Preço das ações') # normalizado
    
    erro = None
    for i in tabela.columns:
        try:
            tabela_norm[i[:5]] = round(tabela[i] / tabela[i].iloc[0], 2)  # pega dado da tabela anterior
        except IndexError:
            st.write(f'Ação {i} não listada')

    # usar Comércio e 'RBNS11.SA' para fazer a exceção de erros, acoes com 6 digitos no ticker nao existe mais na bolsa

    # Plotar o gráfico com todas as ações selecionadas
    grafico2 = px.line(tabela_norm)
    grafico2.update_layout(width=800, height=500)
    st.plotly_chart(grafico2)

    # Retornos Contínuos e Matriz de Covariância
    # ln(retorno_t / retorno_t-1)
    st.header('Médias dos retornos de cada ação:')
    tabela_retorn = tabela_norm.pct_change().dropna()
    media_retor = tabela_retorn.mean()
    for i in range(len(media_retor)):
        st.write(selecionar_acoes[i], round(media_retor[i],4))

    matriz_cov = tabela_retorn.cov() # para o modelo de markowitz é bom ter acoes com alta correlação negativa ! ver video: https://www.youtube.com/watch?v=Y1E73SQPD1U
    st.header('Matriz de covariância:')
    heatmap_retorn = px.imshow(matriz_cov, text_auto=True)
    st.plotly_chart(heatmap_retorn)
else:
    st.write('Selecione os parâmetros na barra lateral')


# ---------------- Simulação ---------------- #

# selic (taxa livre de risco)
selic['Data'] = pd.to_datetime(selic['Data']).dt.tz_localize(None)
selic = selic.loc[(selic['Data']>= data_i) & (selic['Data']<= data_f)]

numero_portfolios = st.sidebar.number_input('Insira o número de portfolios')

def parametros_portofolio (numero_portfolios):
        
    tabela_retorn_esperados = np.zeros(numero_portfolios)
    tabela_volatilidades_esperadas = np.zeros(numero_portfolios)
    tabela_sharpe = np.zeros(numero_portfolios)
    tabela_pesos = np.zeros((numero_portfolios, len(selecionar_acoes)))
    tabela_retorn_esperados_aritm = np.zeros(numero_portfolios)
    
    for i in range(numero_portfolios):
        pesos_random = np.random.random(len(selecionar_acoes))
        pesos_random /= np.sum(pesos_random)
        tabela_pesos[i,:] = pesos_random
        tabela_retorn_esperados[i] = np.sum(media_retor * pesos_random * 252)
        tabela_retorn_esperados_aritm[i] = np.exp(tabela_retorn_esperados[i])-1
        tabela_volatilidades_esperadas[i] =  np.sqrt(np.dot(pesos_random.T, np.dot(matriz_cov * 252, pesos_random)))
        tabela_sharpe[i] = tabela_retorn_esperados[i] / tabela_volatilidades_esperadas[i]
        
    indice_sharpe_max = tabela_sharpe.argmax()
    carteira_max_retorno = tabela_pesos[indice_sharpe_max]
        
    st.header('Pesos da carteira ideal:')
    for z in range(len(selecionar_acoes)):
        st.write(selecionar_acoes[z], round(carteira_max_retorno[z],4))
        
    # restrições PPL para curva de fronteira eficiente
    def pegando_retorno (peso_teste):
        peso_teste = np.array(peso_teste)
        retorno = np.sum(media_retor * peso_teste) * 252
        retorno = np.exp(retorno) - 1 # aqui estou passando os retornos para aritmeticos
        return retorno
    
    def checando_soma_pesos(peso_teste):
        return np.sum(peso_teste)-1
    
    def pegando_vol(peso_teste):
        peso_teste = np.array(peso_teste)
        vol = np.sqrt(np.dot(peso_teste.T, np.dot(matriz_cov * 252, peso_teste)))
        return vol
    
    peso_inicial = [1/len(selecionar_acoes)] * len(selecionar_acoes)  # pesos iguais para todas as acoes
    limites = tuple([(0,1) for i in selecionar_acoes])   # aqui nenhuma acao pode ter mais que 100%
    
    eixo_x_fronteira_eficiente = []
    fronteira_eficiente_y = np.linspace(tabela_retorn_esperados_aritm.min(), tabela_retorn_esperados_aritm.max(), 50 ) 

    # fronteira eficiente com as restrições
    for retorno_possivel in fronteira_eficiente_y:
        restricoes = ({'type':'eq', 'fun':checando_soma_pesos}, {'type':'eq', 'fun' : lambda weight: pegando_retorno(weight) - retorno_possivel}) # é um dicionario de restricoes, quando a igualdade ('eq') for zero é pq a restricao fo satisfeita
        
        result = minimize(pegando_vol, peso_inicial, method='SLSQP', bounds = limites, constraints = restricoes)
        eixo_x_fronteira_eficiente.append(result['fun'])

    st.header(f'Gráfico com a simulação de {numero_portfolios} carteiras: ')   
    # fig, ax = mplt.subplots()
    # ax.scatter(tabela_volatilidades_esperadas, tabela_retorn_esperados_aritm, c=tabela_sharpe)
    # ax.scatter(tabela_volatilidades_esperadas[indice_sharpe_max], tabela_retorn_esperados_aritm[indice_sharpe_max], c = 'red')
    # ax.plot(eixo_x_fronteira_eficiente, fronteira_eficiente_y)
    # st.pyplot(fig)
    
    # grafico interativo com a fronteira eficiente
    carteiras_simulacao = go.Scatter(x=tabela_volatilidades_esperadas,y=tabela_retorn_esperados_aritm,mode='markers',
        marker=dict(size=8, color=tabela_sharpe, colorscale='Viridis'), name = 'Carteiras simuladas')

    carteira_max_retorno = go.Scatter(x=[tabela_volatilidades_esperadas[indice_sharpe_max]], y=[tabela_retorn_esperados_aritm[indice_sharpe_max]],
        mode='markers', marker= dict(size=12, color='red'), name = 'Carteira com o melhor Índice de Sharpe')

    # linha_eficiencia = go.Scatter(x=eixo_x_fronteira_eficiente, y=fronteira_eficiente_y, mode='lines', name = 'Fronteira eficiente')

    layout = go.Layout(xaxis= dict(title='Risco esperado'), yaxis= dict(title='Retorno esperado'))

    # data = [carteiras_simulacao, carteira_max_retorno, linha_eficiencia]
    pontos_dispersao = [carteiras_simulacao, carteira_max_retorno]
    fig = go.Figure(data=pontos_dispersao, layout=layout)
    st.plotly_chart(fig)


if st.sidebar.button('Run'):
    parametros_portofolio (int(numero_portfolios))














# if st.sidebar.button('Gerar gráfico'):
#     fig, ax = mplt.subplots()
#     ax.scatter(tabela_volatilidades_esperadas, tabela_retorn_esperados, c=tabela_sharpe)
#     ax.scatter(tabela_volatilidades_esperadas[indice_sharpe_max], tabela_retorn_esperados[indice_sharpe_max], c = 'red')
#     ax.plot(eixo_x_fronteira, fronteira_eficiente_y)

#     mplt.show()

