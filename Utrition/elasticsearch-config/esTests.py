


import json # for pretty printing dictionaries
from tabulate import tabulate # for making nice tables
from elasticsearch import Elasticsearch # the actual Elasticsearch Python wrapper clinet :)
                                        # again, all this is really doing is constructing the relevant   
                                        # HTTP Requests for you and firing them off at the ES search server 
                                        # So it's a pretty thin wrapper around the raw HTTP API that Elasticsearch provides itself

   


def pprint(d):
    '''
    pretty prints the given dictionary
    '''
    print(json.dumps(d, indent=4))



from elasticsearch import Elasticsearch

es = Elasticsearch([
    {"host": "127.0.0.1", "port": 9200}
]) # connect up to the ES search server


# test we can connect to the ES search server :)
print(es.ping())


# Setup an index to put our dtta in   (an index is like a table)
# We also define a "mapping" for this index  (a mapping is like a table schema)
# pprint(es.indices.create(index="utrition", body={
#     "mappings": {
#         "properties": {         # remember: properties = fields = columns  (basically)
#             "food_name": {"type": "text"}, # a field/column of type "text" is used for the foodName; this is the type we use when we want to do fuzzy searching on a field/column
#             "food_ID_in_sql_db": {"type": "integer"},
#             "units": {"type": "keyword"}   # you don't need to specify this column as an "array" type or anything. in ES a column can contain multiple values by default. and keyword is just a string type basically 
#         }
#     }
# }))
# Only need to do the above once

# Print out all indices
print(es.cat.indices(v=True))   # v for verbose mode (inlcudes column headers)


# exit()

# Delete an index with the given name
# pprint(es.indices.delete(index="test-index"))


# Index in some documents/rows into our utrition index  :)    ("to index" basically just means "to load". And again index=table)
# data = [
#     {
#         "food_name": "Kellogg's Frosted Flakes cereal",
#         "food_ID_in_sql_db": 234,
#         "units": ["bowl"]
#     }, 
#     {
#         "food_name": "Honey-smoked Bacon",
#         "food_ID_in_sql_db": 683,
#         "units": ["strips"]
#     }, 
#     {
#         "food_name": "Honey-nut cheerios cereal",
#         "food_ID_in_sql_db": 4242,
#         "units": ["bowl"]
#     },  
#     {
#         "food_name": "Honeycrest Apple",
#         "food_ID_in_sql_db": 92524,
#         "units": ["quantity"]
#     },  
# ]
# for i in range(len(data)):
#     pprint(es.index(index="utrition", id=i, body=data[i]))



def print_out_all_rows(es):
    '''
    pretty prints all documents in our utrition index
    Recall documents=rows and index=table though, so basically this pretty prints all rows in our table :)

    es: the es object
    '''

    # the match all query below returns all the documents in an index; so it'd be like a select all in SQL (ie a "SELECT * FROM table")
    res = es.search(index="utrition", body={
        "query": {
            "match_all": {}
        }
    })
    # pprint(res)
    # res is a whole mess of data that ES returns us
    # The code below is basically just to parse out the data we need, and then print it out in a nice table
    
    tabulateArr = []  # this is all the data we'll pass to tabulate to print out nicely. Each element in the arr is a row
    for row in res["hits"]["hits"]:
        Id = row["_id"]
        food_name = row["_source"]["food_name"]
        food_ID_in_sql_db = row["_source"]["food_ID_in_sql_db"]
        units = row["_source"]["units"]
        parsedRow = [Id, food_name, food_ID_in_sql_db, units]
        tabulateArr.append(parsedRow)

    print("                   Data in our Elasticsearch Table/Index:                ")
    print(tabulate(tabulateArr, headers=["_id", "food_name", "food_ID_in_sql_db", "units"], tablefmt="psql"))



# Print out all documents/rows in the utrition index    (again documents=rows, index=table basically)
# print_out_all_rows(es)
print()
print()


def search_for_food(es, searchStr):
    '''
    Given a search string like "frosted flakes kellog's cereal",
     prints out the row/document that best matches that search string (using the awesome fuzzy-searching powers!)

    es = the es object
    '''
    res = es.search(index="utrition", body={
        "query": {
            "match": {   # the match query is what we use for a fuzzy search :)
                "food_name": {  # specifies that we are are searching on the food_name field/column
                    "query": searchStr
                }
            }
        }
    })
    # pprint(res)

    # All of the code below is basically just to print the best-matching row

    # So ES returns us back any row that atleast sorta matched the search string
    # And what it does is it gives each row a "score", which indicates how good a match the row actually was :)
    # And very nicely, it returns all the resultting rows sorted by their score -- so the best matches come first! 
    # So we just grab that best match below:
    bestMatchingRow = res["hits"]["hits"][0]
    # and then parse and print it out
    Id = bestMatchingRow["_id"]
    food_name = bestMatchingRow["_source"]["food_name"]
    food_ID_in_sql_db = bestMatchingRow["_source"]["food_ID_in_sql_db"]
    units = bestMatchingRow["_source"]["units"]

    lnes= tabulate([[Id, food_name, food_ID_in_sql_db, units]], headers=["_id", "food_name", "food_ID_in_sql_db", "units"], tablefmt="psql").split("\n")
    print("                    " + lnes[0])
    print("                    " + lnes[1])
    print("BEST MATCHING ROW = " + lnes[2])
    print("                    " + lnes[3])
    print("                    " + lnes[4])


   



# Search for a row using the awesome fuzzy searching! 
# search_for_food("frosted flakes kellog's cereal")




import time
while True:
    print_out_all_rows(es)
    print()
    searchStr = input("Enter a food to search for (like the end-user would): ")
    search_for_food(es, searchStr)
    print()
    print()
    print()
    print()







