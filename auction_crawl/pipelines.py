# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
import os

from auction_crawl.items import ChristiesAuctionItem, ChristiesLotItem
from auction_crawl.settings import outdir


class AuctionCrawlPipeline:
    def __init__(self):
        self.base_dir = None

    def open_spider(self, spider):
        self.base_dir = "%s/%s" % (outdir, spider.folder_name)
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    @staticmethod
    def check_dir(filename):
        """
            检测文件名目录是否存在 不存在则创建
        :param filename:
        :return:
        """
        file_dir = os.path.dirname(filename)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

    def process_item(self, item, spider):
        # line = json.dumps(dict(item), indent=2, ensure_ascii=False) + "\n"
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        if isinstance(item, ChristiesAuctionItem):
            dt = item["end_date"]
            year = dt.split("-")[0]
            month = dt.split("-")[1]
            filename = os.path.join(self.base_dir, year, "{}{}_auction_list.json".format(year, month))
            self.check_dir(filename)
            # filename christies/results/2021/202101_auction_list.json
            with open(filename, 'a', encoding='utf8') as f:
                f.write(line)
        elif isinstance(item, ChristiesLotItem):
            dt = item["end_date"]
            year = dt.split("-")[0]
            month = dt.split("-")[1]
            day = dt.split("-")[2]
            landing_shot = item["landing_url"].split("/")[-1].split(".")[0]
            filename = os.path.join(self.base_dir, year, "{}{}{}_detail_{}.json".format(year, month, day, landing_shot))
            self.check_dir(filename)
            with open(filename, 'a', encoding='utf8') as f:
                f.write(line)
        return item
