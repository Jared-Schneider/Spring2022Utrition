from elasticsearch import Elasticsearch
from flask import Flask, make_response, request, redirect, session, jsonify
import json
import sys
import configparser
import logging
from DNA_Parser.DNA_Parser import DNAParser
from register.Register import Register, Login
from download.Download import Download
from food_recall.FoodSubmission import Submission

sys.path.insert(0, r"/Users/stuti/Desktop/Utrition/parser")
 # TODO: update this absolute path to be correct for you

# SETUP
app = Flask(__name__)
app.secret_key = 'postgres'
NUM_OF_TOP_RESULTS_TO_RETURN = 5

# To empty the log, run:
# > app_py.log
# in your terminal after navigating to the folder containing the log
logging.basicConfig(filename='app_py.log', encoding='utf-8', level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] --- %(message)s (%(filename)s:%(lineno)s)', datefmt='%Y-%m-%d %H:%M:%S')

log = logging.getLogger('UtritionLogger')

# Database configuration
config = configparser.ConfigParser()
config.read('db.ini')

# Connect to the Elasticsearch server (here, the one running locally)
es = Elasticsearch([
    {
        "host": config['elasticSearch']['host'],  # equiv to localhost
        "port": config['elasticSearch']['port']
    }
])

# Ensure that we can hit the ES server; raise exception if we can't
if not (es.ping()):
    raise Exception(
        "Cannot connect to ElasticSearch server.\nEnsure the ES server "
        "specified in app.py is running and that you can (for example) hit it with curl.")


@app.route('/')
def hello():
    log.debug('Route: /; Function: Hello')
    return make_response(open('static/templates/index.html').read())


#Login page
@app.route('/start', methods=['POST', 'GET'])
def start():
    try:
        # Set recall_id variable
        # This is used to make sure that if a user completes/submits food recall and then goes back to the food recall page, 
        # edits/adds onto their food recall and resubmits that those two submissions aren't counted as different entries and that the new submission 
        # overwrites the old submission
        session['recall_id'] = -1
        if request.method == 'POST':
            
            addUser = Login()
            
            #Login
            user_info= addUser.login(request.form['email'])

            # Set email and session variables
            session['user_id'] = user_info['id']
            session['email'] = request.form['email']
            
            # User not in database. Redirecting to registration page
            if session.get('user_id') == 0:
                log.debug('Route: /start; Function: start; User does not exist. Going to register page')
                return redirect('/#/register')

            # User in database but doesn't have DNA info in database. Redirecting to DNA upload page
            elif user_info['dna'] == -1: 
                log.debug('Route: /start; Function: start; User does not have DNA info')
                return redirect('/#/upload')
            
            # User in database and has DNA info in database. Redirecting to food-recall page
            else: 
                log.debug('Route: /start; Function: start; User both exists and has DNA.')
                return redirect('/#/add-food')

    # Error. Something went wrong. Redirecting to error page
    # Note: Python/Flask did not like it if the URL/method was named 'error'. So the name 'bad' was chosen instead            
    except Exception as e:
        log.debug('Route: /start; Function: start; Something went wrong; Likely on the DB side')
        session['e']=str(e)
        session['nextPage']='Login'
        session['nextURL']= '#/start'
        return redirect('/#/bad')


# Registration page
@app.route('/register', methods=['POST'])
def register():
    try:
        if request.method == 'POST':
            addUser = Register()
            log.debug('Route: /register; Function: register; Attempting registration')

            # Register
            session['user_id'] = addUser.register(request.form['f_name'], request.form['l_name'])
            log.debug('Route: /register; Function: register; Successful registration. Redirecting to DNA upload')
        return redirect('/#/upload')
    
    # Error. Something went wrong. Redirecting to error page
    # Note: Python/Flask did not like it if the URL/method was named 'error'. So the name 'bad' was chosen instead
    except Exception as e:
        log.debug('Route: /register; Function: register; Something went wrong during registration')
        session['e']=str(e)
        session['nextPage']='Login'
        session['nextURL']= '#/start'
        return redirect('/#/bad')


