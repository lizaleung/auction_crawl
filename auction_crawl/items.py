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


class ChristiesCalendarItem(scrapy.Item):
    event_id = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    title_txt = scrapy.Field()
    url = scrapy.Field()
    location_txt = scrapy.Field()
    on_view_txt = scrapy.Field()
    subtitle_txt = scrapy.Field()


class ChristiesCalendarDetailItem(scrapy.Item):
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    auction_id = scrapy.Field()
    lot_no = scrapy.Field()
    url = scrapy.Field()
    title_txt = scrapy.Field()
    img = scrapy.Field()
    low_estimate = scrapy.Field()
    high_estimate = scrapy.Field()
    current_bid_txt = scrapy.Field()
    bids = scrapy.Field()
    detail = scrapy.Field()


class PhillipsResultListItem(scrapy.Item):
    """
        Phillips 结果列表
    """
    url = scrapy.Field()
    auction_id = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    title_txt = scrapy.Field()
    location_txt = scrapy.Field()


class PhillipsResultDetailItem(scrapy.Item):
    """
        Phillips 结果列表
    """
    auction_id = scrapy.Field()
    detail_link = scrapy.Field()
    lot_no = scrapy.Field()
    image_src = scrapy.Field()
    maker_name = scrapy.Field()
    description = scrapy.Field()
    high_estimate = scrapy.Field()
    low_estimate = scrapy.Field()
    hammer_plus_bp = scrapy.Field()
    provenance = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    currency = scrapy.Field()
    detail = scrapy.Field()


class PhillipsCalendarListItem(scrapy.Item):
    """
        Phillips 结果列表
    """
    url = scrapy.Field()
    auction_id = scrapy.Field()
    start_date = scrapy.Field()
    title_txt = scrapy.Field()
    location_txt = scrapy.Field()


class PhillipsCalendarDetailItem(scrapy.Item):
    """
            Phillips 结果列表
        """
    auction_id = scrapy.Field()
    detail_link = scrapy.Field()
    lot_no = scrapy.Field()
    image_src = scrapy.Field()
    maker_name = scrapy.Field()
    description = scrapy.Field()
    high_estimate = scrapy.Field()
    low_estimate = scrapy.Field()
    hammer_plus_bp = scrapy.Field()
    provenance = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    currency = scrapy.Field()
    detail = scrapy.Field()
    current_bid = scrapy.Field()
    bids = scrapy.Field()


class SothebysResultItem(scrapy.Item):
    url = scrapy.Field()
    auction_id = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    title_txt = scrapy.Field()
    location_txt = scrapy.Field()


class SothebysResultDetailItem(scrapy.Item):
    auction_id = scrapy.Field()
    detail_url = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    lot_id = scrapy.Field()
    lot_number = scrapy.Field()

    title_txt = scrapy.Field()
    creators = scrapy.Field()
    low_estimate = scrapy.Field()
    high_estimate = scrapy.Field()
    currency = scrapy.Field()
    final_price = scrapy.Field()
    description = scrapy.Field()

    catalogue_note = scrapy.Field()
    image = scrapy.Field()
    provenance = scrapy.Field()
    condition_report = scrapy.Field()


class SothebysCalendarItem(scrapy.Item):
    url = scrapy.Field()
    auction_id = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    title_txt = scrapy.Field()
    location_txt = scrapy.Field()


class SothebysCalendarDetailItem(scrapy.Item):
    auction_id = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    lot_id = scrapy.Field()
    lot_number = scrapy.Field()
    detail_url = scrapy.Field()

    title_txt = scrapy.Field()
    creators = scrapy.Field()
    low_estimate = scrapy.Field()
    high_estimate = scrapy.Field()
    currency = scrapy.Field()
    final_price = scrapy.Field()
    description = scrapy.Field()
    bid = scrapy.Field()
    catalogue_note = scrapy.Field()
    image = scrapy.Field()
    provenance = scrapy.Field()
    condition_report = scrapy.Field()


class SbiResultItem(scrapy.Item):
    uid = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    pdf_url = scrapy.Field()
    info_head = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()


class SbiResultDetailItem(scrapy.Item):
    detail_url = scrapy.Field()
    auction_id = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    lot_no = scrapy.Field()
    location_name = scrapy.Field()
    auth_nm = scrapy.Field()
    img = scrapy.Field()
    detail = scrapy.Field()
    estimate = scrapy.Field()
    price = scrapy.Field()
    price_currency = scrapy.Field()
    detail_condition = scrapy.Field()


class SbiCalendarItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()


class SbiCalendarDetail(scrapy.Item):
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    auction_id = scrapy.Field()
    img = scrapy.Field()
    lot_no = scrapy.Field()
    odc_viewr_Sname = scrapy.Field()
    odc_viewr_Lname = scrapy.Field()
    odc_di_read = scrapy.Field()
    est = scrapy.Field()
    est_small = scrapy.Field()
    read = scrapy.Field()
    url = scrapy.Field()

class BonhamsResultItem(scrapy.Item):
    url = scrapy.Field()
    auction_id = scrapy.Field()
    title_txt = scrapy.Field()
    location_txt = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    bid_online = scrapy.Field()
    catelogue = scrapy.Field()


class BonhamsResultDetailItem(scrapy.Item):
    url = scrapy.Field()
    auction_id = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    lot_no = scrapy.Field()
    title_txt = scrapy.Field()
    online = scrapy.Field()
    low_estimate = scrapy.Field()
    high_estimate = scrapy.Field()
    currency = scrapy.Field()
    desc = scrapy.Field()
    img = scrapy.Field()
    footnote_desc = scrapy.Field()


class BonhamsCalendarItem(BonhamsResultItem):
    pass


class BonhamsCalendarDetailItem(BonhamsResultDetailItem):
    pass
