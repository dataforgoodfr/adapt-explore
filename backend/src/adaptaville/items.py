
import scrapy

class AdaptavilleItem(scrapy.Item):

    nom = scrapy.Field()
    lat = scrapy.Field()
    lng = scrapy.Field()

    type = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()
    image_url = scrapy.Field()
    aleas = scrapy.Field()
    porteurs = scrapy.Field()
    localisation = scrapy.Field()
    email = scrapy.Field()
    contact = scrapy.Field()
    page_text = scrapy.Field()

    scraping_status = scrapy.Field()
    scraping_error = scrapy.Field()