# Used for the registration page to get the user's email
@app.route('/user', methods=['GET', 'PUT'])
def user_email():
    logging.debug('Route: /user; Function: user_email')
    return session['email']


# DNA Upload page
@app.route('/upload', methods=['GET', 'POST'])
def save():
    try:
        if request.method == 'POST':
            log.debug('Route: /upload; Function: save')
            filename = request.files['data'].filename
            log.debug('DNA Filename: %s', filename)
            parser = DNAParser()
            parser.upload(filename)
    
    # Error. Something went wrong. Redirecting to error page
    # Note: Python/Flask did not like it if the URL/method was named 'error'. So the name 'bad' was chosen instead
    except TypeError as e: 
        log.debug('Type Error raised')
        session['e']='File is in an invalid format or does not exist.'
        session['nextPage']='DNA Upload'
        session['nextURL']= '#/upload'
        return redirect('/#/bad')
    
    # Error. Something went wrong. Redirecting to error page
    # Note: Python/Flask did not like it if the URL/method was named 'error'. So the name 'bad' was chosen instead
    except FileNotFoundError as f:
        log.debug("FILE NOT FOUND")
        session['e']='FILE NOT FOUND'
        session['nextPage']='DNA Upload'
        session['nextURL']= '#/upload'
        return redirect('/#/bad')
    
    # Successful upload. Redirecting to food-recall page
    else:
        return redirect('/#/add-food')

# Submitting food-recall information to DB
@app.route('/submit', methods=['PUT'])
def submit():
    log.debug('Route: /submit; Function: Submit')
    
    session['user_food'] = json.loads(request.data)
    food_recall = Submission()
    
    log.debug("Beginning food recall submission")
    
    # Add food recall info to DB
    food_recall.submit_food_recall()
    
    log.debug("Completed food recall submission")
    log.debug("Recall id: %s", str(session.get('recall_id')))
    
    return {'recall_id':str(session.get('recall_id'))}


# Utrition Analysis report download
@app.route('/download')
def download():
    try:
        # TODO: Replace with your path
        with open('/Users/stuti/Desktop/userOutput.html', 'w+') as outputFile:
            report = Download()

            log.debug("Beginning report production")
            report.download(outputFile)
            log.debug("Successfully downloaded output file")

    # Error. Something went wrong. Redirecting to error page
    # Note: Python/Flask did not like it if the URL/method was named 'error'. So the name 'bad' was chosen instead        
    except Exception as e:
        session['e']=str(e)
        session['nextPage']='Add Food'
        session['nextURL']= '#/add-food'
        return redirect('/#/bad')
    
    # Successful download. Redirecting to start page.
    else:
        log.debug("Successful download. Redirecting to start page")
        return redirect('/#/start')

# Error page
# NOTE: when getting value of session, replace session['x'] with session.get('x')
# Note: Python/Flask did not like it if the URL/method was named 'error'. So the name 'bad' was chosen instead
@app.route('/bad', methods=['GET', 'PUT'])
def bad():
    
    log.debug("Error occurred")

    # get session variables
    e = session.get('e')
    nextPage = session.get('nextPage')
    nextURL=session.get('nextURL')
    
    # Removes session variables
    session.pop('e')
    session.pop('nextPage')
    session.pop('nextURL')
    
    return jsonify(e=e, nextPage=nextPage, nextURL=nextURL)


    
