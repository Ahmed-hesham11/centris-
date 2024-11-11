import scrapy
from scrapy.selector import Selector
import json
from scrapy_splash import SplashRequest


class ListisSpider(scrapy.Spider):
    name = "listis"
    allowed_domains = ["www.centris.ca", "localhost"]
    position = {"startPosition": 0}
    script='''
            function main(splash, args)
                    assert(splash:go(args.url))
                    assert(splash:wait(0.5))
                    return  splash:html()
                end
            '''
    custom_settings = {
        'OFFSITE_ENABLED': False,
    }
    
    def start_requests(self):
        query = {
            "query": {
                "UseGeographyShapes": 0,
                "Filters": [
                    {
                        "MatchType": "GeographicArea",
                        "Text": "Montérégie",
                        "Id": "RARA16"
                    }
                ],
                "FieldsValues": [
                    {
                        "fieldId": "GeographicArea",
                        "value": "RARA16",
                        "fieldConditionId": "",
                        "valueConditionId": ""
                    },
                    {
                        "fieldId": "Category",
                        "value": "Residential",
                        "fieldConditionId": "",
                        "valueConditionId": ""
                    },
                    {
                        "fieldId": "SellingType",
                        "value": "Rent",
                        "fieldConditionId": "",
                        "valueConditionId": ""
                    },
                    {
                        "fieldId": "LivingArea",
                        "value": "SquareFeet",
                        "fieldConditionId": "IsResidentialNotLot",
                        "valueConditionId": ""
                    },
                    {
                        "fieldId": "LandArea",
                        "value": "SquareFeet",
                        "fieldConditionId": "IsLandArea",
                        "valueConditionId": ""
                    },
                    {
                        "fieldId": "RentPrice",
                        "value": 0,
                        "fieldConditionId": "ForRent",
                        "valueConditionId": ""
                    },
                    {
                        "fieldId": "RentPrice",
                        "value": 999999999999,
                        "fieldConditionId": "ForRent",
                        "valueConditionId": ""
                    }
                ]
            },
            "isHomePage": True
        }

        yield scrapy.Request(
            url="https://www.centris.ca/property/UpdateQuery",
            method="POST",
            body=json.dumps(query),
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
            },
            callback=self.update_query
        )

    def update_query(self, response):
        yield scrapy.Request(
            url="https://www.centris.ca/Property/GetInscriptions",
            method="POST",
            body=json.dumps(self.position),
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
            },
            callback=self.parse
        )

    def parse(self, response):
        resp_dict = json.loads(response.body)
        html = resp_dict.get('d').get('Result').get('html')
        sel= Selector(text=html)
        listings= sel.xpath('//div[@class="property-thumbnail-item thumbnailItem col-12 col-sm-6 col-md-4 col-lg-3"]')
        base_url = "https://www.centris.ca"
        for list in listings:
            category = list.xpath(".//div[@class='category']/div/text()").get().strip()
            address = list.xpath(".//div[@class='address']/div/text()").get().strip()
            price = list.xpath(".//div[@class='price']/meta[2]/@content").get()
            url = list.xpath(".//a[@class='property-thumbnail-summary-link']/@href").get()
            full_url = base_url + url if url else None
            yield SplashRequest(
                url=full_url,
                endpoint='execute',
                callback=self.parse_summary,
                args={
                    'lua_source':self.script,
                    'timeout':200
                },
                meta={
                    'cat':category,
                    'address':address,
                    "price":price,
                    "url":full_url
                }
            )
                    
                

        inscNumberPerPage= resp_dict.get('d').get('Result').get('inscNumberPerPage')
        count= resp_dict.get('d').get('Result').get('count')
        if self.position["startPosition"]<=count:
            self.position["startPosition"]+=inscNumberPerPage
            yield scrapy.Request(
                url="https://www.centris.ca/Property/GetInscriptions",
                 method="POST",
            body=json.dumps(self.position),
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
            },
            callback=self. parse
                
            )
            
    def parse_summary(self,response):
        Year_built=response.xpath(
        "normalize-space(//*[@id='overview']/div[3]/div[1]/div[6]/div[3]/div[2]/span/text())" ).get() or "Not available"
        roomes_number=response.xpath(
        'normalize-space(//*[@id="overview"]/div[3]/div[1]/div[4]/div[2]/text())').get() or "Not specified"
        catagory=response.request.meta['cat']
        address=response.request.meta['address']
        price=response.request.meta['price']
        url=response.request.meta['url']
        yield{
            'catagory':catagory,
            'address':address,
            'price':price,
            #'Year_built':Year_built,#######there is a problem some times return the right value and some times retuen wronge
            'roomes_number':roomes_number,
            'url':url
        }
    