#!/usr/bin/python3.5

#Author:        Sasan Bahadaran
#Date:          1/26/17
#Organization:  Commerce Data Service
#Description:   This is a script for scraping topics and related information
#from the census.gov website

import scrapy, datetime, itertools
from census_topic_crawler.items import ChildTopic


class MySpider(scrapy.Spider):
    name = "child_topics"
    start_urls = [
            'http://www.census.gov'
            #'http://www.census.gov/topics/preparedness.html'
    ]

    #rules = [Rule(LinkExtractor(allow=['/technology-\d+']), 'parse_story')]

    def parse(self, response):
        print('main page!!!')
        item = ChildTopic()
        item['topic_type'] = 'child'
        item['link'] = response.url
        item['name'] = response.selector.xpath('//h2/text()').extract()[0]
        page_content = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "content_block", " " ))]//text()').extract()
        item['main_content'] = ''.join(page_content)
        item['related_sites'] = ''.join(response.xpath('//*[(@id = "right-column")]//li//text()').extract())
        request = scrapy.Request(response.url+'about/', callback=self.parse_about)
        request.meta['item'] = item
        return request

    def parse_about(self, response):
        print('parse about page!!!!')
        item = response.meta['item']
        page_content = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "content_block", " " ))]//text()').extract()
        item['about_content'] = ''.join(page_content)
        faq = response.xpath('/html/body//a[contains(@href, "faq")]/@href').extract()
        if faq:
            print('FAQ page present')
            request = scrapy.Request(response.url+'faq.html', callback=self.parse_faq)
            request.meta['item'] = item
            return request
        else:
            print('No FAQ page present')
            item['faq_content'] = ''
        return item

    def parse_faq(self, response):
        print('IN FAQ PAGE!!')
        #item = response.request.meta['item']
        item = response.meta['item']
        #item['faq_content'] = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "par parsys", " " ))]').extract()
        #item['faq_content'] = response.xpath('//a/text() | //p/text()').extract()
        #faq_content = ''.join(response.xpath('//i/text() | //div[@class="grid_content_Text"][1]//text()').extract())
        item['faq_content'] = ''.join(response.xpath('//i/text() | //div[@class="grid_content_Text"][1]//text()').extract())
        return item


    # def parse(self, response):
    #     print('IN PARSE')
    #     parent_topic_ids = response.xpath('//div[contains(@id, "accd_a") and not (@id="NAV_437121255_0_accd_a")]/@id').extract()
    #     print('parent_topic_ids: {}'.format(parent_topic_ids))
    #     item = ChildTopic()
    #     child_topics = response.xpath('//div[@id="NAV_30093459_0_accd"]//div[@class="mobileMenuArea3 panel-body"]//div//a//@href').extract()
    #     print('CHILD TOPICS: {}'.format(child_topics))
    #     for child_topic in child_topics:
    #         request = scrapy.Request(child_topic, callback=self.parse_child, meta={'item': item})
    #     #get list of child topics and iterate through that
    #     #determine how to lump child item in with parent item
    #     request.meta['item'] = item
    #     return request
    #
    # def parse_child(self, response):
    #     item = ChildTopic()
    #     #topic_links = response.xpath('//div[@id="'+parent_topic_id+'"]//a/@href').extract()
    #     # for topic_link in topic_links:
    #     #     #call function for topic
    #     #     item['topic_link'] = topic_link
    #     #     print('topic_link: {}'.format(topic_link))
    #     #     topic_name = response.xpath('//a[@href="'+topic_link+'"]/h4/text()')[0].extract()
    #     #     print('topic_name: {}'.format(topic_name))
    #     #     item['topic_link'] = response.url
    #     #     item['topic_main_title'] = response.selector.xpath('//h2/text()').extract()[0]
    #     #     page_content = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "content_block", " " ))]//text()').extract()
    #     #     item['topic_main_content'] = ''.join(page_content)
    #     #     item['topic_related_sites'] = ''.join(response.xpath('//*[(@id = "right-column")]//li//text()').extract())
    #     #     request = scrapy.Request(response.url+'about/', callback=self.parse_about)
    #     #     request.meta['item'] = item
    #     #     return request
    #     #call function for topic
    #     item['topic_type'] = 'child'
    #     link = response.url
    #     item['link'] = link
    #     print('link: {}'.format(link))
    #     item['name'] = response.xpath('//h1/text()')[0].extract()
    #     print('name: {}'.format(response.xpath('//h1/text()')[0].extract()))
    #
    #     #page_content = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "content_block", " " ))]//text()').extract()
    #     # item['main_content'] = ''.join(page_content)
    #     # item['topic_related_sites'] = ''.join(response.xpath('//*[(@id = "right-column")]//li//text()').extract())
    #     request = scrapy.Request(response.url+'about/', callback=self.parse_about)
    #     request.meta['item'] = item
    #     return request
    #
    # def parse_about(self, response):
    #     print('parse about page!!!!')
    #     item = response.meta['item']
    #     item['topic_about_title'] = response.selector.xpath('//h2/text()').extract()[0]
    #     page_content = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "content_block", " " ))]//text()').extract()
    #     item['topic_about_content'] = ''.join(page_content)
    #     faq = response.xpath('/html/body//a[contains(@href, "faq")]/@href').extract()
    #     if faq:
    #         print('FAQ page present')
    #         request = scrapy.Request(response.url+'faq.html', callback=self.parse_faq)
    #         request.meta['item'] = item
    #         return request
    #     else:
    #         print('No FAQ page present')
    #         item['topic_faq_content'] = ''
    #     return item
    #
    # def parse_faq(self, response):
    #     print('IN FAQ PAGE!!')
    #     item = response.meta['item']
    #     item['topic_faq_content'] = ''.join(response.xpath('//i/text() | //div[@class="grid_content_Text"][1]//text()').extract())
    #     return item
