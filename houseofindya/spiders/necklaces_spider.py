import scrapy
import json
import pandas as pd

class NecklacesSpider(scrapy.Spider):
    name = 'necklaces'
    root = 'https://www.houseofindya.com'
    offset = '/zyra/necklace-sets/cat'
    start_urls = [root+offset]

    def parse(self, response):
        yield scrapy.Request(response.url, callback=self.get_full_page, cb_kwargs=dict(depth=1, urls=[]))
        
    def get_full_page(self, response, depth, urls):
        urls.append(response.url)
        isEnd = response.css('.catgList .catLoadmorecntr a::text').get()!='Load More'
        if isEnd:
            for url in urls:
                yield scrapy.Request(url, callback=self.parse_full_page, dont_filter = True)
        else:
            yield scrapy.Request(self.root+self.offset+'?page='+str(depth), callback=self.get_full_page, cb_kwargs=dict(depth=depth+1, urls=urls))

    def parse_full_page(self, response):
        with open( self.name + '.json', 'w') as f:
            f.write(json.dumps([]))
        necklace_urls = response.css('.catgList #JsonProductList li a::attr(href)').extract()
        for url in necklace_urls:
            url = self.root + url
            yield scrapy.Request(url, callback=self.parse_page2, cb_kwargs=dict( size=len(necklace_urls)))

    def parse_page2(self, response, size):
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
