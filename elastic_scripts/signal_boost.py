import ujson as json
import re
import itertools
import csv
import sys
import numpy as np
from elasticsearch import Elasticsearch
from collections import Counter


##########################################################################
# Misc Functions
##########################################################################

stop_words = ['and', 'can', 'or', 'in', 'the', 'at', 'of', 'be', 'more', 'on', 'to', 'are']

def lev(source, target):
    m = len(source)
    n = len(target)
    ld = np.zeros((m+1,n+1))
    ld[0,:] = range(n+1)
    ld[:,0] = range(m+1)
    for j in range(n):
        for i in range(m):
            if source.lower()[i] == target.lower()[j]:
                cost = 0
            else:
                cost = 1
            ld[i+1,j+1] = min([ ld[i, j+1] + 1, ld[i+1, j] + 1, ld[i,j] + cost ])
    return ld[m,n]

def corpus_match(corpus, word):
    return sorted([ check_in((x, lev(x, word)), word) for x in corpus ], key=lambda x: x[1])

def check_in(matched, word):
    ngrams = [ x for x in re.findall('[a-z]+', re.sub('[^\w]', ' ', word.lower())) if x not in stop_words ]
    weight = 0
    for term in ngrams:
        if term in matched[0].lower():
            weight = 100
    return (matched[0], matched[1] - weight)

##########################################################################
# Network Graph Inputs for Gephi
##########################################################################
# with open('extracted_items.json', 'r') as f:
#     signal_boost = json.load(f)

# nodes = {}
# links = []
# for topic in signal_boost:
#     for article in topic.keys():
#         vector = [ x for x in re.findall('[a-z]+',re.sub('[^\w]', ' ', topic[article]).lower()) if x not in stop_words ]
#         cnt_vector = Counter(vector)
#         lnk_vector = list(itertools.combinations(vector, 2))
#         links.extend(lnk_vector)
#         for key in cnt_vector.keys():
#             try:
#                 nodes[key] += cnt_vector[key]
#             except KeyError:
#                 nodes[key] = cnt_vector[key]

# with open('nodes.csv', 'w') as f:
#     w = csv.DictWriter(f, ['id', 'weight'])
#     w.writeheader()
#     w.writerows([ { 'id':x[0], 'weight':x[1] } for x in nodes.items() ])

# with open('links.csv', 'w') as f:
#     w = csv.DictWriter(f, ['source', 'target', 'weight'])
#     w.writeheader()
#     w.writerows([ { 'source': x[0][0], 'target': x[0][1], 'weight': x[1] } for x in Counter(links).items() if x[1] > 20 ])

##########################################################################
# Elasticsearch snapshot load
##########################################################################
es = Elasticsearch([{u'host': u'127.0.0.1', u'port': 9200}])
indices = es.indices.get_aliases().keys()
if 'topics' not in indices:
    sys.exit('The TOPICS index is not present.  Please add it before running this script')

##########################################################################
# Load Topics from ES snapshot
##########################################################################
es_json = es.search(index="topics", body={ "query": { "match_all" : {}}, "size": 1000})

es_topics = [ x['_source']['topic'] for x in es_json['hits']['hits'] ]
es_id = { x['_source']['topic']: x['_id'] for x in es_json['hits']['hits'] }
parents = [ x['_source']['parent'] for x in es_json['hits']['hits'] if 'parent' in x['_source'].keys() ]

##########################################################################
# Load topics from Census Website
##########################################################################
with open('all_topics.json', 'r') as f:
    census_json = json.load(f)
#these are the fields from the scraped content that are combined in order to feed into the content field in the index
description_fields = ['news_items', 'survey_items', 'main_content', 'overview_content',\
    'about_content', 'faq_content', 'definitions_content']
#survey_items - title, description
#news_items - title, description
#definitions_content - only in Public Sector and International Trade

census_topics = [ x['name'] for x in census_json ]
census_description = {}
for topic in census_json:
    print('Scraped Topic: {}'.format(topic['name']))
    description = []
    for field in description_fields:
        try:
            if field == 'news_items':
                if field in topic:
                    subitems = []
                    for news_item in topic[field]:
                        subitems.append(news_item['title'])
                        subitems.append(news_item['description'])
                    description.append(' '.join(subitems))
            elif field == 'survey_items':
                if field in topic:
                    subitems = []
                    for survey_item in topic[field]:
                        subitems.append(news_item['title'])
                        subitems.append(news_item['description'])
                    description.append(' '.join(subitems))
            else:
                description.append(topic[field])
        except KeyError:
            pass
    census_description[topic['name']] = ' '.join(description)

##########################################################################
# Creating simple mapping
# I manually cleaned the mapping after this because no bijective mapping exists
##########################################################################
# matched_topics = {}
# for topic in census_topics:
#     matches = corpus_match(es_topics, topic)
#     if matches[0][1] == -100.0:
#         matched_topics[topic] = matches[0][0]
#     else:
#         matched_topics[topic] = matches[:10]
#
# with open('matched_topics.json', 'w') as f:
#     json.dump(matched_topics, f)

##########################################################################
# Adding fields and content to Elasticsearch
##########################################################################
index_mapping = es.indices.get_mapping(index='topics', doc_type='metadata')
if 'content' not in index_mapping['topics']['mappings']['metadata']['properties']:
    try:
        add_mapping = es.indices.put_mapping(index='topics', doc_type='metadata', body={ "properties" : { "content" : { "type" : "string" }}})
        if add_mapping['acknowledged'] == True:
            print('CONTENT field was added to topics index')
    except Exception as e:
        raise
else:
    print('CONTENT property present in topics index')

with open('matched_topics_manual.json', 'r') as f:
    matched_topics_json = json.load(f)

for topic in matched_topics_json.keys():
    doc_ids = [ es_id[x] for x in matched_topics_json[topic] ]
    for doc_id in doc_ids:
        print('Updating topic: {}'.format(topic))
        es.update(index='topics', doc_type='metadata', id=doc_id, body={'doc':{ 'content': census_description[topic] }})
