
## ElasticSearch Setup
1. Install ElasticSearch locally. The latest version of ElasticSearch can be found here (https://github.com/elastic/elasticsearch). The Utrition web application was developed using ElasticSearch version 7.11.0.
2. Spin up the ElasticSearch server locally following the instructions displayed here (https://github.com/elastic/elasticsearch#installation). By default, the ElasticSearch server will run on port 9200. Do not change the default configuration.
3. Index food data from the 2018 NDSR dataset into ElasticSearch using the following steps:
    1. Clone the repository
    2. Navigate to the Utrition folder
    3. Change your working directory to `elasticsearch-config`
    4. Enter the following command into a command terminal:
        - `python3 es-setup.py` *This will index all ~17,000 food records from `food.json` into the ElasticSearch server*
4. Ensure that the data has been indexed properly by running the tests with the following command:
    - `python3 esTests.py`

