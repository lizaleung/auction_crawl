from datetime import datetime

import scrapy
from bs4 import BeautifulSoup
from scrapy import Request

from auction_crawl.items import SbiResultItem, SbiResultDetailItem


class SbiResultsSpider(scrapy.Spider):
    name = 'sbiResults'
    allowed_domains = ['sbiartauction.co.jp']
    start_urls = ['https://www.sbiartauction.co.jp/en/results/']
    folder_name = "sbi/results"

    def start_requests(self):
        yyyy = self.__dict__.get('yyyy')
        # 获取当前年份
        url = "https://www.sbiartauction.co.jp/en/results/?date={}"
        if yyyy:
            years = [yyyy]
        else:
            current_year = datetime.now().year
            years = [i for i in range(2015, current_year + 1)]
            years.sort(reverse=True)
        for y in years:
            yield scrapy.Request(url.format(y), self.parse_page_list, dont_filter=True, priority=1)

    def parse_page_list(self, response, *args, **kwargs):
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all(class_="rac-li-body")
        for item in items:
            title = item.find("h3").text
            year = item.find(class_="rac-li-date-y").text
            mm = item.find(class_="rac-li-date-md").find_all("span")[-1].text
            mm_int = datetime.strptime(mm, "%B").strftime("%m")
            days = item.find(class_="rac-li-date-md").find_all("span")[0].text.split("-")
            if len(days) == 2:
                start_day, end_day = int(days[0]), int(days[1])
            else:
                start_day, end_day = int(days[0]), int(days[0])
            start_date = "{}-{}-{}".format(year, mm_int, start_day)
            end_date = "{}-{}-{}".format(year, mm_int, end_day)
            info_head = item.find(class_="rac-li-info-read").find("p").text.splitlines()[0]
            links = item.find_all(class_="h__link")
            result_detail_url = links[0].attrs["href"]
            pdf_url = links[1].attrs["href"]
            uid = result_detail_url.split("/")[-1]
            yield SbiResultItem(
                uid=uid,
                title=title,
                url=result_detail_url,
                pdf_url=pdf_url,
                info_head=info_head,
                start_date=start_date,
                end_date=end_date
            )
            yield Request(result_detail_url, callback=self.parser_auction_list,
                          meta={"start_date": start_date, "end_date": end_date}, priority=100)

    def parser_auction_list(self, response):
        self.logger.info(response.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        lal = soup.find_all(class_="lal-thumb")
        for item in lal:
            href = item.find("a").attrs["href"]
            yield Request(href, callback=self.parser_auction_detail, meta=response.meta, priority=1000)

    def parser_auction_detail(self, response):
        self.logger.info(response.url)
        meta = response.meta
        start_date = meta["start_date"]
        end_date = meta["end_date"]
        detail_url = response.url
        soup = BeautifulSoup(response.text, 'html.parser')
        auction_id = soup.find("input", attrs={"name": "auc_id"}).attrs["value"]
        lot_no = soup.find("input", attrs={"name": "lot_no"}).attrs["value"]
        location_name = soup.find(class_="rdc-viewr-Lname").text
        auth_nm = soup.find(class_="rdc-viewr-Sname").text
        img = soup.find(class_="rdc-viewr-display").find("img").attrs["src"]
        detail = soup.find(class_="rdc-di-read").text
        estimate = soup.find(class_="rdc-detail-estimate").find("span").text
        price = soup.find(class_="rdc-detail-price-num").text
        price_currency = soup.find(class_="rdc-detail-price-currency").text
        detail_condition = soup.find(class_="rdc-detail-condition").text
        yield SbiResultDetailItem(
            start_date=start_date,
            end_date=end_date,
            detail_url=detail_url,
            auction_id=auction_id,
            lot_no=lot_no,
            location_name=location_name,
            auth_nm=auth_nm,
            img=img,
            detail=detail,
            estimate=estimate,
            price=price,
            price_currency=price_currency,
            detail_condition=detail_condition
        )
