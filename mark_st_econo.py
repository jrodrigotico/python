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
import time
# streamlit run mark_st_econo.py


# teste= st.container()
# with teste:
#     st.write('nofdogidsf')

# if st.button('limpar'):
#     teste.empty()

# teste = st.empty()

# if st.button('Mostrar Texto'):
#     teste.write('Texto exibido')

# if st.button('Limpar'):
#     teste.empty()


######################### duplicado ################################
# exibir_introducao = True

# if exibir_introducao:
#     introducao = st.container()
#     introducao.header('Teoria Moderna de Portfólio - Markowitz')
#     introducao.write('''A Teoria Moderna do Portfólio, desenvolvida por Harry Markowitz em meados de 1950, postula que diferentes ativos 
#                         podem compor 'n' carteiras de investimentos com o intuito de encontrar uma relação ótima entre risco (variância) e retorno.
#                         Para determinar essa relação, Markowitz não descarta o uso do julgamento profissional para a escolha dos ativos, utilizando 
#                         critérios específicos que não são contemplados nos cálculos matemáticos formais. Com essa abordagem, 
#                         torna-se viável calcular combinações de 'retorno' e 'risco.
#                         Markowitz é o principal responsável por introduzir conceitos de diversificação de ativos!''')
#     # Fonte: The Nobel Prize
#     introducao.image('intro_markow.jpg', caption='Fonte: The Nobel Prize')

# # Botão "Simulação de Carteiras" para remover a introdução
# if st.button('Simulação de Carteiras'):
#     exibir_introducao = False

# # Se exibir_introducao for True, o conteúdo será exibido
# if exibir_introducao:
#     introducao = st.container()
#     introducao.header('Teoria Moderna de Portfólio - Markowitz')
#     introducao.write('''A Teoria Moderna do Portfólio, desenvolvida por Harry Markowitz em meados de 1950, postula que diferentes ativos 
#                         podem compor 'n' carteiras de investimentos com o intuito de encontrar uma relação ótima entre risco (variância) e retorno.
#                         Para determinar essa relação, Markowitz não descarta o uso do julgamento profissional para a escolha dos ativos, utilizando 
#                         critérios específicos que não são contemplados nos cálculos matemáticos formais. Com essa abordagem, 
#                         torna-se viável calcular combinações de 'retorno' e 'risco.
#                         Markowitz é o principal responsável por introduzir conceitos de diversificação de ativos!''')
#     # Fonte: The Nobel Prize
#     introducao.image('intro_markow.jpg', caption='Fonte: The Nobel Prize')


###################
# def main():
#     exibir_introducao = st.session_state.get('exibir_introducao', True)

#     if exibir_introducao:
#         introducao = st.container()
#         introducao.header('Teoria Moderna de Portfólio - Markowitz')
#         introducao.write('''A Teoria Moderna do Portfólio, desenvolvida por Harry Markowitz em meados de 1950, postula que diferentes ativos 
#                             podem compor 'n' carteiras de investimentos com o intuito de encontrar uma relação ótima entre risco (variância) e retorno.
#                             Para determinar essa relação, Markowitz não descarta o uso do julgamento profissional para a escolha dos ativos, utilizando 
#                             critérios específicos que não são contemplados nos cálculos matemáticos formais. Com essa abordagem, 
#                             torna-se viável calcular combinações de 'retorno' e 'risco.
#                             Markowitz é o principal responsável por introduzir conceitos de diversificação de ativos!''')
#         # Fonte: The Nobel Prize
#         introducao.image('intro_markow.jpg', caption='Fonte: The Nobel Prize')

#         # Botão "Limpar Introdução" para remover manualmente a introdução
#         if st.button('Simulação de Carteiras'):
#             st.session_state['exibir_introducao'] = False
#             st.experimental_rerun()

#     # Remover o botão quando a introdução já não estiver visível
#     elif not exibir_introducao:
#         pass

# if __name__ == "__main__":
#     main()

##################
def introducao():
    introducao = st.container()
    introducao.header('Teoria Moderna de Portfólio - Markowitz')
    introducao.write('''A Teoria Moderna do Portfólio, desenvolvida por Harry Markowitz em meados de 1950, postula que diferentes ativos 
                        podem compor 'n' carteiras de investimentos com o intuito de encontrar uma relação ótima entre risco (variância) e retorno.
                        Para determinar essa relação, Markowitz não descarta o uso do julgamento profissional para a escolha dos ativos, utilizando 
                        critérios específicos que não são contemplados nos cálculos matemáticos formais. Com essa abordagem, 
                        torna-se viável calcular combinações de 'retorno' e 'risco.
                        Markowitz é o principal responsável por introduzir conceitos de diversificação de ativos!''')
    # Fonte: The Nobel Prize
    introducao.image('intro_markow.jpg', caption='Fonte: The Nobel Prize')

exibir_introducao = st.session_state.get('exibir_introducao', True)

if exibir_introducao:
    introducao()

    # remove a introdução
    if st.button('Simulação de Carteiras'):
        st.session_state['exibir_introducao'] = False
        st.experimental_rerun()

# Restante do código após pressionar o botão
if not exibir_introducao:
    st.header('Aqui está o restante do seu conteúdo!')
    st.write('Seu código continua aqui...')
    st.write('É isso!')

    