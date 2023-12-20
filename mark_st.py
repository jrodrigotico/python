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
import warnings


# ---------------- Anotações ---------------- # 
# arrumar datas nas tabelas
# ver se consegue tirar o 'empty' da tabela
# streamlit run mark_st.py
# https://www.youtube.com/watch?v=Y1E73SQPD1U
# https://www.youtube.com/watch?v=BchQuTJvRAs
# https://www.linkedin.com/pulse/modern-portfolio-theory-python-building-optimal-web-app-phuaphan-oyhhc/
# https://modern-portfolio-theory.streamlit.app
# https://analisemacro.com.br/mercado-financeiro/selecao-de-carteira-e-teoria-de-markowitz/ - riskfolio
# https://medium.com/@rodrigobercinimartins/como-extrair-dados-da-bovespa-sem-gastar-nada-com-python-14a03454a720 - yahoo query
# https://www.youtube.com/watch?v=rxWkIn1EZnM&t=236s - pie chart streamlit
# fonte dos tickers e segmento = Economática 14/12/2023, a empresa Allos foi classificado como 'Outros' no Subsetor Bovespa
# Acoes com problemas: CRTE3, GOLL3, INTB3
# Pensar em fazer um app multipages
# pensar em usar o st.session_state
# dados economatica = 01/01/2013 até 01/11/2023
# carteira de maior retorno é a carteira em que 100% do capital está no ativo de maior retorno
# carteira de mínima variancia é a carteira que seria o ponto de inflexao da curva, seria bem no meio da curva


# ---------------- Arquivos ---------------- # 
# tickers acoes existentes (o ideal seria fazer um web scrapping na B3 ou consumir uma api da B3, pq com um arquivo fica muito travado)
# https://www.dadosdemercado.com.br/bolsa/acoes , att: Cotações atualizadas no fechamento de 24/11/2023.
yf.pdr_override() #corrige problemas da bibliotece do pandas_datareader
acoes = pd.read_csv('https://raw.githubusercontent.com/jrodrigotico/python/projeto_acoes/base_completa_acoes_subsetor.csv', sep=';')[['Código','Subsetor Bovespa']]
acoes = acoes[acoes['Código'].apply(lambda x: len(str(x))==5)]
# acoes = acoes.loc[(acoes['ticker_numero'] != 'CÓDIGO') & (acoes['LISTAGEM'].notna())].iloc[:,range(0,2)]


# ---------------- Inicial ---------------- # 
st.set_page_config(page_title='Markowitz', layout='centered')
# if 'intro' not in st.session_state:
#     st.session_state['intro'] = False
    
st.header('Teoria Moderna de Portfólio - Markowitz')
st.markdown('''A Teoria Moderna do Portfólio, desenvolvida por Harry Markowitz na década de 1950,
            é um conceito fundamental em finanças que busca otimizar a relação entre risco e retorno
            em um portfólio de investimentos.''')

# if st.button('Simulação de Carteiras'):
#     st.session_state.intro = True # o session_state guarda as informações, ou seja, sem ele rodaria a cada interação, quando o botão 'Simulação de Carteiras', ele fica True

# variaveis vazias que serão rodadas no 'if', porem depois serão usadas fora do 'if' , por isso preciso declará-las fora
# selecionar_acoes = []
# data_i = None
# data_f = None

# if st.session_state['intro']: # preserva o estado que a pagina está, ou seja, a barra lateral ficará 'fixa' com os dados 'guardados'
st.sidebar.header('Parâmetros')
data_i = st.sidebar.date_input('Data inicial', format='YYYY-MM-DD', value=None)
data_i = pd.Timestamp(data_i)

data_f = st.sidebar.date_input('Data final',  format='YYYY-MM-DD', value=None)
data_f = pd.Timestamp(data_f)

# seleção de subsetor da empresa
subsetor = st.sidebar.multiselect('Selecione o subsetor', sorted(acoes['Subsetor Bovespa'].unique()))

# seleção de ações
# acoes filtradas pelo subsetor
filtro_subsetor = acoes.loc[acoes['Subsetor Bovespa'].isin(subsetor)].iloc[:,0] # esse iloc retorna as acoes de determinado subsetor que foi anteriormente selecionado, é zero pq o 0 representa a coluna de códigos que é o que eu desejo que retorne
filtro_subsetor = pd.DataFrame(filtro_subsetor)

# retirar tickers que deram problema com o yahoo finance
acoes_erro = pd.read_csv('https://raw.githubusercontent.com/jrodrigotico/python/projeto_acoes/acoes_erro_yahoo.csv', sep=';') 
acoes_erro.columns = ['Index', 'Ticker']

def retirar_sa(i):
    return i[:5]

acoes_erro['Ticker'] = acoes_erro['Ticker'].apply(retirar_sa)
valores_fixos = ~filtro_subsetor['Código'].isin(acoes_erro['Ticker'])
filtro_subsetor = filtro_subsetor[valores_fixos] # mantem os valores que nao estao em 'acoes_erro'


