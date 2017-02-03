# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Topic(scrapy.Item):
    parent_topic_ID = scrapy.Field()
    parent_topic_name = scrapy.Field()
    topic_type = scrapy.Field()
    topic_name = scrapy.Field()
    topic_link = scrapy.Field()
    main_title = scrapy.Field()
    main_content = scrapy.Field()
    related_sites = scrapy.Field()
    about_title = scrapy.Field()
    about_content = scrapy.Field()
    topic_faq_content = scrapy.Field()

#class AboutsubTopic(scrapy.Item):

#parent_topic_about_title
#parent_topic_about_content
#parent_topic_about_subtopic (need a new item per with title and description)

# class AboutPage(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     name = scrapy.Field()
#     title = scrapy.Field()
#     content = scrapy.Field()
