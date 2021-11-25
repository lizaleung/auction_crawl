import json
import re

import scrapy
from scrapy import Request

from auction_crawl.items import PhillipsCalendarListItem, PhillipsCalendarDetailItem


class PhillipscalendarSpider(scrapy.Spider):
    name = 'phillipsCalendar'
    allowed_domains = ['phillips.com']
    start_urls = ['https://www.phillips.com/calendar/']
    folder_name = 'phillips/calendar'

    def parse(self, response, *args, **kwargs):
        data_dump = re.match(r".+PhillipsReact.CalendarPage, (.+?)\), document.getElementById.+", response.text,
                             re.DOTALL).group(1)
        data = json.loads(data_dump)
        # with open("D://abc.json", 'w', encoding='utf-8') as f:
        #     f.write(json.dumps(data, indent=4))
        for item in data["data"]:
            auction_id = item["saleNumber"]
            url = "https://www.phillips.com/auctions/auction/{}".format(auction_id)
            location_txt = item["locationName"]
            title_txt = item["auctionTitle"]
            start_date = item["startDateTimeOffset"][:20].replace("T", " ")
            end_date = item["endDateTimeOffset"][:20].replace("T", " ") if item["endDateTimeOffset"] else None
            yield PhillipsCalendarListItem(auction_id=auction_id, start_date=start_date, title_txt=title_txt,
                                           location_txt=location_txt, url=url)

            yield scrapy.Request("https://www.phillips.com/auctions/auction/{}".format(auction_id),
                                 self.parse_auction_list,
                                 meta={"auction_id": auction_id, "start_date": start_date, "end_date": end_date})

    def parse_auction_list(self, response):
        try:
            data_dump = re.match(r".+PhillipsReact.AuctionPage, (.+?)\), document.getElementById.+", response.text,
                                 re.DOTALL).group(1)
        except AttributeError:
            return
        data = json.loads(data_dump)
        for item in data["auction"]["lots"]:
            detail_link = item["detailLink"]
            yield scrapy.Request(detail_link, self.parse_auction_detail, meta=response.meta)
            # 每个详情的数据都是一样的
            break

    def parse_auction_detail(self, response):
        data_dump = re.match(r".+PhillipsReact.LotPage, (.+?)\), document.getElementById.+", response.text,
                             re.DOTALL).group(1)
        data = json.loads(data_dump)
        auction_id = response.meta["auction_id"]
        start_date = response.meta["start_date"]
        end_date = response.meta["end_date"]
        for _item in data["auction"]["lots"]:
            lot_no = _item["lotNumber"]
            self.logger.info("lot:%s" % lot_no)
            image_src = "https://assets.phillips.com/image/upload/t_Website_LotDetailMainImage/v1635797509" + _item[
                "imagePath"]
            detail_link = _item["detailLink"]

            maker_name = _item["makerName"]
            description = _item["description"]
            high_estimate = _item["highEstimate"]
            low_estimate = _item["lowEstimate"]
            hammer_plus_bp = _item["hammerPlusBP"]
            provenance = _item["provenance"]
            currency = _item["currencySign"]
            auctionMobilityAuctionRowId = _item["auctionMobilityAuctionRowId"]
            lot = {
                "detail_link": detail_link,
                "lot_no": lot_no,
                "maker_name": maker_name,
                "description": description,
                "high_estimate": high_estimate,
                "image_src": image_src,
                "low_estimate": low_estimate,
                "hammer_plus_bp": hammer_plus_bp,
                "auction_id": auction_id,
                "provenance": provenance,
                "start_date": start_date,
                "end_date": end_date,
                "currency": currency
            }
            yield Request(f"https://live.phillips.com/widget/lots/{auctionMobilityAuctionRowId}", self.parse_fetch_bid,
                          meta={"lot": lot},dont_filter=True)

    def parse_fetch_bid(self, response):
        self.logger.info(response)
        """
        只为获取bid
        https://live.phillips.com/widget/lots/1-4W41B2
        :param response:
        :return:
        """
        lot = response.meta["lot"]
        data = json.loads(response.text)
        res = {}
        for i in data["result_page"]:
            if i["lot_number"] == lot["lot_no"]:
                res = i
        lot["detail"] = res["description"]
        lot["bids"] = res["live_bid_timed_count"]
        lot["current_bid"] = res["timed_auction_bid"]["amount"]
        yield PhillipsCalendarDetailItem(**lot)
