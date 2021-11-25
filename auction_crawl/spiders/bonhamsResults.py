import json
import re

import scrapy
from bs4 import BeautifulSoup
from scrapy import Request

from auction_crawl.items import BonhamsResultItem, BonhamsResultDetailItem


class BonhamsResultsSpider(scrapy.Spider):
    lot_page_url: str
    name = 'bonhamsResults'
    allowed_domains = ['bonhams.com']
    start_urls = ['http://bonhams.com/']
    folder_name = "bonhams/results"

    def start_requests(self):
        yyyy = self.__dict__.get('yyyy')
        if yyyy:
            self.url = "https://www.bonhams.com/api/v1/search_json/?content=sale&date_range=BT," + yyyy + "-01-01," + yyyy + "-12-31,&exclude_sale_type=3&length=96&randomise=False&page={page}"
        else:
            self.url = "https://www.bonhams.com/api/v1/search_json/?content=sale&date_range=BT&exclude_sale_type=3&length=96&randomise=False&page={page}"
        yield Request(self.url.format(page=1), self.parse, dont_filter=True)

    def parse(self, response, *args, **kwargs):
        self.logger.info(response.url)
        data = json.loads(response.text)
        if not data:
            return
        main_index_page = data["main_index_page"]
        main_index_page_length = data["main_index_page_length"]
        if main_index_page < main_index_page_length:
            yield Request(self.url.format(page=main_index_page + 1), self.parse, dont_filter=True)

        items = data["model_results"]["sale"]["items"]
        for item in items:
            auction_id = item["iSaleNo"]
            title_txt = item["name_text"]
            location_txt = item["location"]
            start_date = item["dtStartUTC"]
            end_date = item["dtEndUTC"]
            bid_online = item["bid_online"]
            url = "https://www.bonhams.com/" + item["url"]
            # 爬取详情 详情中有category url
            to_item = BonhamsResultItem(url=url, auction_id=auction_id, title_txt=title_txt, location_txt=location_txt,
                                        start_date=start_date, end_date=end_date, bid_online=bid_online)
            yield Request("https://www.bonhams.com/auctions/{}/".format(auction_id), self.parse_detail_info,
                          meta={"item": dict(to_item)})
            self.lot_page_url = "https://api01.bonhams.com/api/search/auction/{auction_id}/?page=1&page_size=10000"
            yield Request(self.lot_page_url.format(auction_id=auction_id), self.parse_detail_list,
                          meta={"auction_id": auction_id, "page": 1, "start_date": start_date, "end_date": end_date,
                                "url": url})

    def parse_detail_info(self, response):
        item = response.meta["item"]
        soup = BeautifulSoup(response.text, 'html.parser')
        try:
            catelogue = soup.find(text=re.compile(".+Catalogue.+", re.DOTALL)).parent.attrs["href"]
        except (KeyError, AttributeError):
            catelogue = None
        try:
            e_catelogue_tag = soup.find(text=re.compile(".+E-catalogue.+", re.DOTALL)).parent
            e_catelogue = re.match(r".+(http://issuu.com/Bonhams/docs/bonhams-auction-\d+-en).+",
                                   str(e_catelogue_tag)).group(1)
        except (KeyError, AttributeError):
            e_catelogue = None
        item["catelogue"] = catelogue or e_catelogue or None
        yield BonhamsResultItem(**item)

    def parse_detail_list(self, response):
        auction_id = response.meta["auction_id"]
        data = json.loads(response.text)
        start_date = response.meta["start_date"]
        end_date = response.meta["end_date"]
        #  最多10000 肯定够了
        for item in data["results"]:
            lot_no = item["iSaleLotNo"]
            self.logger.info(lot_no)
            url = response.meta["url"] + "lot/" + str(lot_no)
            title_txt = item["sDesc"]
            online = item["iSaleNo"]["sSaleType"]
            low_estimate = item["dEstimateLow"]
            high_estimate = item["dEstimateHigh"]
            currency = item["sCurrencySymbol"]
            desc = item["sCatalogDesc"]
            footnote_desc = item["footnote_sExtraDesc"]
            img = item["images"][0]["image_url"] if item["images"] else None
            yield BonhamsResultDetailItem(url=url, auction_id=auction_id, lot_no=lot_no, title_txt=title_txt,
                                          online=online, img=img,
                                          start_date=start_date, end_date=end_date,
                                          low_estimate=low_estimate, high_estimate=high_estimate, currency=currency,
                                          desc=desc, footnote_desc=footnote_desc)
