# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ParentTopic(scrapy.Item):
    topic_type = scrapy.Field()
    ID = scrapy.Field()
    name = scrapy.Field()
    link = scrapy.Field()
    main_content = scrapy.Field()
    about_content = scrapy.Field()
    #list of dicts with each containing - name, description
    about_child_topics = scrapy.Field()
    #list of dicts with each containing - date, title, description, link
    news_items = scrapy.Field()
    #list of dicts with each containing - title, description, link
    survey_items = scrapy.Field()
    overview_content = scrapy.Field()
    definitions_content = scrapy.Field()
    related_sites = scrapy.Field()

class ChildTopic(scrapy.Item):
    topic_type = scrapy.Field()
    parent = scrapy.Field()
    link = scrapy.Field()
    name = scrapy.Field()
    main_content = scrapy.Field()
    #related_sites = scrapy.Field()
    about_content = scrapy.Field()
    faq_content = scrapy.Field()
