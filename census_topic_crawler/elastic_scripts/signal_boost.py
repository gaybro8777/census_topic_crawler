import ujson as json
import re
import itertools
import csv
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

print(indices)

##########################################################################
# Load Topics from ES snapshot
##########################################################################
with open('es_topics.json', 'r') as f:
    es_json = json.load(f)

es_topics = [ x['_source']['topic'] for x in es_json['hits']['hits'] ]
es_id = { x['_source']['topic']: x['_id'] for x in es_json['hits']['hits'] }
# parents = [ x['_source']['parent'] for x in es_json['hits']['hits'] if 'parent' in x['_source'].keys() ]

##########################################################################
# Load topics from Census Website
##########################################################################
with open('all_topics.json', 'r') as f:
    census_json = json.load(f)

description_fields = ['definitions_content', 'overview_content', 'about_content', 'faq_content']

census_topics = [ x['name'] for x in census_json ]
census_description = {}
for topic in census_json:
    description = []
    for field in description_fields:
        try:
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

# with open('matched_topics.json', 'w') as f:
#     json.dump(matched_topics, f)

##########################################################################
# Adding fields to Elasticsearch
##########################################################################
# with open('matched_topics_manual.json', 'r') as f:
#     matched_json = json.load(f)

# doctype = "metadata"
# for topic in matched_json.keys():
#     doc_ids = [ es_id[x] for x in matched_json[topic] ]
#     for doc_id in doc_ids:
#         es.update(index='topics', doc_type='metadata', id=doc_id, body={"doc":{ "content": census_description[topic] }})