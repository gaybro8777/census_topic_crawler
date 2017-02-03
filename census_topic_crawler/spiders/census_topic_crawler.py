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
            'http://www.census.gov/topics.html',
            #'http://www.census.gov/topics/preparedness.html'
    ]

    #rules = [Rule(LinkExtractor(allow=['/technology-\d+']), 'parse_story')]

    def parse(self, response):
        #get topics
        #use
        item = Topic()
        parent_topic_ids = response.xpath('//div[contains(@id, "accd_a") and not (@id="NAV_437121255_0_accd_a")]/@id').extract()
        for parent_topic_id in parent_topic_ids:
            parse_parent(parent_topic_id)
            item['parent_topic_ID'] = parent_topic_id
            print('parent_topic_id: {}'.format(parent_topic_id))
            parent_topic_name = response.xpath('//div[@id="'+parent_topic_id+'"]//h4[@class="mobileMenuEntry2"]/text()').extract()[0].strip()
            print('parent_topic_name: {}'.format(parent_topic_name))
            item['parent_topic_name'] = parent_topic_name
            topic_links = response.xpath('//div[@id="'+parent_topic_id[:-2]+'"]//a/@href').extract()
            for topic_link in topic_links:
                #call function for topic
                item['topic_link'] = topic_link
                print('topic_link: {}'.format(topic_link))
                topic_name = response.xpath('//a[@href="'+topic_link+'"]/h4/text()')[0].extract()
                print('topic_name: {}'.format(topic_name))
                #dig into link for topic_name
                #parse_topic

    def parse_parent(parent_topic_id):
        



        # item['topic_link'] = response.url
        # item['topic_main_title'] = response.selector.xpath('//h2/text()').extract()[0]
        # page_content = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "content_block", " " ))]//text()').extract()
        # item['topic_main_content'] = ''.join(page_content)
        # item['topic_related_sites'] = ''.join(response.xpath('//*[(@id = "right-column")]//li//text()').extract())
        # request = scrapy.Request(response.url+'about/', callback=self.parse_about)
        # request.meta['item'] = item
        # return request

    #def parse_parent(self, response):


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
        item = response.meta['item']
        item['topic_faq_content'] = ''.join(response.xpath('//i/text() | //div[@class="grid_content_Text"][1]//text()').extract())
        return item
