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