'''
Route for Elasticsearch component to map end-user's food entry to the units for that food

This route accepts an HTTP POST Request. The POST body is assumed to be some JSON that look like this: { 
"search_str": "21553" } Which indicates that the user selected "baby food, apples and chicken" on the front end  

We then use the user's search string to search over our dataset in ES, in the nice fuzzy searching way 
So ES will give us back the best matching food for their search string 
Then we just return the units for that food in some JSON in the HTTP Response Body 
So the returned JSON that gets sent back to the front-end looks like this: 
{
   "units": [
        {
            "food_unit_abbv": "JAR",
            "food_unit_desc": "jar - each 4 OZ",
            "grams_per_food_spec_unit": "113.0"
        },
        {
            "food_unit_abbv": "PK",
            "food_unit_desc": "pack - each 4 OZ",
            "grams_per_food_spec_unit": "113.0"
        }
    ]
}

'''


@app.route('/es-units-lookup', methods=["POST"])
def es_units_lookup():
    log.debug('Route: /es-units-lookup; Function: es-units-lookup')
    sent_data = json.loads(request.data)  # data front-end sent us
    # So go ahead and perform the search
    res = es.search(index="food-data", size=1, body={
        # size is (max) number of results/rows/foods that will be returned. defaults to 10 if unspecified,
        # so note that you MUST pass size if you want to get back more than 10 rows
        "query": {
            "match": {  # the match query is what we use for a fuzzy search :)
                "id": {  # specifies that we are are searching on the id field/column
                    "query": sent_data["search_str"]
                }
            }
        }
    })

    # Units now contains a list of possible units for the selected food
    units = res["hits"]["hits"][0]["_source"]["units"]

    # top5BestMatchingFoods is an array/list of dict object, each dict representing a food
    log.debug("----- Units for Selected Food -----")
    log.debug(json.dumps(units, indent=4))

    ret = {}  # return value we will send back
    matchesWereFound = (len(units) != 0)
    # if len(top5BestMatchingFoods) == 0,  that means ES didn't find any foods that matched the seach string at all

    if matchesWereFound:
        # Initialize dictionary with key value "units" to be an empty list
        ret["units"] = []

        # Append each possible unit for a food to the key: "units"
        for unit in units:
            ret["units"].append(unit)

        # Returning a union of the units for the top 5 best-matching foods
        log.debug("Top foods being returned: %s", json.dumps(ret,indent=4))
        return ret

    else:
        log.debug("NO MATCHES FOUND for the given search string; ie, no foods we have matched it well. So just returning an empty JSON object")
        return ret


'''
Route for Elasticsearch component to map end-user's food entry to that food in the index

This route accepts an HTTP POST Request. The POST body is assumed to be some JSON that look like this: { 
"search_str": "baby food apples" } Which indicates that the user entered "baby food apples" on the front end in the
#foodType searchbox

We then use the user's search string to search over our dataset in ES, in the nice fuzzy searching way 
So ES will give us back the best matching food for their search string 
Then we just return the top 5 best matching foods in some JSON in the HTTP Response Body 
So the returned JSON that gets sent back to the front-end looks like this: 

{
    "foods": [
        {
            "id": "21553",
            "food_desc": "baby food, apples and chicken",
            "units": [
                {
                    "food_unit_abbv": "JAR",
                    "food_unit_desc": "jar - each 4 OZ",
                    "grams_per_food_spec_unit": "113.0"
                },
                {
                    "food_unit_abbv": "PK",
                    "food_unit_desc": "pack - each 4 OZ",
                    "grams_per_food_spec_unit": "113.0"
                }
            ],
            "score": 14.156658
        },
        {
            "id": "16715",
            "food_desc": "baby food, fruit, apples and cherries",
            "units": [
                {
                    "food_unit_abbv": "PCH",
                    "food_unit_desc": "pouch - each 3.5 OZ",
                    "grams_per_food_spec_unit": "99.0"
                },
                {
                    "food_unit_abbv": "JAR",
                    "food_unit_desc": "jar - each 4 OZ",
                    "grams_per_food_spec_unit": "113.0"
                },
                {
                    "food_unit_abbv": "PK",
                    "food_unit_desc": "pack - each 4 OZ",
                    "grams_per_food_spec_unit": "113.0"
                }
            ],
            "score": 13.53286
        },
        {
            "id": "16681",
            "food_desc": "baby food, fruit, apples and blueberries",
            "units": [
                {
                    "food_unit_abbv": "PCH",
                    "food_unit_desc": "pouch - each 3.5 OZ",
                    "grams_per_food_spec_unit": "99.0"
                },
                {
                    "food_unit_abbv": "JAR",
                    "food_unit_desc": "jar - each 4 OZ",
                    "grams_per_food_spec_unit": "113.0"
                },
                {
                    "food_unit_abbv": "PK",
                    "food_unit_desc": "pack - each 4 OZ",
                    "grams_per_food_spec_unit": "113.0"
                }
            ],
            "score": 13.53286
        },
        {
            "id": "111100",
            "food_desc": "baby food, fruit, apples, toddler (dices)",
            "units": [
                {
                    "food_unit_abbv": "CNT",
                    "food_unit_desc": "container - each 4.5 OZ",
                    "grams_per_food_spec_unit": "128.0"
                }
            ],
            "score": 13.53286
        },
        {
            "id": "21337",
            "food_desc": "baby food, fruit, apples and apricots",
            "units": [
                {
                    "food_unit_abbv": "PCH",
                    "food_unit_desc": "pouch - each 3.5 OZ",
                    "grams_per_food_spec_unit": "99.0"
                },
                {
                    "food_unit_abbv": "JAR",
                    "food_unit_desc": "jar - each 4 OZ",
                    "grams_per_food_spec_unit": "113.0"
                },
                {
                    "food_unit_abbv": "PK",
                    "food_unit_desc": "pack - each 4 OZ",
                    "grams_per_food_spec_unit": "113.0"
                }
            ],
            "score": 13.53286
        }
    ]
}

'''


