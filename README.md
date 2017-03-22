# census_topic_crawler

![U.S. Census Bureau logo](https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Seal_of_the_United_States_Census_Bureau.svg/240px-Seal_of_the_United_States_Census_Bureau.svg.png)


This project attempts to get relevant information about [Census website topics](https://census.gov/topics) and enhance a elasticsearch index that contains a set of similar topic names.

Specifically, there are two main areas of this repository.  The first is:

### Topic Crawler
A spider for crawling Census website topic pages in order to grab relevant information and output that into a formatted JSON document.

There are two spiders (crawlers) that for crawling the Census topic pages.
- parent_topics (filename: `census_topic_crawler.py`)
- child_topics (filename: `census_child_topic_crawler.py`)

In order to execute each of these spiders, run the following command in the base folder of the repository:

`scrapy crawl [name of spider] -o [name of output file] -t json`

When the above command is executed, the output will be written to the specified filename.

**Note: the format of the site may change.  If the layout changes, it is not guaranteed that this bot completely execute without errors.**

### Topic Information Loader
Some scripts to load that information into a new field in an existing topic index and query that index to test the results of the changes.  These files are contained in the `elastic_scripts` directory of the repository (along with an additional README).
