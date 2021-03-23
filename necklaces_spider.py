import scrapy
import json
import pandas as pd

class NecklacesSpider(scrapy.Spider):
    root = 'https://www.houseofindya.com'
    name = 'necklaces'
    start_urls = ['https://www.houseofindya.com/zyra/necklace-sets/cat']
    def parse(self, response):
        with open( self.name + '.json', 'w') as f:
            f.write(json.dumps([]))
        necklace_urls = response.css('.catgList #JsonProductList li a::attr(href)').extract()
        for url in necklace_urls:
            url = self.root + url
            request = scrapy.Request(url, callback=self.parse_page2, cb_kwargs=dict(url=url, size=len(necklace_urls)))
            yield request
    def parse_page2(self, response, url, size):
        with open( self.name + '.json', 'r+') as f:
            necklace = {}
            necklace['title'] = response.css('.prodRight h1::text').get()
            necklace['price'] = response.css('.prodRight h4 span::text').getall()[1].strip()
            necklace['images'] = response.css('.prodLeft img::attr(data-original)').extract()
            desc = response.css('.prodRight .prodecCntr #tab-1 p::text').extract()
            necklace['description'] = desc[0]+'\n'+desc[1]
            data = json.load(f)
            data.append(necklace)
            f.seek(0)
            f.truncate()
            json.dump(data, f)
            if len(data)==size:
                df = pd.DataFrame.from_dict(data)
                df.to_csv(self.name +'.csv')
