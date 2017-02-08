#!/usr/bin/python3.5

#Author:        Sasan Bahadaran
#Date:          1/26/17
#Organization:  Commerce Data Service
#Description:   This is a script for scraping topics and related information
#from the census.gov website

import scrapy, datetime, itertools
from census_topic_crawler.items import ParentTopic, ChildTopic


class MySpider(scrapy.Spider):
    name = "census"
    start_urls = [
            'http://www.census.gov/topics.html'
            #'http://www.census.gov/topics/preparedness.html'
    ]

    #rules = [Rule(LinkExtractor(allow=['/technology-\d+']), 'parse_story')]

    def parse(self, response):
        print('IN PARSE')
        parent_topic_ids = response.xpath('//div[contains(@id, "accd_a") and not (@id="NAV_437121255_0_accd_a")]/@id').extract()
        item = ParentTopic()
        print('parent_topic_ids: {}'.format(parent_topic_ids))
        for parent_topic_id in itertools.islice(parent_topic_ids, 0, 2):
            print('IN FOR!!!!!!')
            item['topic_type'] = 'parent'
            item['ID'] = parent_topic_id
            print('parent_topic_id: {}'.format(parent_topic_id))
            parent_topic_name = response.xpath('//div[@id="'+parent_topic_id+'"]//h4[@class="mobileMenuEntry2"]/text()').extract()[0].strip()
            print('parent_topic_name: {}'.format(parent_topic_name))
            item['name'] = parent_topic_name
            main_link = response.xpath('//div[@id="'+parent_topic_id[:-8]+'0TabContent"]//a[contains(text(), "Main")]//@href')[0].extract()
            print('main_link: {}'.format(main_link))
            request = scrapy.Request(main_link, callback=self.parse_parent_main, meta={'item': item})
            request.meta['item'] = item
            print('HEYYYYYYYY!!!!!!!!!!!!!!!!!!!!!!!!')
            #get list of child topics and iterate through that
            #determine how to lump child item in with parent item
        return request

    def parse_parent_main(self, response):
        print('IN PARSE_PARENT_MAIN')
        item = response.meta['item']
        item['main_content'] = response.xpath('//div[@id="landingAboutText"]/p/text()')[0].extract()
        print('main_content: {}'.format(response.xpath('//div[@id="landingAboutText"]/p/text()')[0].extract()))
        return scrapy.Request(response.url[:-5]+'/about.html', callback=self.parse_parent_about, meta={'item': item})

    def parse_parent_about(self, response):
        print('IN PARSE_PARENT_ABOUT!!!')
        item = response.meta['item']
        about_content = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "textimageText", " " )) and (((count(preceding-sibling::*) + 1) = 1) and parent::*)]//text()').extract()
        item['about_content'] = ''.join(about_content)
        subtopics = response.xpath('//*[(@id = "detailContent")]//ul//a/text()').extract()
        subtopics_items = []
        for subtopic in subtopics:
            st = {}
            st['name'] = subtopic
            subtopic_description = response.xpath('//*[(@id = "detailContent")]//li[contains(a/text(), "'+subtopic+'")]//text()').extract()[1]
            st['description'] = subtopic_description
            subtopics_items.append(st)
        item['about_child_topics'] = subtopics_items
        return scrapy.Request(response.url[:-10]+'news.html', callback=self.parse_parent_news, meta={'item': item})

    #only grabbing 2017 news items for now
    def parse_parent_news(self, response):
        print('IN PARSE_PARENT_NEWS')
        item = response.meta['item']
        articles = response.xpath('//div[@id="listArticlesContainer"]//div[@class="textColumn"]//div[@class="title"]/a/@href').extract()
        articles_items = []
        for article in articles:
            art = {}
            art['link'] = 'www.census.gov'+article
            art['title'] = response.xpath('//div[@id="listArticlesContainer"]//div[@class="textColumn"]//div[@class="title"]//a[@href="'+article+'"]/@title').extract()[0].strip()
            date = response.xpath('//div[@class="article row nested-row no-gutter"]//div[contains(div/a/@href, "'+article+'")]//div[@class="publishdate"]//text()').extract()[0].strip()
            date = datetime.datetime.strptime(date, '%B %d, %Y').strftime('%m/%d/%Y')
            art['date'] = date
            art['description'] = response.xpath('//div[@class="article row nested-row no-gutter"]//div[contains(div/a/@href, "'+article+'")]//div[@class="abstract hidden-xs"]//text()').extract()[0].strip()
            articles_items.append(art)
        item['news_items'] = articles_items
        return scrapy.Request(response.url[:-10]+'/surveys.html', callback=self.parse_parent_survey, meta={'item': item})

    def parse_parent_survey(self, response):
        print('IN PARSE_PARENT_SURVEY')
        item = response.meta['item']
        surveys = response.xpath('//div[@id="listArticlesContainer"]//div[@class="textColumn"]//div[@class="title"]/a/@href').extract()
        survey_items = []
        for survey in surveys:
            sur = {}
            sur['link'] = survey
            sur['title'] = response.xpath('//div[@id="listArticlesContainer"]//div[@class="textColumn"]//div[@class="title"]//a[@href="'+survey+'"]/@title').extract()[0].strip()
            sur['description'] = response.xpath('//div[@class="article row nested-row no-gutter"]//div[contains(div/a/@href, "'+survey+'")]//div[@class="abstract hidden-xs"]//text()').extract()[0].strip()
            survey_items.append(sur)
        item['survey_items'] = survey_items
        return item

    def parse_child(self, response):
        item = ChildTopic()
        topic_links = response.xpath('//div[@id="'+parent_topic_id+'"]//a/@href').extract()
        for topic_link in topic_links:
            #call function for topic
            item['topic_link'] = topic_link
            print('topic_link: {}'.format(topic_link))
            topic_name = response.xpath('//a[@href="'+topic_link+'"]/h4/text()')[0].extract()
            print('topic_name: {}'.format(topic_name))
            item['topic_link'] = response.url
            item['topic_main_title'] = response.selector.xpath('//h2/text()').extract()[0]
            page_content = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "content_block", " " ))]//text()').extract()
            item['topic_main_content'] = ''.join(page_content)
            item['topic_related_sites'] = ''.join(response.xpath('//*[(@id = "right-column")]//li//text()').extract())
            request = scrapy.Request(response.url+'about/', callback=self.parse_about)
            request.meta['item'] = item
            #dig into link for topic_name
            #parse_topic
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
        item = response.meta['item']
        item['topic_faq_content'] = ''.join(response.xpath('//i/text() | //div[@class="grid_content_Text"][1]//text()').extract())
        return item
