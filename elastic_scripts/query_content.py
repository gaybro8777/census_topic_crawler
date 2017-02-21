import argparse
import re
import pprint
import ujson as json
from elasticsearch import Elasticsearch

pp = pprint.PrettyPrinter(indent=2)

if __name__=='__main__':
    es = Elasticsearch([{u'host': u'127.0.0.1', u'port': 9200}])
    parser = argparse.ArgumentParser(description='Search against boosted content field.')
    parser.add_argument('search', action='store', type=str, help='Search string')
    parser.add_argument('-o', action='store_true', default=False, help='Search old fields.')
    parser.add_argument('-f', action='store_true', default=False, help='Return full JSON.')
    parser.add_argument('-c', action='store_true', default=False, help='Print comparison.')
    parser.add_argument('-m', action='store_true', default=False, help='Print mapping.')
    args = parser.parse_args()
    if args.o:
        topics = es.search(index="topics", body={ "query": { "match": { "topic": args.search } } })
        if args.f:
            for result in topics['hits']['hits']:
                result['_source'].pop('content')
            pp.pprint(topics)
        else:
            for doc in topics["hits"]["hits"]:
                print("%s: %s" % (doc['_id'], doc['_source']['topic']))
    elif args.c:
        topics_old = es.search(index="topics", body={ "query": { "match": { "topic": args.search } } })
        topics_new = es.search(index="topics", body={ "query": { "match": { "content": args.search } } })       
        print("Old: %d vs New: %d"%(topics_old["hits"]["total"], topics_new["hits"]["total"]))
        print("\tOld:")
        for doc in topics_old["hits"]["hits"]:
            print("\t\t%s: %s" % (doc['_id'], doc['_source']['topic']))
        print("\tNew:")
        for doc in topics_new["hits"]["hits"]:
            print("\t\t%s: %s" % (doc['_id'], doc['_source']['topic']))
    elif args.f:
        topics = es.search(index="topics", body={ "query": { "match": { "content": args.search } } })
        pp.pprint(topics)
        # for doc in topics["hits"]["hits"]:
        #     print("%s: %s" % (doc['_id'], doc['_source']['topic']))
    elif args.m:
        with open('matched_topics_manual.json', 'r') as f:
            mapping = json.load(f)
        pp.pprint(mapping)
    else:
        topics = es.search(index="topics", body={ "query": { "match": { "content": args.search } } })
        for doc in topics["hits"]["hits"]:
            print("%s: %s" % (doc['_id'], doc['_source']['topic']))


