# Projeto de Web Scraping com Python e Scrapy

## Descrição

Este é um projeto didático e realiza a extração de dados de produtos de um site e-commerce utilizando a biblioteca Scrapy. Os dados extraídos são processados e armazenados em um banco de dados usando SQLite para posterior análises.

## Estrutura do Projeto

O projeto é estruturado de acordo com o padrão do Scrapy e além da estrutura de pastas padrão, contém os seguintes arquivos principais:

### Arquivo: `mercadolivre.py`

Este arquivo contém o código do spider Scrapy responsável por extrair informações de produtos da lista de resultados de busca do Mercado Livre.

#### Código:

```python
import scrapy

class MercadolivreSpider(scrapy.Spider):
    name = "mercadolivre"
    start_urls = ["https://lista.mercadolivre.com.br/intelbras"]
    pag_inicial = 1
    pag_final = 10

    def parse(self, response):
        """
        Faz o parse da resposta HTML obtida a partir da URL inicial. 
        Extrai informações dos itens listados na página e gera um dicionário com os dados extraídos.
        """

        # Seleciona todos os itens na página de resultados de busca
        itens = response.css('div.ui-search-result__content')

        for item in itens:
            # Extrai os preços e centavos dos itens
            precos = item.css('span.andes-money-amount__fraction::text').getall()
            centavos = item.css('span.andes-money-amount__cents::text').getall()

            # Gera um dicionário com as informações extraídas de cada item
            yield {
                'produto': item.css('h2.ui-search-item__title::text').get(),
                'avaliação': item.css('span.ui-search-reviews__rating-number::text').get(),
                'avaliações_qtd': item.css('span.ui-search-reviews__amount::text').get(),
                'preco': precos[1] if len(precos) > 1 else None,
                'preco_centavos': centavos[1] if len(centavos) > 1 else None
            }

        # Verifica se há mais páginas a serem processadas
        if self.pag_inicial < self.pag_final:
            # Extrai o link para a próxima página de resultados
            if proxima_pagina := response.css(
                'li.andes-pagination__button.andes-pagination__button--next a::attr(href)'
            ).get():
                self.pag_inicial += 1
                # Faz uma requisição para a próxima página e chama o método parse novamente
                yield scrapy.Request(url=proxima_pagina, callback=self.parse)
```

### Arquivo: `data_transformation.py`

Este arquivo contém o código responsável por processar os dados extraídos, adicionando metadados, limpando os dados e armazenando-os em um banco de dados SQLite.

#### Código:

```python
import pandas as pd
import sqlite3
import datetime as dt

class MercadoLivreData:
    def __init__(self, json_path, db_path, source_url):
        """
        Inicializa a classe com os caminhos para o arquivo JSON, banco de dados e URL de origem.
        """
        self.json_path = json_path
        self.db_path = db_path
        self.source_url = source_url
        self.df = None

    def load_data(self):
        """
        Carrega os dados do arquivo JSON.
        """
        self.df = pd.read_json(self.json_path, lines=True)

    def add_metadata(self):
        """
        Adiciona metadados ao DataFrame.
        """
        self.df['_source'] = self.source_url
        self.df['_data_coleta'] = dt.datetime.now()

    def clean_data(self):
        """
        Limpa e processa os dados do DataFrame.
        """
        self.df['avaliações_qtd'] = self.df['avaliações_qtd'].str.replace('[\(\)]', '', regex=True)
        self.df['avaliações_qtd'] = self.df['avaliações_qtd'].fillna(0).astype(int)

        self.df['avaliação'] = self.df['avaliação'].fillna(0).astype(float)
        self.df['preco'] = self.df['preco'].fillna(0).astype(float)
        self.df['preco_centavos'] = self.df['preco_centavos'].fillna(0).astype(float)

        self.df['preco_produto'] = self.df['preco'] + self.df['preco_centavos'] / 100
        self.df.drop('preco_centavos', axis=1, inplace=True)
        self.df.drop('preco', axis=1, inplace=True)

    def save_to_sql(self):
        """
        Salva os dados no banco de dados SQLite.
        """
        con = sqlite3.connect(self.db_path)
        self.df.to_sql('prod_mercado_livre', con=con, if_exists='replace', index=False)
        con.close()

    def process(self):
        """
        Executa o fluxo completo de processamento dos dados:
        - Carrega os dados
        - Adiciona metadados
        - Limpa os dados
        - Salva os dados no banco de dados
        """
        self.load_data()
        self.add_metadata()
        self.clean_data()
        self.save_to_sql()

if __name__ == "__main__":
    json_path = '../../Dados/itensML.jsonl'
    db_path = '../../Dados/scrp_ml.db'
    source_url = 'https://lista.mercadolivre.com.br/intelbras'

    ml_data = MercadoLivreData(json_path, db_path, source_url)
    ml_data.process()
```

## Funcionalidades

* **Extração de Dados** : Utiliza Scrapy para extrair informações de produtos do Mercado Livre, como nome do produto, avaliação, quantidade de avaliações e preço.
* **Transformação de Dados** : Processa os dados extraídos, adiciona metadados e limpa as informações.
* **Armazenamento de Dados** : Salva os dados processados em um banco de dados SQLite para análise posterior.

## Resultados

Os dados extraídos e processados estão armazenados em um banco de dados SQLite (`scrp_ml.db`) e podem ser utilizados para diversas análises de mercado e precificação.

## Executando o Projeto

1. **Instalar Dependências** : Certifique-se de ter as bibliotecas necessárias instaladas (`scrapy`, `pandas`, `sqlite3`).
2. **Executar o Spider** : Navegue até o diretório do projeto e execute o comando `scrapy crawl mercadolivre` para iniciar a coleta de dados.
3. **Processar os Dados** : Após a coleta, execute o script `data_transformation.py` para processar e salvar os dados no banco de dados SQLite.

#### Dependências e Versões Necessárias

Os softwares e bibliotecas utilizados no projetos tinham a seguintes versões:

* Python - Versão: 3.12.4
* Pandas - Versão: 2.2.2
* Scrapy - Versão: 2.11.2
* SQLite - Versão: 3.41.2

**Obs:** para mais detalhes consulte o aquivo "requirements.txt"

**Links relacionados:**

* [Debian Linux](https://www.debian.org/index.pt.html)
* [VSCode](https://code.visualstudio.com/)
* [Python](https://www.python.org/)
* [Jupyter](https://jupyter.org/)
* [Pandas](https://pandas.pydata.org/)
* [Scrapy](https://scrapy.org/)
* [SQLite](https://www.sqlite.org/)
* [Git](https://git-scm.com/)

## Problemas enfrentados

O código poderá enfrentar problemas ao ser executado utilizando versões diferentes de linguagem e bibliotecas. Certifique-se de que as versões listadas no item "Dependências e Versões Necessárias" estão corretamente instaladas.

Caso já exista um ambiente de desenvolvimento com versões diferentes em uso na máquina utilizada, uma boa alternativa seria a criação de uma ambiente virtual de desenvolvimento. Em caso de dúvida, segue o link da documentação.
[Ambientes virtuais e pacotes](https://docs.python.org/pt-br/3/tutorial/venv.html)

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests no repositório do projeto.

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](https://github.com/thaleswillreis/Data_Pipeline_Web_Scraping/blob/main/LICEN%C3%87A_PT-BR.md) para mais detalhes.