# filtro de acoes depois de selecionados os subsetores
selecionar_acoes = st.sidebar.multiselect('Selecione as ações', sorted(filtro_subsetor['Código'] + '.SA'))
st.set_option('deprecation.showPyplotGlobalUse', False)


# ---------------- Dados das ações selecionadas ---------------- #
# for i in selecionar_acoes:
#     tabela[f'{i}'] = round(yf.download(i, start=data_i, end=data_f)['Adj Close'].resample('M').last(),2)
tabelas_acoes = []  
tabela_norm = pd.DataFrame()
valores_iniciais = {}
indices_iniciais = {}

if selecionar_acoes:
    for i in selecionar_acoes:
        tabela_acao = round(yf.download(i, start=data_i, end=data_f)["Adj Close"].rename(i), 2)
        tabelas_acoes.append(tabela_acao)

        # primeiro valor e seu índice para cada ação
        primeiro_valor = tabela_acao.first_valid_index()
        if primeiro_valor:
            valores_iniciais[i] = tabela_acao.loc[primeiro_valor]
            indices_iniciais[i] = primeiro_valor

    tabela = pd.concat(tabelas_acoes, axis=1)

    st.write('---')
    st.subheader('Preço das ações histórico')
    for i in tabela.columns:
        if i in valores_iniciais and i in indices_iniciais: # normaliza usando o primeiro valor válido de cada ação, se disponível
            first_valid_index = indices_iniciais[i]
            tabela_norm[i[:5]] = round(tabela[i] / valores_iniciais[i], 2)
        else:
            first_valid_index = tabela[i].first_valid_index()
            if first_valid_index:
                tabela_norm[i[:5]] = round(tabela[i] / tabela[i].loc[first_valid_index], 2)
            else:
                tabela_norm[i[:5]] = tabela[i]
                
            
    # Plotar o gráfico com todas as ações selecionadas considerando intervalo em que determinada ação ainda nao existia e portanto preço igual a zero
    grafico2 = px.line(tabela_norm)
    grafico2.update_layout(width=800, height=500)
    st.plotly_chart(grafico2)
    
    
    # st.write('---')
    # st.subheader('Preço das ações') # normalizado
    # erro = None
    # for i in tabela.columns:
    #     tabela_norm[i[:5]] = round(tabela[i] / tabela[i].iloc[0], 2)  # pega dado da tabela anterior
    
    # # Plotar o gráfico com todas as ações selecionadas, a partir do momento em que todas as ações selecionadas existem    
    # grafico3 = px.line(tabela_norm)
    # grafico3.update_layout(width=800, height=500)
    # st.plotly_chart(grafico3)
    
    
    # Retornos Contínuos e Matriz de Correlação
    # ln(retorno_t / retorno_t-1)
    st.write('---')
    st.header('Médias dos retornos de cada ação:')
    tabela_retorn = tabela_norm.pct_change().dropna()
    media_retor = tabela_retorn.mean()
    for i in range(len(media_retor)):
        st.write(selecionar_acoes[i], round(media_retor[i],10))

    matriz_corr = tabela_retorn.corr() # para o modelo de markowitz é bom ter acoes com alta correlação negativa ! ver video: https://www.youtube.com/watch?v=Y1E73SQPD1U
    st.write('---')
    st.header('Matriz de covariância:')
    st.markdown('''Quanto menor a correlação entre os ativos ou até mesmo quanto mais negativa, menor será o risco dessa carteira se comparada aos ativos individuais ''')
    heatmap_retorn = px.imshow(matriz_corr, text_auto=True)
    st.plotly_chart(heatmap_retorn)


# ---------------- SELIC ---------------- #
# Dados cdi (taxa livre de risco)
# DI - Depósito Interfinanceiro - Taxas - DI PRÉ - Over
# SELIC
# 16/01/2013 até 30/11/2023 , fonte B3
selic = pd.read_csv('https://raw.githubusercontent.com/jrodrigotico/python/projeto_acoes/selic.csv', sep=';')
selic['Data'] = pd.to_datetime(selic['Data'])

# verificacoes da data para nao dar warning antes de selecionar os parametros da barra lateral
# isinstance verifica se é uma lista
# if isinstance(data_i, list) and len(data_i) > 0:
#     data_i = pd.to_datetime(data_i[0])
# else:
#     data_i = pd.to_datetime(data_i[0])

# if isinstance(data_f, list) and len(data_f) > 0:
#     data_f = pd.to_datetime(data_f[0])
# else:
#     data_f = pd.to_datetime(data_f[0])

selic = selic.loc[(selic['Data'] >= data_i) & (selic['Data'] <= data_f)]
selic['Taxa SELIC'] = selic['Taxa SELIC'].str.replace(',','.').astype(float)    

ret_livre = selic['Taxa SELIC'].dropna().mean()/100


