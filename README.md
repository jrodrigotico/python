[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Python Version](https://img.shields.io/badge/python-3.11.6-blue.svg)](https://www.python.org/downloads/)
![GitHub License](https://img.shields.io/github/license/jrodrigotico/python)

:construction_worker: Projeto em desenvolvimento


## 	:school: Teoria Moderna de Portfólio - Markowitz
A Teoria Moderna do Portfólio, desenvolvida por Harry Markowitz em meados de 1950, postula que diferentes ativos podem compor 'n' carteiras de investimentos com o intuito de encontrar uma relação ótima entre risco e retorno. 
Markowitz é o principal responsável por introduzir conceitos de diversificação de ativos, contribuindo significativamente para o aprimoramento das estratégias de investimentos.


## 	:books: Estrutura do repositório
| **Arquivo** | **Conteúdo** |
| ------------- | ------------- |
| mark_st.py | Script da aplicação web |
| arquivos | Arquivos no formato '.csv' que são utilizados em 'mark_st.py' |
| requirements.txt | Dependências do projeto |

:exclamation: O trabalho de Markowitz está anexado em 'arquivos' com o nome de 'Teoria_Markowitz_1952.pdf'.


## 	:scissors: Tratamento dos dados
A taxa **SELIC** foi selecionada como a taxa livre de risco para calcular o **Índice de Sharpe**. Os dados estão disponíveis para o período entre 16/01/2013 e 31/11/2023.

Ações brasilerias precisam estar com **'.SA'** para servirem como símbolo no 'Yahoo Finance' e assim extrair informações.

A ação da empresa **Allos (ALOS3)** está no subsetor **'Outros'**.

No arquivo **'base_completa_acoes_subsetor.csv'**, localizado na pasta 'arquivos', consta uma lista de todas as ações listadas na B3, conforme a base do **Economatica** em 14/12/2023. Ações com tickers de seis caracteres foram retiradas, pois não são acessíveis via API do Yahoo Finance.

Algumas ações apresentaram problemas durante a extração de dados da API do Yahoo Finance, então essas empresas foram excluídas da lista de tickers. Os detalhes dessas ações estão no arquivo **'acoes_erro_yahoo.csv'**, também na pasta 'arquivos'.


## :bar_chart: Demonstração da aplicação

gif

falar brevemente da utilidade e funcionalidades, falar sobre o 'bug' de quando for selecionar as acoes que precisa-se selecionar uma de cada vez , 
apenas quando aparecer o grafico historico de pre

:exclamation: É necessário aguardar a conclusão do plotagem do gráfico histórico de preços antes de escolher uma nova ação na caixa de seleção 'Ações'.


## 	:desktop_computer: Acesso ao aplicativo
Clone do repositório:

```
git clone https://github.com/jrodrigotico/python.git
```

Instalação das depedências:

```
pip install -r requirements.txt
```

Rodar o script 'mark_st.py' e aplicar o seguinte comando no terminal:
```
streamlit run mark_st.py
```

Alternativamente, pode-se acessar o aplicativo por qualquer navegador pelo link:
http://localhost:8501  

:exclamation: Recomenda-se a utilização do aplicativo em um navegador no modo 'Dark'.  


## :mag_right: Tecnologias utilizadas
- ``Python - 3.11.6``
- ``API Yahoo Finance (yfinance - v0.2.33)``
- ``Streamlit``
- ``Visual Studio Code``


## 	:email: Contato
Para feedbacks, sugestão de melhorias ou relato de problemas, sinta-se à vontade para entrar em contato comigo através do meu perfil no Linkedin:

[![LinkedIn Badge](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/joão-rodrigo-lemes-5603a6154/)





