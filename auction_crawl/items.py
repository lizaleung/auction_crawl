# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ChristiesAuctionItem(scrapy.Item):
    event_id = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    title_txt = scrapy.Field()
    landing_url = scrapy.Field()
    location_txt = scrapy.Field()
    sale_total_value_txt = scrapy.Field()
    subtitle_txt = scrapy.Field()
    analytics_id = scrapy.Field()


class ChristiesLotItem(scrapy.Item):
    end_date = scrapy.Field()
    landing_url = scrapy.Field()
    event_id = scrapy.Field()
    object_id = scrapy.Field()
    url = scrapy.Field()
    image_src = scrapy.Field()
    consigner_information = scrapy.Field()
    title_secondary_txt = scrapy.Field()
    title_primary_txt = scrapy.Field()
    provenance = scrapy.Field()
    price_realised_txt = scrapy.Field()
    estimate_txt = scrapy.Field()
    description_txt = scrapy.Field()
    lot_id_txt = scrapy.Field()