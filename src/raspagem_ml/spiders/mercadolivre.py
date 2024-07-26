import scrapy


class MercadolivreSpider(scrapy.Spider):
    name = "mercadolivre"
    start_urls = ["https://lista.mercadolivre.com.br/intelbras"]
    pag_inicial = 1
    pag_final = 10

    def parse(self, response):
        itens = response.css('div.ui-search-result__content')

        for item in itens:

            precos = item.css('span.andes-money-amount__fraction::text').getall()
            centavos = item.css('span.andes-money-amount__cents::text').getall()

            yield {
                'produto': item.css('h2.ui-search-item__title::text').get(),
                'avaliação': item.css('span.ui-search-reviews__rating-number::text').get(),
                'avaliações_qtd': item.css('span.ui-search-reviews__amount::text').get(),
                'preco': precos[1] if len(precos) > 1 else None,
                'preco_centavos': centavos[1] if len(centavos) > 1 else None
            }

        if self.pag_inicial < self.pag_final:
            if proxima_pagina := response.css(
                'li.andes-pagination__button.andes-pagination__button--next a::attr(href)'
            ).get():
                self.pag_inicial += 1
                yield scrapy.Request(url=proxima_pagina, callback=self.parse)
