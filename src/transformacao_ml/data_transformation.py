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
