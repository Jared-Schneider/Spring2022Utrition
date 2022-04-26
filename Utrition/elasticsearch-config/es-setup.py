import requests
import json
from elasticsearch import Elasticsearch
from requests.exceptions import HTTPError


def main():
    # Local server hosting ElasticSearch
    url = 'http://localhost:9200/'

    # Try to connect to local host port 9200 and handle any exceptions or errors
    try:
        response = requests.get(url)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        exit()
    except Exception as err:
        print(f'Exception occurred: {err}')
        exit()

    # If we reach here , we were able to connect to the ElasticSearch server running locally

    # So create ElasticSearch object
    es = Elasticsearch([
        {
            "host": "127.0.0.1",  # equiv to localhost above
            "port": 9200
        }
    ])

    if es.ping():
        print("\n---------------Successfully connected to ElasticSearch Server---------------\n")

    print(es.cat.indices(v=True))

    # Read food data from JSON file into a dictionary
    with open('elasticsearch-config/food.json') as f:
        food = json.load(f)

    # Remove indices if they already exist. Indices are being remade and re-seeded with data.
    if es.indices.exists(index='food-data'):
        es.indices.delete(index='food-data')

    # Create mapping to index food data
    es.indices.create(index="food-data", body={
        "mappings": {
            "properties": {
                "id": {"type": "integer"},  # The food id related to a particular food
                "food_desc": {"type": "text"},  # The description for a particular food
                "units": {"type": "object"},  # Nested object containing the array of possible units for the food
                # Note that in ES, columns/fields can actually hold an array of whatever type you declare for the
                # field So the units field here will hold an array of objects, each object being a unit You do not
                # have to do anything to set this up; ES allows by default columns to store an array of values
            }
        }
    })

    print(es.cat.indices(v=True))

    # Index first 25 items from food.json
    for i in range(len(food["food_data"])):
        es.index(index="food-data", id=i, body=food["food_data"][i]["food"])

    print('----------------------ElasticSearch Indexing Complete-------------------------')


if __name__ == "__main__":
    main()
