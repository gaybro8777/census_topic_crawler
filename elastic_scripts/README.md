# census_topic_crawler

![U.S. Census Bureau logo](https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Seal_of_the_United_States_Census_Bureau.svg/240px-Seal_of_the_United_States_Census_Bureau.svg.png)

### Topic Information Loader
This directory contains scripts to load scraped information from the topic crawler into a new field in an existing topic index and query that index to test the results of the changes.  These files are contained in the `elastic_scripts` directory of the repository.

**Note: these scripts are specific to this project and assume that an elasticsearch index (topic) is running with a specific configuration**

#### File Details
`all_topics.json` - is a JSON representation of all of the data gathered from the Census website crawler. *Note* that there are two separate crawlers.  This file concatenates output from each of those crawlers.  However, this file is not contained in the repository due to file size and the fact that the extracted content could change depending on when the spiders are executed.

While many attributes were saved for each topic, only some of them were chosen to be included in the Elasticsearch index. The list of chosen attributes can be found within signal_boost.py as the description_fields.

`matched_topics_manual.json` - maps topics from `all_topics.json` to entries from the `topic` field within the topics Elasticsearch index. The keys on the left are website topics. The values on the right within the arrays are ES topics. An empty array indicates that there was no ES topic appropriate
to list. When modifying this list, you should ensure that the names of topics are represented identically to their source (all casings, typos, and spacings preserved).

`signal_boost.py` - modifies the existing topics index to include a content attribute, and it fills that attribute with details from the Census website. This script relies on all_topics.json and matched_topics_manual.json.

  - To add more content to the index: New JSON entries can be added to all_topics.json. The new entries should model the existing entries as closely as possible with similar attribute names.

  - To modify the text content concatenated into the topics index: The description_fields array can be modified. Additional code may need to be added below to parse the fields correctly.

  - To update the mapping of website topics to ES topics: Add new or modified entries to matched_topics_manual.json.

`query_index.py` - Is a script with command line arguments that provides the capability to test the
generates the `query_output.txt` result file. It has a few command line arguments that can be detailed via --help. You can pass an individual query string, or use a preset list of queries. The execution used to generate query_output.txt is:

`python query_index.py "" -u`

#### Setup and Execution of scripts

1. Update your `config/elasticsearch.yaml` file to support inline scripts:
```
script.inline: true
script.indexed: true
```

2. Execute `signal_boost.py` to load the extracted content into the index.

***Note: This script expects the `all_topics.json` file mentioned above to be in the `elastic_scripts` directory***

3. This step is not required for the main functionality, but is meant to help test the results of the index enhancements.  
