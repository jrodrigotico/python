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
# Acoes com problemas:  OIBR3 (da retorno inf), MMAQ3 ( nan na media dos retornos)
# se eu adicionar uma acao que nao comeca no mesmo intervalo de tempo, da problema no indice de sharpe que fica 'nan', ex: 'AGXY3'
# Pensar em fazer um app multipages
# pensar em usar o st.session_state
# dados economatica = 01/01/2013 até 01/11/2023
# carteira de maior retorno é a carteira em que 100% do capital está no ativo de maior retorno
# carteira de mínima variancia é a carteira que seria o ponto de inflexao da curva, seria bem no meio da curva
# papaer: V = variância da carteira , E = retorno da carteira
# sigma = σ = covariancia

# Textos - rascunho
#  ****(μi, σij) 
# O símbolo "μi" representa a média ou o valor esperado de uma variável aleatória "i"
# "σij" sugere uma matriz de covariância ou uma medida que captura a variabilidade conjunta entre as variáveis "i" e "j". Isso implica que há uma relação ou dependência entre essas variáveis.

# ***** indice de sharpe negativo
# Se, por acaso, o ativo em análise apresentar um Sharpe negativo, isso indica que o retorno
#  da aplicação não compensa o seu risco, que é representado pela volatilidade


# ---------------- Arquivos ---------------- # 
# tickers acoes existentes (o ideal seria fazer um web scrapping na B3 ou consumir uma api da B3, pq com um arquivo fica muito travado)
# https://www.dadosdemercado.com.br/bolsa/acoes , att: Cotações atualizadas no fechamento de 24/11/2023.
yf.pdr_override() #corrige problemas da bibliotece do pandas_datareader
acoes = pd.read_csv('https://raw.githubusercontent.com/jrodrigotico/python/projeto_acoes/base_completa_acoes_subsetor.csv', sep=';')[['Código','Subsetor Bovespa']]
acoes = acoes[acoes['Código'].apply(lambda x: len(str(x))==5)]


# ---------------- Introducao ---------------- # 
def introducao(): # funcao para exibir a introducao e seus componentes
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
        st.session_state['exibir_introducao'] = False # transforma a chave em falsa
        st.experimental_rerun() # recarrega a página