@app.route('/es-food-lookup', methods=["POST"])
def es_food_lookup():
    log.debug('Route: /es-food-lookup; Function: es-food-lookup')
    
    sent_data = json.loads(request.data)  # data front-end sent us
    # So go ahead and perform the search
    res = es.search(index="food-data", size=15, body={
        # size is (max) number of results/rows/foods that will be returned. defaults to 10 if unspecified,
        # so note that you MUST pass size if you want to get back more than 10 rows
        "query": {
            "match": {  # the match query is what we use for a fuzzy search :)
                "food_desc": {  # specifies that we are are searching on the food_name field/column
                    "query": sent_data["search_str"]
                }
            }
        }
    })

    ret = []  # what we will return; it's a list/array of dict's, each dict is a food

    numRowsParsed = 0
    for row in res["hits"]["hits"]:
        parsed_row = row["_source"]
        parsed_row["score"] = row["_score"]  # I figure it's useful to include the score in the returned results too
        parsed_row
        ret.append(parsed_row)
        numRowsParsed += 1
        if numRowsParsed == NUM_OF_TOP_RESULTS_TO_RETURN:
            break

    top5BestMatchingFoods = ret[:NUM_OF_TOP_RESULTS_TO_RETURN]

    # top5BestMatchingFoods is an array/list of dict object, each dict representing a food
    log.debug("-----  Top 5 Best Matching Foods, as returned by Elasticsearch -----")
    log.debug(json.dumps(top5BestMatchingFoods, indent=4))

    ret = {}  # return value we will send back
    matchesWereFound = (len(top5BestMatchingFoods) != 0)
    # if len(top5BestMatchingFoods) == 0,  that means ES didn't find any foods that matched the seach string at all

    if matchesWereFound:
        # Initialize the dictionary key value "foods" to be an empty list
        ret["foods"] = []

        # Add each returned food to the list for key: "foods"
        for food in top5BestMatchingFoods:
            ret["foods"].append(food)

        # print(f"Returning this JSON:\n{json.dumps(ret, indent=4)}")
        return ret

    else:
        # No matches found, return an empty map
        log.debug("NO MATCHES FOUND for the given search string; ie, no foods we have matched it well. So just returning an empty JSON object")
        return ret


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
