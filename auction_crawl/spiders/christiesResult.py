import json
import re

import scrapy

from auction_crawl.items import ChristiesAuctionItem, ChristiesLotItem


class ChristiesSpiderSpider(scrapy.Spider):
    name = 'christiesResult'
    allowed_domains = ['christies.com']
    start_urls = ['https://www.christies.com/en/results']

    folder_name = 'christies/results'
    """
        -a yyyy=1996
        -a yyyy=2015 -a mm=05
    """

    def parse(self, response, **kwargs):
        """
            通过首页 获取筛选条件  script 15
        :param response:
        :return:
        """
        yyyy = self.__dict__.get('yyyy')
        mm = self.__dict__.get('mm')
        filter_dump = re.match(r".*data: ({.*]}),", response.text, re.DOTALL).group(1)
        filters = json.loads(filter_dump)
        for year_dict in filters["options"]["groups"]["year"]["filters"]:
            year = year_dict["id"]
            if yyyy and yyyy != year: continue
            for month_dict in filters["options"]["groups"]["month"]["filters"]:
                month = month_dict["id"]
                if mm and int(month) != int(mm): continue
                url = "https://www.christies.com/en/results?month={}&year={}".format(month, year)
                request = scrapy.Request(url=url,
                                         callback=self.parse_page,
                                         )
                yield request

    def parse_page(self, response):
        """
            解析页面内容
        :param response:
        :return:
        """
        data_dump = re.match(r".*data: ({\"auction_results_api_endpoint.*]}),", response.text, re.DOTALL).group(1)
        data = json.loads(data_dump)
        for _item in data["events"]:
            item = {
                "analytics_id": _item["analytics_id"].split("-")[-1],
                "subtitle_txt": _item["subtitle_txt"],
                "event_id": _item["event_id"],
                "start_date": _item["start_date"].split("T")[0],
                "end_date": _item["end_date"].split("T")[0],
                "title_txt": _item["title_txt"],
                "landing_url": _item["landing_url"],
                "location_txt": _item["location_txt"],
                "sale_total_value_txt": _item["sale_total_value_txt"]
            }
            yield ChristiesAuctionItem(**item)
            # 拍卖日程
            auction_calendar_url = _item["landing_url"]
            yield scrapy.Request(auction_calendar_url, self.parse_auction_calendar, meta={"auction": item})

    def parse_auction_calendar(self, response):
        """
            解析拍卖日程 获取所有的拍卖商品
        :param response:
        :return:
        """
        # 这里的saleid selenumber  匹配json 数据不稳定 直接匹配最好
        # 获取所有拍卖物品
        total_page = int(re.match(r'.*total_pages\":(\d+),\"show_sort', response.text, re.DOTALL).group(1))
        sale_id = re.match(r'.*saleid\":(.+?),', response.text, re.DOTALL).group(1).replace('"', '')
        sale_number = re.match(r'.*sale_number\":(.+?),', response.text, re.DOTALL).group(1).replace('"', '').replace(
            'null', '')

        for page in range(1, total_page):
            item_page_url = "https://www.christies.com/api/discoverywebsite/auctionpages/lotsearch?action=paging&geocountrycode=HK&language=en&page={page}&pagesize=30&saleid={saleid}&salenumber={salenumber}&saletype=Sale&sortby=lotnumber".format(
                page=page, saleid=sale_id, salenumber=sale_number)
            yield scrapy.Request(item_page_url, self.parse_goods_page, meta=response.meta)

    def parse_goods_page(self, response):
        """
            json 数据解析  寻找商品详情
        :param response:
        :return:
        """
        auction = response.meta["auction"]
        event_id = auction["event_id"]
        template_url = "https://www.christies.com/lot/lot-{object_id}?ldp_breadcrumb=back&intObjectID={object_id}&from=salessummary&lid=1"
        for _item in json.loads(response.text)["lots"]:
            object_id = _item["object_id"]
            item = {
                "landing_url": auction["landing_url"],
                "end_date": auction["end_date"],
                "event_id": event_id,
                "object_id": _item["object_id"],
                "url": _item["url"],
                "image_src": _item["image"]["image_src"],
                "consigner_information": _item["consigner_information"],
                "title_secondary_txt": _item["title_secondary_txt"],
                "title_primary_txt": _item["title_primary_txt"],
                "price_realised_txt": _item["price_realised_txt"],
                "estimate_txt": _item["estimate_txt"],
                "description_txt": _item["description_txt"],
                "lot_id_txt": _item["lot_id_txt"]

            }
            yield scrapy.Request(template_url.format(object_id=object_id), callback=self.parse_goods_detail,
                                 meta={'item': item})

    def parse_goods_detail(self, response):
        item = response.meta["item"]
        try:
            provenance = response.xpath('//div[contains(text(),"Provenance")]/following-sibling::div/span/text()')[
                0].extract()
        except IndexError:
            provenance = None
        item["provenance"] = provenance
        yield ChristiesLotItem(**item)
