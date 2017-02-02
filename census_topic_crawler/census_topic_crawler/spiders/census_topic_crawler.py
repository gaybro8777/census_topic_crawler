#!/usr/bin/python3.5

#Author:        Sasan Bahadaran
#Date:          1/26/17
#Organization:  Commerce Data Service
#Description:   This is a script for scraping topics and related information
#from the census.gov website

import scrapy
from census_topic_crawler.items import Topic


class MySpider(scrapy.Spider):
    name = "census"
    start_urls = [
            'http://www.census.gov/hhes/fertility/',
            'http://www.census.gov/hhes/commuting/'
            #'http://www.census.gov/topics.html',
            #'http://www.census.gov/topics/preparedness.html'
    ]

    #rules = [Rule(LinkExtractor(allow=['/technology-\d+']), 'parse_story')]

    def parse(self, response):
        print('main page!!!')
        item = Topic()
        item['topic_link'] = response.url
        item['topic_main_title'] = response.selector.xpath('//h2/text()').extract()[0]
        page_content = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "content_block", " " ))]//text()').extract()
        item['topic_main_content'] = ''.join(page_content)
        item['topic_related_sites'] = ''.join(response.xpath('//*[(@id = "right-column")]//li//text()').extract())
        request = scrapy.Request(response.url+'about/', callback=self.parse_about)
        request.meta['item'] = item
        return request

    def parse_about(self, response):
        print('parse about page!!!!')
        item = response.meta['item']
        item['topic_about_title'] = response.selector.xpath('//h2/text()').extract()[0]
        page_content = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "content_block", " " ))]//text()').extract()
        item['topic_about_content'] = ''.join(page_content)
        faq = response.xpath('/html/body//a[contains(@href, "faq")]/@href').extract()
        if faq:
            print('FAQ page present')
            request = scrapy.Request(response.url+'faq.html', callback=self.parse_faq)
            request.meta['item'] = item
            return request
        else:
            print('No FAQ page present')
            item['topic_faq_content'] = ''
        return item

    def parse_faq(self, response):
        print('IN FAQ PAGE!!')
        #item = response.request.meta['item']
        item = response.meta['item']
        #item['faq_content'] = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "par parsys", " " ))]').extract()
        #item['faq_content'] = response.xpath('//a/text() | //p/text()').extract()
        #faq_content = ''.join(response.xpath('//i/text() | //div[@class="grid_content_Text"][1]//text()').extract())
        item['topic_faq_content'] = ''.join(response.xpath('//i/text() | //div[@class="grid_content_Text"][1]//text()').extract())
        return item
