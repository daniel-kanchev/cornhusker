import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from cornhusker.items import Article


class cornhuskerSpider(scrapy.Spider):
    name = 'cornhusker'
    start_urls = ['https://cornhuskerbank.wordpress.com/']
    page = 1

    def parse(self, response):
        links = response.xpath('//h1[@class="entry-title"]/a/@href').getall()
        if links:
            yield from response.follow_all(links, self.parse_article)
            self.page += 1
            next_page = f'https://cornhuskerbank.wordpress.com/page/{self.page}/'
            if next_page:
                yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1[@class="entry-title"]/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//time/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="entry-content"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
