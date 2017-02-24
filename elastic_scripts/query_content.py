import argparse
import re
import pprint
import ujson as json
from elasticsearch import Elasticsearch

pp = pprint.PrettyPrinter(indent=2)
queries = ['income inequality', 'number of households', 'minimum wage', 'disposable income', 'languages spoken in us', 'homeownership rate',\
                'african american population', 'per capita income', 'state and county quick facts', 'educational attainment by state',\
                'race breakdown', 'children in poverty', 'marriage statistics', 'welfare recipients by race', 'interracial marriage statistics',\
                'veterans by state', 'average household type', 'undocumented immigrants 2012', 'domestic violence statistics', 'single parents statistics',\
                'urban and rural population', 'smoking', 'us population by race', 'wealth distribution', 'public transportation', 'gender wage gap',\
                'median household income by state', 'average family size', 'prison population', 'migration data', 'annual survey of manufacturers',\
                'pet ownership', 'housing permits', 'demographic profile', 'current world population', 'literacy rates'
                ]

if __name__=='__main__':
    es = Elasticsearch([{u'host': u'127.0.0.1', u'port': 9200}])
    parser = argparse.ArgumentParser(description='Search against boosted content field.')
    parser.add_argument('-o', action='store_true', default=False, help='Search old fields.')
    parser.add_argument('-f', action='store_true', default=False, help='Return full JSON.')
    parser.add_argument('-c', action='store_true', default=False, help='Print comparison.')
    parser.add_argument('-m', action='store_true', default=False, help='Print mapping.')
    parser.add_argument('-u', action='store_true', default=False, help='use list of queries and output results to file.')
    parser.add_argument('search', action='store', type=str, help='Search string in quotes')
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
    elif args.u:
        file = open('queryoutput.txt', 'w')
        for query in queries:
            topics_old = es.search(index="topics", body={ "query": { "match": { "topic": query } } })
            topics_new = es.search(index="topics", body={ "query": { "match": { "content": query } } })       
            file.write('Search Query: \"{}\"'.format(query)+'\n')
            file.write("Old: %d vs New: %d"%(topics_old["hits"]["total"], topics_new["hits"]["total"])+'\n')
            file.write("\tOld:\n")
            for doc in topics_old["hits"]["hits"]:
                file.write("\t\t%s: %s" % (doc['_id'], doc['_source']['topic'])+'\n')
            file.write("\tNew:\n")
            for doc in topics_new["hits"]["hits"]:
                file.write("\t\t%s: %s" % (doc['_id'], doc['_source']['topic'])+'\n')
        file.close()
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


