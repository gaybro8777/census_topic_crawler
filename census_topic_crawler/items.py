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
    #survey_title = scrapy.Field()
    #survey_content = scrapy.Field()

class ChildTopic(scrapy.Item):
    #parent_topic_ID = scrapy.Field()
    #parent_topic_name = scrapy.Field()
    #topic_type = scrapy.Field()
    #topic_name = scrapy.Field()
    #topic_link = scrapy.Field()
    topic_type = scrapy.Field()
    link = scrapy.Field()
    main_title = scrapy.Field()
    main_content = scrapy.Field()
    related_sites = scrapy.Field()
    about_title = scrapy.Field()
    about_content = scrapy.Field()
    topic_faq_content = scrapy.Field()

# #for parent topic about page. One item for each child topic
# class ParentAboutChildTopics(scrapy.Item):
#     child_topic_name = scrapy.Field()
#     child_topic_description = scrapy.Field()

#for parent topic news page.  One item for each article
# class ParentNewsArticle(scrapy.Item):
#     news_article_year = scrapy.Field()
#     news_article_title = scrapy.Field()
#     news_article_description = scrapy.Field()
