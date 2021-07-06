import os
import sys
import requests
import re

import scrapy
from scrapy.loader import ItemLoader
# from scraper_api import ScraperAPIClient

from auction_crawl.spiders import utils
from auction_crawl.items import ChristiesItem, ChristiesDetailsItem

import json


# scraperapi_token = os.environ['SCRAPERAPI_TOKEN']
# scraperapi_token = "f81631dc362c696a2a5c51a2e21e9600"

# client = ScraperAPIClient(scraperapi_token)


class ChristiesSpider(scrapy.Spider):

    folder_name = "christies"
        
    def start_requests(self):
        self.log("Set output dir: %s" %utils.outdir)
        urls = self.urls_to_crawl

        for url in urls:
            # url = client.scrapyGet(url)
            yield scrapy.Request(url=url, callback=self.parse)
            # yield scrapy.Request(url=url, callback=self.parse_individual_listing)

    def parse(self, response):

        html_filename = 'html/%s.html' % (self.filename)
        # self.log('Writing html source to file %s' % html_filename)
        # utils.writeToFile(self.folder_name, html_filename, response.body, mode = 'wb')

        self.log('Scrapping %s' %response.url)

        self.log('A               ')

        self.log('A               ')
        self.log('A               ')
        self.log('A               ')
        self.log('A               ')
        print(response)
        for eachElement in response.xpath("//section[contains(@class,'container-fluid chr-event-tile')]"):
            href = eachElement.css("a::attr(href)").extract_first()
            title = eachElement.css("a.chr-event-tile__title ::text").extract()
            event_type = eachElement.css("span.chr-event-tile__subtitle ::text").extract()
            status = eachElement.css("span.chr-event-tile__subtitle ::text").extract()
            date = eachElement.css("div.chr-event-tile__status ::text").extract()  
            location = eachElement.css("div.chr-event-tile__details-footer span.chr-body ::text").extract() 
            print(eachElement)
            print(href)
            print(title)
            print(event_type)
            print(status)
            print(date)
            print(location)

        return(None)

        for eachElement in response.css("article.property-list_item"):
            href = eachElement.css("a::attr(href)").extract_first()
            title = eachElement.css("h2.property-list_item_title ::text").extract()
            title = " ".join([ eachRow.strip() for eachRow in title if eachRow.strip() != "" ])
            price = " ".join(eachElement.css("p.property-list_item_price ::text").extract())
            category = eachElement.css("p.property-list_item_type ::text").extract_first()
            description = eachElement.css("div.property-list_item_description ::text").extract_first()

            # print(title)
            # print(href)
            # print(category)
            # print(price)
            # print(description)

            l = ChristiesItem(
                    title = title,
                    price = price,
                    url = href,
                    category = category,
                    description = description
                    )
            yield l

            request = scrapy.Request(url = href, 
                                 callback=self.parse_individual_listing,
                                 )
            yield request


    def parse_individual_listing(self, response):

        title = response.css("h1.property-detail_title ::text").extract()
        title = " ".join([ eachRow.strip() for eachRow in title if eachRow.strip() != "" ])
        
        suffix = title.replace(" ","")
        html_filename = 'html/%s_%s.html' % (self.filename, suffix)
        # self.log('Writing html source to file %s' % html_filename)
        # utils.writeToFile(self.folder_name, html_filename, response.body, mode = 'wb')

        self.log('Scrapping %s' %response.url)

        listingId = suffix
        url = response.url

        imgs = response.css("div.property-detail_gallery img::attr(src)").extract()
        
        lat = response.xpath("//div[@class='c-map_canvas js-single-map-canvas']/@data-lat").extract_first()
        lng = response.xpath("//div[@class='c-map_canvas js-single-map-canvas']/@data-lng").extract_first()

        description = response.css("div.property-detail_description ::text").extract()
        description = " ".join([ eachVal.strip() for eachVal in description if eachVal.strip() != "" ])

        table = {}

        for eachElement in response.css("div.property-detail_spec_item"):
            label = eachElement.css("div.property-detail_spec_item_heading span.en::text").extract_first()
            value = eachElement.css("div.property-detail_spec_item_content ::text").extract()
            value = " ".join([ eachVal.strip() for eachVal in value if eachVal.strip() != "" ])
            table[label] = value

        size = {}
        size['land'] = table['land size'] if "land size" in table.keys() else ""
        size['building'] = table['building size'] if "building size" in table.keys() else ""

        # print(title)
        # print(imgs)
        # print(lat,lng)
        # print(description)
        # print(table)

        l = ChristiesDetailsItem(
            listingId = listingId,
            title = title,
            url = url,
            location = "%s,%s"%(lat,lng),
            price = table['price'] if "price" in table.keys() else "",
            size = size,
            imgs = imgs,
            details = table
            )

        yield l



class Christies(ChristiesSpider):

    name = "christies"
    filename = "christies"
    filename_individual = "christies"
    # urls_to_crawl = ['https://www.christies.com/calendar']
    urls_to_crawl = ['https://www.christies.com/en/results']
    # https://www.christies.com/en/results


