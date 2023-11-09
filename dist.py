import pandas as pd
import streamlit as st
import os
import numpy as np
import plotly.figure_factory as ff
import plotly.express as px
import seaborn as sb
import random
import matplotlib.pyplot as plt

# anotações
# inicial streamlit = https://www.youtube.com/watch?v=0sxWFeFlsHs&t=231s
# deploy streamlit = https://www.youtube.com/watch?v=vw0I8i7QJRk
# https://tdenzl-bulian-bulian-ifeiih.streamlit.app / https://github.com/tdenzl/bulian
# control + c para o terminal 
# fazer funcao para ver se existe pelo menos um input vazio e retornar uma mensagem
# checar seed, ver se eu colocar a mesma seed se da o mesmo gráfico
# melhorar o layout, ideias: colocar formula, mexer na posicao das coisas, alterar tamanho da fonte, aumentar grafico
# ver st.echo(), 

st.set_page_config (page_title='Distribuições estatísticas', initial_sidebar_state= 'expanded',layout='centered', page_icon=':bar_chart:')
# st.header('Distribuições')

st.markdown('<br>', unsafe_allow_html=True) # adiciona uma linha vazia para dar um 'espaçamento'
# st.markdown('<br><br>', unsafe_allow_html=True) # adiciona duas linhas vazias para dar um 'espaçamento'

seed = int(st.sidebar.number_input('Seed', value=0, help='Garante a replicação do modelo'))
st.sidebar.markdown('---')

parametros = []
st.sidebar.header('Parâmetros')
opcoes_dist = st.sidebar.selectbox('Qual distribuição?', ('Normal','Binomial','Binomial Negativa','t', 'f', 'Qui²', 'Poisson'), index=None)
if opcoes_dist =='Binomial':
    numero1 = st.sidebar.number_input('Número de tentativas', value=None, placeholder= 'Insira um número')
    numero2 = st.sidebar.number_input('Probabilidade de Sucesso', value=None, placeholder= 'Insira um número')
    numero3 = st.sidebar.number_input('Tamanho', value=None, placeholder= 'Insira um número', step =1)
    numero4 = st.sidebar.number_input('Bins', value=None, placeholder= 'Insira um número', step = 1)
    parametros.extend([numero1,numero2,numero3,numero4])
elif opcoes_dist =='Binomial Negativa':
    numero1 = st.sidebar.number_input('Número de sucessos', value=None, placeholder= 'Insira um número')
    numero2 = st.sidebar.number_input('Probabilidade de Sucesso', value=None, placeholder= 'Insira um número')
    numero3 = st.sidebar.number_input('Tamanho', value=None, placeholder= 'Insira um número', step =1)
    numero4 = st.sidebar.number_input('Bins', value=None, placeholder= 'Insira um número', step = 1)
    parametros.extend([numero1,numero2,numero3,numero4])
elif opcoes_dist =='Poisson':
    numero1 = st.sidebar.number_input('Média', value=None, placeholder= 'Insira um número')
    numero2 = st.sidebar.number_input('Graus de liberdade', value=None, placeholder= 'Insira um número')
    numero3 = st.sidebar.number_input('Tamanho', value=None, placeholder= 'Insira um número', step =1)
    numero4 = st.sidebar.number_input('Bins', value=None, placeholder= 'Insira um número', step=1)
    parametros.extend([numero1,numero2,numero3,numero4])
elif opcoes_dist =='Normal':
    numero1 = st.sidebar.number_input('Média', value=None, placeholder= 'Insira um número')
    numero2 = st.sidebar.number_input('Desvio-padrão', value=None, placeholder= 'Insira um número')
    numero3 = st.sidebar.number_input('Tamanho', value=None, placeholder= 'Insira um número', step =1)
    numero4 = st.sidebar.number_input('Bins', value=None, placeholder= 'Insira um número',step =1)
    parametros.extend([numero1,numero2,numero3,numero4])
elif opcoes_dist =='Qui²':
    numero1 = st.sidebar.number_input('Graus de liberdade', value=None, placeholder= 'Insira um número')
    numero2 = st.sidebar.number_input('Tamanho', value=None, placeholder= 'Insira um número', step =1)
    numero3 = st.sidebar.number_input('Bins', value=None, placeholder= 'Insira um número', step=1)
    parametros.extend([numero1,numero2,numero3])
