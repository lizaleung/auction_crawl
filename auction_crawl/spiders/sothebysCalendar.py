import json
import re

import scrapy
from bs4 import BeautifulSoup
from scrapy import Request

from auction_crawl.items import SothebysCalendarItem, SothebysCalendarDetailItem


class SothebysCalendarSpider(scrapy.Spider):
    name = 'sothebysCalendar'
    allowed_domains = ['sothebys.com']
    folder_name = 'sothebys'
    start_urls = ['https://www.sothebys.com/en/calendar']
    template_url = None

    def start_requests(self):
        f = to = q = f0 = ""
        self.template_url = "https://www.sothebys.com/en/calendar?from=%s&to=%s&q=%s&_requestType=ajax&p={p}&f0=%s" % (
            f, to, q, f0)
        url = self.template_url.format(p=1)
        yield scrapy.Request(url, self.parse, dont_filter=True)

    def parse(self, response, *args, **kwargs):
        page_count = re.match(r".+<span data-page-count>(\d+)</span>.+", response.text, re.DOTALL).group(1)
        page_count = int(page_count)
        for page in range(1, page_count + 1):
            yield Request(self.template_url.format(p=page), callback=self.parse_list, dont_filter=True,
                          priority=100 + page_count - page)

    def parse_list(self, response):
        self.logger.info(response.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        lis = soup.find_all(class_="SearchModule-results-item")
        for li in lis:
            # print(response.url,li.find(class_="Card-title").text)
            href = li.find(class_="Card-info-container").attrs.get("href")
            if not href:
                continue
            yield Request(href, self.parse_detail_list, priority=1000)

    def parse_detail_list(self, response):
        self.logger.info(response.url)
        if "sculpture-to-wear" in response.url:
            return
        if "buy/auction" not in response.url:
            iot_page_urls = response.xpath(
                "//a[@class='NavigationLink' and contains(text(),'lots')]//@href").extract()
            if iot_page_urls:
                yield Request(iot_page_urls[0], self.parse_detail_list, priority=1000)
            return
        auction = response.meta.get("auction")
        try:
            data_dump = re.match(r".+application/json\">(.+?)</script.+", response.text,
                                 re.DOTALL).group(1)
        except AttributeError:
            return
        data = json.loads(data_dump)
        # with open("C:\\Users\\tong\\Desktop\\spider\\sothebys\\iot_list_96.json", "w", encoding='utf-8') as f:
        #     f.write(json.dumps(data, indent=2, ensure_ascii=False))
        auction_json = data["props"]["pageProps"]["auctionJson"]["data"]["auctionDetails"]
        title_txt = auction_json["name"]
        location_txt = auction_json["location"]
        auction_id = auction_json["auctionId"]
        start_date = auction_json["auctionDates"][
            "open_"].replace("T", " ").replace("Z", ":00")
        end_date = data["props"]["pageProps"]["auctionJson"]["data"]["auctionDetails"]["auctionDates"]["end_"].replace(
            "T", " ").replace("Z", ":00") if \
            data["props"]["pageProps"]["auctionJson"]["data"]["auctionDetails"]["auctionDates"]["end_"] else None

        if not auction:
            auction = {
                "url": response.url,
                "auction_id": auction_id,
                "title_txt": title_txt,
                "location_txt": location_txt,
                "start_date": start_date,
                "end_date": end_date

            }
            yield SothebysCalendarItem(**auction)
        # with open("C:\\Users\\tong\\Desktop\\spider\\sothebys\\iot_list.json", "w", encoding='utf-8') as f:
        #     f.write(json.dumps(data, indent=2, ensure_ascii=False))

        all_lot = data["props"]["pageProps"]["lotsJson"]["data"]["auction"]["lots"]
        for next_item in all_lot:
            next_href = "https://www.sothebys.com/" + next_item["url"]
            yield scrapy.Request(next_href, self.parse_lot_detail, meta={"auction": auction}, dont_filter=True,
                                 priority=10000)

    def parse_lot_detail(self, response):
        auction = response.meta["auction"]
        data_dump = re.match(r".+application/json\">(.+?)</script.+", response.text,
                             re.DOTALL).group(1)
        data = json.loads(data_dump)
        auction_json = data["props"]["pageProps"]["auctionJson"]["data"]["auctionDetails"]
        auction_id = auction_json["auctionId"]
        lots_json_list = data["props"]["pageProps"]["lotsJson"]["data"]["auction"]["lots"]
        lot_json = {k["lotId"]: k for k in lots_json_list}
        lot_details_json = data["props"]["pageProps"]["lotDetailsJson"]["data"]["lotDetails"]
        # with open("C:\\Users\\tong\\Desktop\\spider\\sothebys\\iot_detail.json", "w", encoding='utf-8') as f:
        #     f.write(json.dumps(data, indent=2, ensure_ascii=False))
        lot_id = lot_details_json["lotId"]
        lot_number = lot_json[lot_id]["lotNr"]
        title_txt = lot_json[lot_id]["title"]
        objects = lot_json[lot_id]["objectSet"]["objects"]
        creators = objects[0]["object_"]["creators"][0]["creator"]["displayName"] if objects and objects[0]["object_"][
            "creators"] else None
        estimates = lot_json[lot_id]["estimates"]
        low_estimate, high_estimate, currency = estimates["low"], estimates["high"], auction_json["currency"]
        final_price = lot_json[lot_id]["premiums"]["finalPrice"]
        description = lot_details_json["description"]
        catalogue_note = lot_json[lot_id]["catalogueNote"]
        image = auction_json["images"]["images"][0]["renditions"][0]["url"]
        bid = lot_json[lot_id]["numberOfBids"]
        provenance = lot_details_json["items"][0]["provenance"] if lot_details_json["items"] else None
        condition_report = lot_details_json["conditionReport"]
        yield SothebysCalendarDetailItem(auction_id=auction_id, start_date=auction["start_date"],
                                         end_date=auction["end_date"], lot_id=lot_id, lot_number=lot_number,
                                         detail_url=response.url,
                                         title_txt=title_txt, creators=creators,
                                         low_estimate=low_estimate, high_estimate=high_estimate, currency=currency,
                                         final_price=final_price, image=image, bid=bid,
                                         description=description, catalogue_note=catalogue_note,
                                         provenance=provenance, condition_report=condition_report)


"""
https://www.sothebys.com/en/results?from=2021/1/1&to=2021/1/30&f0=1609430400000-1611936000000&q=&_requestType=ajax
https://www.sothebys.com/en/results?from=2021/1/1&to=2021/1/31&f0=1609430400000-1612022400000&q=&_requestType=ajax&p=2
"""
