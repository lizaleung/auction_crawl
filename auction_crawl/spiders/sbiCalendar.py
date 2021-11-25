from datetime import datetime

import scrapy
from bs4 import BeautifulSoup

from auction_crawl.items import SbiCalendarItem, SbiCalendarDetail
import re


class SbiCalendarSpider(scrapy.Spider):
    name = 'sbiCalendar'
    allowed_domains = ['sbiartauction.co.jp']

    start_urls = ['https://www.sbiartauction.co.jp/en/calendar/']
    folder_name = "sbi/calendar"

    def parse(self, response, *args, **kwargs):
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all(class_='cla-content-item')
        for item in items:
            try:
                dtd = item.find(class_="cla-date-d").text
            except:
                import pdb
                pdb.set_trace()
            d1 = dtd.split("-")[0].strip()
            d2 = dtd.split("-")[-1].strip() if len(dtd.split("-")) > 1 else d1
            dtmy = item.find(class_="cla-date-my").text
            dtm = datetime.strptime(dtmy, "%B %Y")
            start_date = dtm.strftime("%Y-%m-") + d1
            end_date = dtm.strftime("%Y-%m-") + d2
            title = item.find(class_="cla-content-title").text
            url = \
                item.find("a",
                          attrs={"href": re.compile(r"https://www.sbiartauction.co.jp/auction/catalogue/\d+")}).attrs[
                    "href"]
            yield SbiCalendarItem(title=title, url=url, start_date=start_date, end_date=end_date)
            yield scrapy.Request(url, self.parser_list_detail,
                                 meta={"data": {"start_date": start_date, "end_date": end_date}})

    def parser_list_detail(self, response, *args, **kwargs):
        lots = re.findall(r'https://www.sbiartauction.co.jp/auction/detail/\d+/\d+', response.text)
        for lot in lots:
            yield scrapy.Request(lot, self.parser_detail, meta={"data": response.meta["data"]})

    def parser_detail(self, response, *args, **kwargs):
        soup = BeautifulSoup(response.text, 'html.parser')
        auction_id = soup.find("input", attrs={"name": "auc_id"}).attrs["value"]
        lot_no = soup.find("input", attrs={"name": "lot_no"}).attrs["value"]
        odc_viewr_Lname = soup.find(class_='odc-viewr-Lname').text
        odc_viewr_Sname = soup.find(class_="odc-viewr-Sname").text
        odc_di_read = soup.find(class_='odc-di-read').text
        est = soup.find(class_='odc-detail-estimate').text.replace('Estimate', '')
        try:
            est_small = soup.find(class_='lld-info_estimate_small').text
        except:
            est_small = None
        read = soup.find(class_='odc-condition').find(class_='odc-di-read').text
        img = soup.find(class_="odc-viewr-display").find("img").attrs["src"]
        start_date = response.meta["data"]["start_date"]
        end_date = response.meta["data"]["end_date"]
        yield SbiCalendarDetail(start_date=start_date, end_date=end_date,url=response.url, auction_id=auction_id, lot_no=lot_no,
                                odc_viewr_Sname=odc_viewr_Sname, odc_viewr_Lname=odc_viewr_Lname,
                                odc_di_read=odc_di_read, est=est, est_small=est_small, read=read, img=img)