elif opcoes_dist =='t':
    numero1 = st.sidebar.number_input('Graus de liberdade', value=None, placeholder= 'Insira um número')
    numero2 = st.sidebar.number_input('Tamanho', value=None, placeholder= 'Insira um número', step =1)
    numero3 = st.sidebar.number_input('Bins', value=None, placeholder= 'Insira um número', step=1)
    parametros.extend([numero1,numero2,numero3])
elif opcoes_dist =='f':
    numero1 = st.sidebar.number_input('Graus de liberdade numerador', value=None, placeholder= 'Insira um número')
    numero2 = st.sidebar.number_input('Graus de liberdade denominador', value=None, placeholder= 'Insira um número')
    numero3 = st.sidebar.number_input('Tamanho', value=None, placeholder= 'Insira um número', step =1)
    numero4 = st.sidebar.number_input('Bins', value=None, placeholder= 'Insira um número', step=1)
    parametros.extend([numero1,numero2,numero3,numero4])
else:
    st.sidebar.write('Parâmetros da distribuição serão apresentados quando o tipo da distribuição for selecionado')


# gráficos, fiz matplot para distribuições que são discretas, pq o ff.create_displot nao funciona bem com distribuicoes discretas
st.set_option('deprecation.showPyplotGlobalUse', False)


# Gráficos ()

if opcoes_dist =='Binomial':
    st.subheader('Distribuição' + ' ' + opcoes_dist)
    if all(x is not None for x in parametros): # se cada parametro x de 'parametros' estiver preenchido, a condicao entra e o grafico é plotado
        distribuicao = np.random.binomial(parametros[0],parametros[1],parametros[2])
        plt.hist(distribuicao, bins=parametros[3])
        st.pyplot()
    else:
        st.warning('Preencher todos os paramêtros!')
    

elif opcoes_dist =='Binomial Negativa':
    st.subheader('Distribuição' + ' ' + opcoes_dist)
    if all(x is not None for x in parametros):
        distribuicao = np.random.negative_binomial(parametros[0], parametros[1],parametros[2])
        plt.hist(distribuicao, bins=parametros[3])
        st.pyplot()
    else:
        st.warning('Preencher todos os paramêtros!')

elif opcoes_dist =='Poisson':
    st.subheader('Distribuição' + ' ' + opcoes_dist)
    if all(x is not None for x in parametros):
        distribuicao = np.random.poisson(parametros[0],parametros[2])
        plt.hist(distribuicao, bins=parametros[3])
        st.pyplot()  
    else:
        st.warning('Preencher todos os paramêtros!')  
    

elif opcoes_dist =='Normal':
    st.subheader('Distribuição' + ' ' + opcoes_dist)
    if all(x is not None for x in parametros):
        distribuicao = np.random.normal(parametros[0],parametros[1],parametros[2])
        plt.hist(distribuicao, bins=parametros[3])
        st.pyplot()
    else:
        st.warning('Preencher todos os paramêtros!')  
        

elif opcoes_dist =='Qui²':
    st.subheader('Distribuição' + ' ' + opcoes_dist)
    if all(x is not None for x in parametros):
        distribuicao = np.random.chisquare(parametros[0],parametros[1])
        plt.hist(distribuicao, bins=parametros[2])
        st.pyplot()
    else:
        st.warning('Preencher todos os paramêtros!')  
        

elif opcoes_dist =='t':
    st.subheader('Distribuição' + ' ' + opcoes_dist)
    if all(x is not None for x in parametros):
        distribuicao = np.random.standard_t(parametros[0],parametros[1])
        plt.hist(distribuicao, bins=parametros[2])
        st.pyplot()
    else:
        st.warning('Preencher todos os paramêtros!')  
        

elif opcoes_dist =='f':
    st.subheader('Distribuição' + ' ' + opcoes_dist)
    if all(x is not None for x in parametros):
        distribuicao = np.random.f(parametros[0],parametros[1], parametros[2])
        plt.hist(distribuicao, bins=parametros[3])
        st.pyplot()
    else:
        st.warning('Preencher todos os paramêtros!')  
        



# exemplo sem usar o matplot lib
# elif opcoes_dist =='f':
#     distribuicao = np.random.f(parametros[0],parametros[1], parametros[2])
#     tabela = pd.DataFrame({'dist_f': distribuicao})
#     grafico = ff.create_distplot([tabela['dist_f']], group_labels=['Distribuição f'], bin_size = parametros[3]/100)  # nao posso usar seaborn para o grafico pq esse pacote retorna um grafico matplot e o plotly nao aceita
#     st.plotly_chart(grafico, use_container_width=True)