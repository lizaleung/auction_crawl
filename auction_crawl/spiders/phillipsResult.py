import json
import re
from datetime import datetime
from typing import List

import scrapy
from bs4 import BeautifulSoup
from scrapy import Request

from auction_crawl.items import PhillipsResultListItem, PhillipsResultDetailItem


class PhillipsSpider(scrapy.Spider):
    years: List[str]
    name = 'phillipsResult'
    allowed_domains = ['phillips.com']
    start_urls = ['https://www.phillips.com/auctions/past']
    folder_name = 'phillips'

    def start_requests(self):
        yyyy = self.__dict__.get('yyyy')
        # 获取当前年份
        url = "https://www.phillips.com/auctions/past/filter/Year%3D{}/sort/newest"
        years = ["0001"]
        year = datetime.now().year
        start_year = 2006
        for i in range(start_year, year + 1):
            years.append(str(i))
        if yyyy:
            years = [i for i in years if i == yyyy]
        self.years = years

        if not years:
            return
        for y in years:
            if yyyy and y != yyyy:
                continue
            yield scrapy.Request(url.format(y), self.parse, dont_filter=True)

    def parse(self, response, **kwargs):
        """
            所有的结果全部在一个接口中
        :param response:
        :return:
        """

        data_dump = re.match(r".+PhillipsReact.PastAuctions, (.+?)\), document.getElementById.+", response.text,
                             re.DOTALL).group(1)
        data = json.loads(data_dump)
        # with open("test", 'w', encoding='utf-8') as f:
        #     f.write(json.dumps(data, indent=4))
        for _item in data["data"]:
            auction_id = _item["saleNumber"]
            url = "https://www.phillips.com/auctions/auction/{}".format(auction_id)
            title_txt = _item["auctionTitle"]
            location_txt = _item["locationName"]
            start_date = _item["startDateTimeOffset"][:19].replace("T", " ")
            end_date = _item["endDateTimeOffset"][:19].replace("T", " ") if _item["endDateTimeOffset"] else None
            year = start_date.split("-")[0]
            if year not in self.years:
                continue
            if not end_date or not title_txt:
                continue
            item = PhillipsResultListItem(title_txt=title_txt, start_date=start_date, end_date=end_date,
                                          location_txt=location_txt,
                                          auction_id=auction_id, url=url)
            yield item
            yield scrapy.Request("https://www.phillips.com/auctions/auction/{}".format(auction_id),
                                 self.parse_auction_list,
                                 meta={"auction": item})

    def parse_auction_list(self, response):
        data_dump = re.match(r".+PhillipsReact.AuctionPage, (.+?)\), document.getElementById.+", response.text,
                             re.DOTALL).group(1)
        data = json.loads(data_dump)
        for item in data["auction"]["lots"]:
            detail_link = item["detailLink"]
            yield scrapy.Request(detail_link, self.parse_auction_detail, meta=response.meta)
            # 每个详情的数据都是一样的
            break

    def parse_auction_detail(self, response):
        self.logger.info(response.url)
        data_dump = re.match(r".+PhillipsReact.LotPage, (.+?)\), document.getElementById.+", response.text,
                             re.DOTALL).group(1)
        data = json.loads(data_dump)
        auction = response.meta["auction"]
        for _item in data["auction"]["lots"]:
            image_src = "https://assets.phillips.com/image/upload/t_Website_LotDetailMainImage/v1635797509" + _item[
                "imagePath"]
            detail_link = _item["detailLink"]
            lot_no = _item["lotNumber"]
            maker_name = _item["makerName"]
            description = _item["description"]
            high_estimate = _item["highEstimate"]
            low_estimate = _item["lowEstimate"]
            hammer_plus_bp = _item["hammerPlusBP"]
            provenance = _item["provenance"]
            currency = _item["currencySign"]
            lot = {
                "detail_link": detail_link,
                "lot_no": lot_no,
                "maker_name": maker_name,
                "description": description,
                "high_estimate": high_estimate,
                "image_src": image_src,
                "low_estimate": low_estimate,
                "hammer_plus_bp": hammer_plus_bp,
                "auction_id": auction["auction_id"],
                "provenance": provenance,
                "start_date": auction["start_date"],
                "end_date": auction["end_date"],
                "currency": currency
            }
            yield Request(detail_link, self.parser_lot_detail, meta={"lot": lot})

    def parser_lot_detail(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        detail = soup.find("p", class_="lot-page__lot__additional-info").text
        lot = response.meta["lot"]
        lot["detail"] = detail
        yield PhillipsResultDetailItem(**lot)
