#!/usr/bin/python3.5

#Author:        Sasan Bahadaran
#Date:          1/26/17
#Organization:  Commerce Data Service
#Description:   This is a script for scraping topics and related information
#from the census.gov website

import scrapy, datetime, itertools
from census_topic_crawler.items import ParentTopic


class MySpider(scrapy.Spider):
    name = "parent_topics"
    start_urls = [
            'http://www.census.gov',
            'http://www.census.gov/topics/preparedness.html'
    ]

    def parse(self, response):
        print('IN PARSE')
        items = []
        print('URL: {}'.format(response.url))
        if response.url == 'http://www.census.gov/topics/preparedness.html':
            item = ParentTopic()
            item['topic_type'] = 'parent'
            item['name'] = 'Emergency Preparedness'
            item['ID'] = ''
            item['main_content'] = response.xpath('//*[(@id = "landingAboutText")]//p/text()').extract()[0]
            request = scrapy.Request('http://www.census.gov/topics/preparedness/about.html', callback=self.parse_emerg_prep_about, meta={'item': item})
            request.meta['item'] = item
            items.append(item)
            yield request
        else:
            parent_topic_ids = response.xpath('//div[contains(@id, "accd_a") and not (@id="NAV_437121255_0_accd_a")]/@id').extract()
            for parent_topic_id in parent_topic_ids:
                item = ParentTopic()
                item['topic_type'] = 'parent'
                item['ID'] = parent_topic_id
                print('parent_topic_id: {}'.format(parent_topic_id))
                parent_topic_name = response.xpath('//div[@id="'+parent_topic_id+'"]//h4[@class="mobileMenuEntry2"]/text()').extract()[0].strip()
                item['name'] = parent_topic_name
                main_link = response.xpath('//div[@id="'+parent_topic_id[:-8]+'0TabContent"]//a[contains(text(), "Main")]//@href')[0].extract()
                if parent_topic_id in ['NAV_246571490_0_accd_a', 'NAV_1082186784_0_accd_a']:
                    request = scrapy.Request('http://www.census.gov/econ/progoverview.html', callback=self.parse_parent_overview, meta={'item': item})
                elif parent_topic_id == 'NAV_1207455997_0_accd_a':
                    request = scrapy.Request('http://www.census.gov/govs/definitions/', callback=self.parse_parent_definitions, meta={'item': item})
                else:
                    request = scrapy.Request(main_link, callback=self.parse_parent_main, meta={'item': item})
                request.meta['item'] = item
                items.append(item)
                yield request
        return items

    def parse_parent_main(self, response):
        print('IN PARSE_PARENT_MAIN')
        item = response.meta['item']
        link_url = response.url
        if item['ID'] == 'NAV_820029714_0_accd_a':
            main_content = response.xpath('//div[@id="middle-column"]//div[@class="inside"]/p/text()').extract()
            main_content = ''.join(main_content)
            item['main_content'] = main_content
            return scrapy.Request(response.url[:-10]+'reference/definitions/index.html', callback=self.parse_parent_definitions, meta={'item': item})
        else:
            main_content = response.xpath('//div[@id="landingAboutText"]/p/text()').extract()
            main_content = ''.join(main_content)
            item['main_content'] = main_content
            return scrapy.Request(response.url[:-5]+'/about.html', callback=self.parse_parent_about, meta={'item': item})

    def parse_parent_about(self, response):
        print('IN PARSE_PARENT_ABOUT!!!')
        item = response.meta['item']
        diff_struct_pages = ['http://www.census.gov/topics/education/about.html',\
            'http://www.census.gov/topics/families/about.html'\
            'http://www.census.gov/topics/health/about.html']
        about_content = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "textimageText", " " )) and (((count(preceding-sibling::*) + 1) = 1) and parent::*)]//text()').extract()
        item['about_content'] = ''.join(about_content)
        if response.url == 'http://www.census.gov/topics/education/about.html':
            subtopics = response.xpath('//*[(@id = "detailContent")]//li//a[(((count(preceding-sibling::*) + 1) = 1) and parent::*)]/text()').extract()
        else:
            subtopics = response.xpath('//*[(@id = "detailContent")]//ul//a/text()').extract()
        subtopics_items = []
        for subtopic in subtopics:
            st = {}
            st['name'] = subtopic
            subtopic_description = response.xpath('//*[(@id = "detailContent")]//li[contains(a/text(), "'+subtopic+'")]/text()').extract()
            st['description'] = subtopic_description
            subtopics_items.append(st)
        item['about_child_topics'] = subtopics_items
        if response.url == 'http://www.census.gov/topics/income-poverty/about.html':
            next_url = 'http://www.census.gov/topics/income-poverty/news-updates/news.html'
        else:
            next_url = response.url[:-10]+'news.html'
        return scrapy.Request(next_url, callback=self.parse_parent_news, meta={'item': item})

    #only grabbing 2017 news items for now
    def parse_parent_news(self, response):
        print('IN PARSE_PARENT_NEWS')
        item = response.meta['item']
        excepts = ['http://www.census.gov/topics/income-poverty/news-updates/news.html', 'http://www.census.gov/topics/economy/news.html', 'http://www.census.gov/topics/business/news.html']
        articles = response.xpath('//div[@id="listArticlesContainer"]//div[@class="textColumn"]//div[@class="title"]/a/@href').extract()
        articles_items = []
        for article in articles:
            print('ARTICLE: {}'.format(article))
            art = {}
            art['link'] = 'www.census.gov'+article
            art['title'] = response.xpath('//div[@id="listArticlesContainer"]//div[@class="textColumn"]//div[@class="title"]//a[@href="'+article+'"]/@title').extract()[0].strip()
            date = response.xpath('//div[@class="article row nested-row no-gutter"]//div[contains(div/a/@href, "'+article+'")]//div[@class="publishdate"]//text()').extract()[0].strip()
            date = datetime.datetime.strptime(date, '%B %d, %Y').strftime('%m/%d/%Y')
            art['date'] = date
            art['description'] = response.xpath('//div[@class="article row nested-row no-gutter"]//div[contains(div/a/@href, "'+article+'")]//div[@class="abstract hidden-xs"]//text()').extract()[0].strip()
            articles_items.append(art)
        item['news_items'] = articles_items
        if response.url in excepts:
            return item
        else:
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
            if response.url == 'http://www.census.gov/topics/employment/surveys.html':
                sur['description'] = ''
            else:
                sur['description'] = response.xpath('//div[@class="article row nested-row no-gutter"]//div[contains(div/a/@href, "'+survey+'")]//div[@class="abstract hidden-xs"]//text()').extract()[0].strip()
            survey_items.append(sur)
        item['survey_items'] = survey_items
        return item

    def parse_parent_overview(self, response):
        print('IN PARSE_PARENT_OVERVIEW')
        item = response.meta['item']
        overview_content = response.xpath('//*[@id="middle-column"]//p/text() | //*[@id="middle-column"]//h2/text() | //*[@id="middle-column"]//h4/text() | //*[@id="middle-column"]//h3/text() | //*[@id="middle-column"]//strong/text() | //*[@id="middle-column"]//a/text()').extract()
        overview_content = ''.join(overview_content)
        item['overview_content'] = overview_content
        next_url = ''
        if item['ID'] == 'NAV_1082186784_0_accd_a':
            next_url = 'http://www.census.gov/topics/business/news.html'
        else:
            next_url = 'http://www.census.gov/topics/economy/news.html'
        print('ITEM ID: {}'.format(item['ID']))
        return scrapy.Request(next_url, callback=self.parse_parent_news, meta={'item': item})

    def parse_parent_definitions(self, response):
        print('IN PARSE_PARENT_DEFINTIONS')
        item = response.meta['item']
        def_content = response.xpath('//*[(@id = "middle-column")]//li//text()').extract()
        def_content = ''.join(def_content)
        item['definitions_content'] = def_content
        return item

    def parse_emerg_prep_about(self, response):
        print('IN PARSE_EMERG_PREP_ABOUT')
        item = response.meta['item']
        about_content = response.xpath('//*[contains(concat( " ", @class, " " ),\
            concat( " ", "publishdate", " " ))]/text() | //*[contains(concat( " ", @class, " " ),\
            concat( " ", "title", " " ))]//a/text() | //*[(@id = "listArticlesContainer")]\
            //*[contains(concat( " ", @class, " " ), concat( " ", "hidden-xs", " " ))]/text() |\
            //*[(@id = "detailContent")]//p/text()').extract()
        about_content = ''.join(about_content)
        item['about_content'] = about_content
        return scrapy.Request('http://www.census.gov/topics/preparedness/related-sites.html', callback=self.parse_emerg_prep_related_sites, meta={'item': item})

    def parse_emerg_prep_related_sites(self, response):
        print('IN PARSE_EMERG_PREP_RELATED_SITES')
        item = response.meta['item']
        related_sites = response.xpath('//*[(@id = "listArticlesContainer")]//*[contains(concat( " ", @class, " " ), concat( " ", "hidden-xs", " " ))]/text() | //*[(@id = "listArticlesContainer")]//a/text()').extract()
        related_sites = ''.join(related_sites)
        item['related_sites'] = related_sites
        return scrapy.Request('http://www.census.gov/topics/preparedness/surveys-programs.html', callback=self.parse_parent_survey, meta={'item': item})
