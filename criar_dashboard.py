########### testanto 2
import os   
from dash import Dash, html, dcc
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd 
from scipy.stats import f
from scipy.stats import t
import numpy as np  
os.chdir('C:/Users/Computadores Gamer/OneDrive/Área de Trabalho/dash python')    

# criacao aplicativo
app_teste2 = Dash(__name__)

#### criacao tabela
vendas = pd.read_excel('Vendas.xlsx', 'Plan1', parse_dates=['Data'])
vendas = pd.DataFrame(vendas)

# extraindo ano mes e dia
vendas['ano'] = vendas['Data'].dt.year
vendas['mes'] = vendas['Data'].dt.month
vendas['dia'] = vendas['Data'].dt.day
del vendas['Data']

# agrupando ( o codigo abaixo trata de um jeito porco Tabela MultiIndex para Tabela Index)
vendas.columns
vendas1 = vendas.groupby('ID Loja').agg({'Produto':[('count')]}).T
vendas1 = vendas1.reset_index(drop=True)
vendas1 = vendas1.T
vendas1 = vendas1.reset_index(drop=False)
vendas1 = vendas1.rename(columns = {'ID Loja':'loja',0:'quant_produtos'})


#### criacao grafico
vendas1.columns
grafico_vendas = px.bar(vendas1, x=('loja'), y ='quant_produtos')
grafico_geral = px.scatter(vendas, x = 'Produto' , y= 'Valor Unitário')
 

# layout
app_teste2.layout = html.Div(children =[
    html.H1(children='Produtos por loja'),
    
    html.Div(children = '''
             Produtos vendidos em lojas de shopping centers
             '''),
             
    dcc.Graph(id = 'teste vendas', figure = grafico_vendas ),
    dcc.Graph(id = 'teste2 vendas', figure = grafico_geral )
   
])

# coloca o site no ar
if __name__ == '__main__':
    app_teste2.run_server(debug = False)