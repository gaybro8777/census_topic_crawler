# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Topic(scrapy.Item):
    #parent_topic_ID = scrapy.Field()
    #parent_topic_name = scrapy.Field()
    #topic_name = scrapy.Field()
    topic_link = scrapy.Field()
    topic_main_title = scrapy.Field()
    topic_main_content = scrapy.Field()
    topic_related_sites = scrapy.Field()
    topic_about_title = scrapy.Field()
    topic_about_content = scrapy.Field()
    topic_faq_content = scrapy.Field()

# class AboutPage(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     name = scrapy.Field()
#     title = scrapy.Field()
#     content = scrapy.Field()