# --------- Código geral ---------- #
if not exibir_introducao:
    st.sidebar.header('Parâmetros')

    data_i = st.sidebar.date_input('Data inicial', format='YYYY-MM-DD', value=None)
    data_i = pd.Timestamp(data_i)
    data_f = st.sidebar.date_input('Data final',  format='YYYY-MM-DD', value=None)
    data_f = pd.Timestamp(data_f)
    peridiocidade = st.sidebar.selectbox('Selecione a peridiocidade', ('Diário', 'Mensal', 'Anual'))

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
    tabelas_acoes = []  
    tabela_norm = pd.DataFrame()
    valores_iniciais = {}
    indices_iniciais = {}

    if selecionar_acoes:
        for i in selecionar_acoes:
            # tabela_acao = round(yf.download(i, start=data_i, end=data_f)['Adj Close'].resample('M').last(),2)
            try:
                tabela_acao = round(yf.download(i, start=data_i, end=data_f)["Adj Close"].rename(i), 2)
            except:
                pass

            if peridiocidade=='Mensal':
                tabela_acao = tabela_acao.resample('M').last()
            elif peridiocidade == 'Anual':
                tabela_acao = tabela_acao.resample('Y').last()
            else:
                tabela_acao = tabela_acao
            tabelas_acoes.append(tabela_acao)

            # primeiro valor e seu índice para cada ação
            primeiro_valor = tabela_acao.first_valid_index()
            if primeiro_valor:
                valores_iniciais[i] = tabela_acao.loc[primeiro_valor]
                indices_iniciais[i] = primeiro_valor

        tabela = pd.concat(tabelas_acoes, axis=1)

        st.subheader(f'Preço das ações - {peridiocidade}')
        st.markdown('''Os preços das ações selecionadas ao longo do intervalo de tempo estão normalizados. 
                    Essa normalização garante que o preço de todas as ações comece a partir do mesmo valor, 
                    possibilitando a comparação e sem alterar o comportamento dessas ações.''')
        
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

        # Retornos Contínuos e Matriz de Correlação
        # ln(retorno_t / retorno_t-1)
        st.write('---')
        st.header('Médias dos retornos de cada ação:')
        st.markdown('''Foi utilizado o retorno contínuo para o cálculo do retorno de cada ação, em seguida, foi-se calculada a média.
                    Os dados mostrados abaixo já estão em porcentagem.''')
        tabela_retorn = tabela_norm.pct_change().dropna() # aqui se faz a formula norma de variacao percentual: 'Valor f/Valor i - 1 '
        retorno_contiuo = np.log(tabela_retorn + 1) # aqui soma-se 1 para ficar apenas a divisao entre 'Valor f/Valor i' e o LN é aplicado nessa divisão
        
        def media(i):
            return i.mean()
        media_retor = retorno_contiuo.apply(media, axis = 0) # compara os valores das linhas

        for i, z in zip(media_retor, selecionar_acoes):
            porcent = i * 100
            # st.latex(rf'''\text{{{z}: {i:.4f}\%}}''')
            st.write(z, ": ", round(i,4))
        matriz_corr = tabela_retorn.corr() # para o modelo de markowitz é bom ter acoes com alta correlação negativa ! ver video: https://www.youtube.com/watch?v=Y1E73SQPD1U

        st.write('---')
        st.header('Matriz de correlação:')
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

    selic = selic.loc[(selic['Data'] >= data_i) & (selic['Data'] <= data_f)]
    selic['Taxa SELIC'] = selic['Taxa SELIC'].str.replace(',','.').astype(float)    
    ret_livre = selic['Taxa SELIC'].dropna().mean()/100


    # ---------------- Simulação ---------------- #
    fator_periodicidade = []
    numero_portfolios = st.sidebar.number_input('Insira o número de portfolios')
    def parametros_portofolio (numero_portfolios):
            
        tabela_retorn_esperados = np.zeros(numero_portfolios)
        tabela_volatilidades_esperadas = np.zeros(numero_portfolios)
        tabela_sharpe = np.zeros(numero_portfolios)
        tabela_pesos = np.zeros((numero_portfolios, len(selecionar_acoes)))
        tabela_retorn_esperados_aritm = np.zeros(numero_portfolios)

        if peridiocidade == 'Mensal':
            fator_periodicidade = 12
        elif peridiocidade == 'Anual':
            fator_periodicidade = 1
        elif peridiocidade == 'Diário':
            fator_periodicidade = 252     
        
        for i in range(numero_portfolios):
            pesos_random = np.random.random(len(selecionar_acoes))
            pesos_random /= np.sum(pesos_random)
            tabela_pesos[i,:] = pesos_random
            tabela_retorn_esperados[i] = np.sum(media_retor * pesos_random * fator_periodicidade)
            tabela_retorn_esperados_aritm[i] = np.exp(tabela_retorn_esperados[i])-1
            tabela_volatilidades_esperadas[i] =  np.sqrt(np.dot(pesos_random.T, np.dot(matriz_corr * fator_periodicidade, pesos_random)))
            tabela_sharpe[i] = (tabela_retorn_esperados[i] - ret_livre) / tabela_volatilidades_esperadas[i]
            
        indice_sharpe_max = tabela_sharpe.argmax()
        carteira_max_retorno = tabela_pesos[indice_sharpe_max]
        menor_risco = tabela_volatilidades_esperadas.argmin()
        carteira_min_variancia= tabela_pesos[menor_risco]

        st.write('---')
        st.header('Carteira de mínima variância:')
        st.markdown('''Para uma determinada combinação de pesos de ativos em uma carteira, há um ponto que representa o risco  mínimo.
                    Esse ponto representa a carteira de mínimo risco ou carteira de mínima variância.''')
        
        legenda = selecionar_acoes
        valores_cart_min_var = carteira_min_variancia
        graph_pizza2 = go.Figure(data=[go.Pie(labels=legenda, values =valores_cart_min_var )])
        st.plotly_chart(graph_pizza2)

        st.header('Carteira ótima:')
        st.markdown('''Para a determinação da carteira ótima foi utilizado o 'Índice de Sharpe'.  O ponto que representa a carteira ótima
                        mostra a combinação de ativos para ter um ganho a partir de uma taxa livre de risco.''')    
        
        legenda = selecionar_acoes
        valores_cart_max_retorno = carteira_max_retorno
        graph_pizza = go.Figure(data=[go.Pie(labels=legenda, values =valores_cart_max_retorno )])
        st.plotly_chart(graph_pizza)

        # st.write('---') 

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
        # st.latex(rf'''\text{{Taxa livre de risco (SELIC) média: {ret_livre*100:.4f}\%}}''')
        st.markdown(f'Taxa livre de risco (SELIC) média: {round(ret_livre,4)}')   
        
        sharpe_max = ((tabela_retorn_esperados_aritm[indice_sharpe_max] - ret_livre) / tabela_volatilidades_esperadas[indice_sharpe_max])
        # st.latex(rf'''\text{{Índice de Sharpe Máximo: {sharpe_max}}}''')
        st.markdown(f'Índice de Sharpe Máximo: {round(sharpe_max,4)}')
        if sharpe_max>0:
            st.write(f'O índice de Sharpe de {round(sharpe_max,4)} diz que para cada 1 ponto de risco, o investidor obteve um retorno positivo de {round(sharpe_max,4)}. Com isso o investimento na carteira compensa o risco.')
        elif sharpe_max<0:
            st.write(f'O índice de Sharpe de {sharpe_max} diz que para cada 1 ponto de risco, o investidor obteve um retorno negativo de {sharpe_max}. Com isso o investimento na carteira não compensa o risco.')
        elif sharpe_max=='nan':
            st.write('Algum ativo escolhido apresenta média de retorno igual a zero ou nan')

        # grafico interativo com a fronteira eficiente
        carteiras_simulacao = go.Scatter(x=tabela_volatilidades_esperadas,y=tabela_retorn_esperados_aritm,mode='markers',
            marker=dict(size=8, color=tabela_sharpe, colorscale='Viridis'), name = 'Carteiras simuladas')
        
        carteira_max_sharpe = go.Scatter(x=[tabela_volatilidades_esperadas[indice_sharpe_max]], y=[tabela_retorn_esperados_aritm[indice_sharpe_max]],
            mode='markers', marker= dict(size=12, color='red'), name = 'Carteira com o melhor Índice de Sharpe')
        
        carteira_min_variancia = go.Scatter(x=[tabela_volatilidades_esperadas[menor_risco]], y=[tabela_retorn_esperados_aritm[menor_risco]],
            mode='markers', marker= dict(size=12, color='pink'), name = 'Carteira de mínima variância') # essa carteira é importante lembrar do ponto de 'inflexão'

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
            st.latex(r'''RiscoCarteira =  \sqrt{\left(Wa^2 \cdot \sigma a^2\right) + \left(Wb^2 \cdot \sigma b^2\right) + 2 \cdot \left( Wa \cdot Wb \cdot \rho ab \cdot \sigma a  \cdot \sigma b  \right)}''')
            st.write('\n')
            st.latex(r'''\text{alternativamente pode-se usar a covariância entre os ativos} \\
                \text {multiplicada pelos seus respectivos pesos}''')
            st.latex(r'''RiscoCarteira =  \sqrt{\left(Wa^2 \cdot \sigma a^2\right) + \left(Wb^2 \cdot \sigma b^2\right) + 2 \cdot \left( Wa \cdot Wb \cdot covab\right)}''')
        with st.expander('Referências'):
            st.latex(r'''\text{MARKOWITZ, Harry. Portfolio selection. The Journal of Finance,}\\
                    \text {v. 7, n. 1, p. 77-91, Mar. 1952}''')
            st.latex(r'''\text{Guasti Lima, Fabiano. Análise de Risco. Atlas, 2016}''')
            st.latex(r'''\text{Assaf Neto, Alexandre. Mercado Financeiro. Décima Terceira Edição. Atlas}''')
            st.latex(r'''\text{Canal Brenno Sullivan - VAROS Quant }''')
            st.latex(r'''\text{Streamlit Documentaion - https://docs.streamlit.io}''')