# ---------------- Simulação ---------------- #
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
        tabela_volatilidades_esperadas[i] =  np.sqrt(np.dot(pesos_random.T, np.dot(matriz_corr * 252, pesos_random)))
        tabela_sharpe[i] = (tabela_retorn_esperados[i] - ret_livre) / tabela_volatilidades_esperadas[i]
        
    indice_sharpe_max = tabela_sharpe.argmax()
    carteira_max_retorno = tabela_pesos[indice_sharpe_max]
    menor_risco = tabela_volatilidades_esperadas.argmin()
    carteira_min_variancia= tabela_pesos[menor_risco]
    
    st.write('---') 
    st.header('Composição da carteira de Índice Sharpe máximo:')
    legenda = selecionar_acoes
    valores_cart_max_retorno = carteira_max_retorno
    graph_pizza = go.Figure(data=[go.Pie(labels=legenda, values =valores_cart_max_retorno )])
    st.plotly_chart(graph_pizza)
        
    st.header('Composição da carteira de mínima variância:')
    legenda = selecionar_acoes
    valores_cart_min_var = carteira_min_variancia
    graph_pizza2 = go.Figure(data=[go.Pie(labels=legenda, values =valores_cart_min_var )])
    st.plotly_chart(graph_pizza2)
    
    
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
        vol = np.sqrt(np.dot(peso_teste.T, np.dot(matriz_corr * 252, peso_teste)))
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

    st.write('---')
    st.header(f'Gráfico com a simulação de {numero_portfolios} carteiras: ') 
    st.subheader('Taxa livre de risco (SELIC)')  
    st.write(ret_livre)
    st.subheader('Índice de Sharpe máximo')  
    st.write((tabela_retorn_esperados_aritm[indice_sharpe_max] - ret_livre) / tabela_volatilidades_esperadas[indice_sharpe_max])

    # grafico interativo com a fronteira eficiente
    carteiras_simulacao = go.Scatter(x=tabela_volatilidades_esperadas,y=tabela_retorn_esperados_aritm,mode='markers',
        marker=dict(size=8, color=tabela_sharpe, colorscale='Viridis'), name = 'Carteiras simuladas')
    
    carteira_max_sharpe = go.Scatter(x=[tabela_volatilidades_esperadas[indice_sharpe_max]], y=[tabela_retorn_esperados_aritm[indice_sharpe_max]],
        mode='markers', marker= dict(size=12, color='red'), name = 'Carteira com o melhor Índice de Sharpe')
    
    carteira_min_variancia = go.Scatter(x=[tabela_volatilidades_esperadas[menor_risco]], y=[tabela_retorn_esperados_aritm[menor_risco]],
        mode='markers', marker= dict(size=12, color='black'), name = 'Carteira de mínima variância') # essa carteira é importante lembrar do ponto de 'inflexão'
    
    layout = go.Layout(xaxis= dict(title='Risco esperado'), yaxis= dict(title='Retorno esperado'))
    pontos_dispersao = [carteiras_simulacao, carteira_max_sharpe, carteira_min_variancia]
    fig = go.Figure(data=pontos_dispersao, layout=layout)
    st.plotly_chart(fig)


# ---------------- Simulação ativada e principais fórmulas ---------------- #   
if st.sidebar.button('Simular'):
    parametros_portofolio (int(numero_portfolios))
    st.write('---')
    with st.expander('Princpais fórmulas'):
        st.latex(r'''RetornoCarteira =  \sum_{i=1} WiRi''')
        st.write('\n')
        st.latex(r'''RetornoContínuo = \ln{\left(Retorno_t /Retorno_t-1\right) } ''')
        st.write('\n')
        st.latex(r''' IndíceSharpe = \left(\frac{{Retorno-Taxa\quad livre\quad de\quad risco}}{{Risco}} \right)''')
        st.write('\n')
        st.latex(r'''RiscoCarteira =  \sqrt{\left(Wa^2 \cdot \sigma a^2\right) + \left(Wb^2 \cdot \sigma b^2\right) + 2 \cdot \left( Wa \cdot Wb \cdot \rho ab \cdot \sigma  \cdot \sigma b  \right)}''')
        st.write('\n')
        st.latex(r'''\text{alternativamente pode-se usar a covariância entre os ativos} \\
            \text {multiplicada pelos seus respectivos pesos}''')
        st.latex(r'''RiscoCarteira =  \sqrt{\left(Wa^2 \cdot \sigma a^2\right) + \left(Wb^2 \cdot \sigma b^2\right) + 2 \cdot \left( Wa \cdot Wb \cdot covab\right)}''')
    with st.expander('Referências'):
        st.latex(r'''\text{Guasti Lima, Fabiano. Análise de Risco. Atlas, 2016}''')
        st.latex(r'''\text{Streamlit Documentaion - https://docs.streamlit.io}''')
        st.latex(r'''\text{Assaf Net, Alexandre. Mercado Financeiro. Décima Terceira Edição. Atlas}''')
        




