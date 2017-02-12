#!/usr/bin/python3.5

#Author:        Sasan Bahadaran
#Date:          1/26/17
#Organization:  Commerce Data Service
#Description:   This is a script for scraping topics and related information
#from the census.gov website

import scrapy, datetime, itertools, requests
from census_topic_crawler.items import ChildTopic


class MySpider(scrapy.Spider):
    name = "child_topics"
    start_urls = [
            'http://www.census.gov/topics/population.html',
            #'http://www.census.gov/topics/education.html'
            #'http://www.census.gov/topics/employment.html'
            #'http://www.census.gov/topics/families.html',
            #'http://www.census.gov/topics/health.html',
            #'http://www.census.gov/topics/income-poverty.html'
            # #'http://www.census.gov/housing/',
    ]

    def parse(self, response):
        print('IN PARSE')
        items = []
        child_topics = response.xpath('//*[(@id = "bulletedLinkList")]//a/@href').extract()
        print('CHILD TOPICS: {}'.format(child_topics))
        for child_topic in child_topics:
            item = ChildTopic()
            item['parent'] = response.xpath('//h1/text()').extract()[0]
            item['topic_type'] = 'child'
            if child_topic == '/topics/education/school-districts.html':
                full_url = 'http://www.census.gov/did/www/schooldistricts/index.html'
            elif child_topic == '//www.census.gov/population/international/data/hiv/':
                full_url = 'http://www.census.gov/population/international/'
            elif 'www.census.gov' in child_topic:
                if 'http:' in child_topic:
                    if response.url == 'http://www.census.gov/topics/employment.html':
                        full_url = child_topic
                    else:
                        full_url = child_topic
                else:
                    full_url = 'http:'+child_topic
            else:
                full_url = 'http://www.census.gov'+child_topic
            item['link'] = full_url
            item['name'] = response.xpath('//a[@href="'+child_topic+'"]/text()').extract()[0]
            if full_url not in ['http://www.census.gov/topics/education/educational-services.html',
                'http://www.census.gov/govs/apes/',
                'http://www.census.gov/econ/sbo/',
                'http://www.census.gov/topics/income-poverty/public-assistance.html']:
                request = scrapy.Request(full_url,
                    callback=self.parse_child_main,
                    meta={'item': item},
                    dont_filter=True)
                request.meta['item'] = item
                items.append(item)
                yield request
        return items

    def parse_child_main(self, response):
        print('IN PARSE_CHILD_MAIN')
        item = response.meta['item']
        print('RESPONSE URL: {}'.format(response.url))
        if response.url in ['http://www.census.gov/did/www/schooldistricts/data/',
            'http://www.census.gov/did/www/sahie/']:
            main_content = response.xpath('//*[(@id = "middle-column")]//a/text() | //div[@id="middle-column"]//p/text()').extract()
        elif response.url == 'http://www.census.gov/govs/school/':
            main_content = response.xpath('//div[@id="middle-column"]//p/text()').extract()
        elif response.url == 'http://www.census.gov/hhes/school/':
            main_content = response.xpath('//div[@id="middle-column"]//div[@class="inside"]/p/text()').extract()
        elif response.url == 'http://www.census.gov/people/io/':
            main_content = response.xpath('//div[@id="middle-column"]//div[@class="content_block"]/p/text()').extract()
        elif response.url in ['http://www.census.gov/hhes/commuting/data/workathome.html',
            'http://www.census.gov/hhes/povmeas/index.html',
            'http://www.census.gov/hhes/well-being/',
            'http://www.census.gov/did/www/saipe/',
            'http://www.census.gov/did/www/schooldistricts/index.html',
            'http://www.census.gov/hhes/commuting/']:
            main_content = response.xpath('//div[@id="middle-column"]//p/text() | //div[@id="middle-column"]//p/a/text()').extract()
        elif response.url in ['http://www.census.gov/people/disabilityemptab/',
            'http://www.census.gov/people/eeotabulation/',
            'http://www.census.gov/hhes/samesex/',
            'http://www.census.gov/hhes/families/',
            'http://www.census.gov/hhes/fertility/',
            'http://www.census.gov/people/disability/',
            'http://www.census.gov/hhes/well-being/index.html']:
            main_content = response.xpath('//div[@id="middle-column"]//div[@class="content_block"]//p/text() | //div[@id="middle-column"]//div[@class="content_block"]//a/text()').extract()
        elif response.url == 'http://www.census.gov/population/international/':
            main_content = response.xpath('//div[@id="middle-column"]//div[@class="content_block"]//p/text() | //div[@id="middle-column"]//div[@class="content_block"]/a/text()').extract()
        elif response.url == 'http://www.census.gov/population/www/socdemo/grandparents.html':
            main_content = response.xpath('//p[contains(a/text(), "decennial census")]//text()').extract()
        else:
            main_content = response.xpath('//div[@id="landingAboutText"]/p/text()').extract()
        main_content = ''.join(main_content)
        main_content = ' '.join(main_content.split())
        item['main_content'] = main_content

        if response.url.endswith('/'):
            if response.url == 'http://www.census.gov/govs/school/':
                next_url = 'http://www.census.gov/govs/school/about_the_survey.html'
            else:
                next_url = response.url+'about/'
        elif response.url == 'http://www.census.gov/hhes/commuting/data/workathome.html':
            next_url = 'http://www.census.gov/hhes/commuting/about/'
        elif response.url == 'http://www.census.gov/hhes/well-being/index.html':
            next_url = 'http://www.census.gov/hhes/well-being/about/'
        elif response.url == 'http://www.census.gov/hhes/povmeas/index.html':
            next_url = 'http://www.census.gov/hhes/povmeas/about/index.html'
        elif response.url == 'http://www.census.gov/hhes/povmeas/index.html':
            next_url = 'http://www.census.gov/hhes/povmeas/about/index.html'
        elif response.url == 'http://www.census.gov/did/www/saipe/':
            next_url = 'http://www.census.gov/did/www/saipe/about/index.html'
        elif response.url == 'http://www.census.gov/topics/income-poverty.html':
            next_url = 'http://www.census.gov/topics/income-poverty/poverty/about.html'
        elif response.url == 'http://www.census.gov/topics/income-poverty/poverty.html':
            next_url = 'http://www.census.gov/topics/income-poverty/poverty/about.html'
        elif response.url == 'http://www.census.gov/govs/school/':
            next_url = 'http://www.census.gov/govs/school/about_the_survey.html'
        elif response.url == 'http://www.census.gov/topics/education/school-enrollment.html':
            next_url = 'http://www.census.gov/hhes/school/about/index.html'
        else:
            next_url = response.url[:-5]+'/about.html'

        if response.url in ['http://www.census.gov/schools/',
            'http://www.census.gov/did/www/schooldistricts/index.html',
            'http://www.census.gov/hhes/socdemo/marriage/',
            'http://www.census.gov/population/www/socdemo/grandparents.html',
            'http://www.census.gov/hhes/samesex/']:
            return item
        else:
            return scrapy.Request(next_url,
                callback=self.parse_child_about,
                meta={'item': item},
                dont_filter=True)

    def parse_child_about(self, response):
        print('IN PARSE_CHILD_ABOUT')
        item = response.meta['item']
        if response.url == 'http://www.census.gov/people/io/about/':
            about_content = response.xpath('//div[@id="middle-column"]//div[@class="content_block"]/p/text()').extract()
        elif response.url == 'http://www.census.gov/hhes/commuting/about/':
            about_content = response.xpath('//*[(@id = "middle-column")]//p/text() | //*[(@id = "middle-column")]//h3/text()').extract()
        elif response.url == 'http://www.census.gov/people/disabilityemptab/about/':
            about_content = 'This page is forthcoming. Please see the Frequently Asked Questions in the interim.'
        elif response.url in ['http://www.census.gov/population/international/about/',
            'http://www.census.gov/people/eeotabulation/about/',
            'http://www.census.gov/did/www/sahie/about/index.html',
            'http://www.census.gov/did/www/saipe/about/index.html']:
            about_content = response.xpath('//div[@id="middle-column"]//a/text() | //div[@id="middle-column"]//p/text()').extract()
        elif response.url in ['http://www.census.gov/hhes/families/about/',
            'http://www.census.gov/hhes/fertility/about/',
            'http://www.census.gov/people/disability/about/',
            'http://www.census.gov/hhes/povmeas/about/index.html',
            'http://www.census.gov/hhes/well-being/about/']:
            about_content = response.xpath('//div[@id="middle-column"]//a/text() | //div[@id="middle-column"]//p/text() | //div[@id="middle-column"]//text()').extract()
        else:
            about_content = response.xpath('//div[@id="detailContent"]//h3/text() | \
                //div[@id="detailContent"]//p/text() | //div[@id="detailContent"]//a/text() |\
                //div[@id="detailContent"]//b/text()').extract()
        about_content = ''.join(about_content)
        about_content = ' '.join(about_content.split())
        item['about_content'] = about_content
        faq = None
        if response.url not in ['http://www.census.gov/govs/school/about_the_survey.html',
            'http://www.census.gov/topics/income-poverty/poverty/about.html']:
            faq = response.xpath('/html/body//a[contains(@href, "faq")]/@href').extract()
        elif response.url == 'http://www.census.gov/people/eeotabulation/about/':
            faq = ['/people/eeotabulation/about/faq5year.html']
        if faq:
            faq_link = ''
            if faq[0] == 'faq.html':
                faq_link = response.url+faq[0]
            else:
                faq_link = 'http://www.census.gov'+faq[0]
            print('FAQ page present!!!!!!!')
            return scrapy.Request(faq_link,
                callback=self.parse_child_faq,
                meta={'item': item},
                dont_filter=True)
        else:
            print('No FAQ page present')
            return item

    def parse_child_faq(self, response):
        print('IN PARSE_CHILD_FAQ')
        item = response.meta['item']
        if response.url in ['http://www.census.gov/hhes/school/about/faqs.html',
            'http://www.census.gov/hhes/well-being/about/faq.html']:
            faq_content = response.xpath('//*[(@id = "middle-column")]//p/text() | //*[(@id = "middle-column")]//h3/text() | //div[@id ="middle-column"]//a/text()').extract()
        elif response.url in ['http://www.census.gov/people/io/about/faq.html',
            'http://www.census.gov/people/disabilityemptab/about/faq.html']:
            faq_content = response.xpath('//div[@id="middle-column"]//p/text() | //div[@id="middle-column"]//i/text() | //div[@id="middle-column"]//p/a/text()').extract()
        elif response.url == 'http://www.census.gov/hhes/commuting/about/faq.html':
            faq_content = response.xpath('//div[@class="grid_content_detailsStandard grid_slatelink"]//div[@class="grid_content_Text"]/p/text() | //div[@class="grid_content_detailsStandard grid_slatelink"]//i/text() | //div[@class="grid_content_detailsStandard grid_slatelink"]//div[@class="grid_content_Text"]/a/text()').extract()
        elif response.url in ['http://www.census.gov/did/www/sahie/about/faq.html',
            'http://www.census.gov/did/www/saipe/about/faq.html',
            'http://www.census.gov/hhes/veterans/about/faq.html',
            'http://www.census.gov/people/eeotabulation/about/faq5year.html']:
            faq_content = response.xpath('//div[@id="middle-column"]//text()').extract()
        else:
            faq_content = response.xpath('//*[(@id = "detailContent")]//*[(((count(preceding-sibling::*) + 1) = 1) and parent::*)]/text()').extract()
        faq_content = ''.join(faq_content)
        faq_content = ' '.join(faq_content.split())
        item['faq_content'] = faq_content
        return item
