import pandas as pd
import yfinance as yf
import pandas_datareader as pdr
import numpy as np
import matplotlib.pyplot as mplt
import seaborn as sn
import datetime

yf.pdr_override() #corrige problemas da bibliotece do pandas_datareader

data_i = '2023-01-01'
data_f = '2023-06-01'
acoes = ['ITUB3']

tabela_cotacoes = pdr.get_data_yahoo('ITUB3', data_i, data_f)
tabela_cotacoes