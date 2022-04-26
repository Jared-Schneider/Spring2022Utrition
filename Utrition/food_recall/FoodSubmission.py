#!/usr/bin/python3

import psycopg2
import configparser
from flask import session
import logging

class Submission:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('db.ini')
        self.log = logging.getLogger('UtritionLogger')
        return 

    def submit_food_recall(self):
        # Establish DB Connection
        self.log.debug("Establishing DB Connection")
        with psycopg2.connect(host = self.config['utrition_dna']['host'],database=self.config['utrition_dna']['db'], user=self.config['utrition_dna']['user'], password=self.config['utrition_dna']['pass']) as conn:
            
            # User has submitted a recall during this login session
            if session.get('recall_id') != -1:
                self.update_recall(conn)
            
            # User has not submitted a recall during this login session
            else: 
                self.new_recall(conn)

            # Add submitted food data to database  
            self.add_recall(conn)

    # Called when the user does not have any food recall information from this session
    # conn: DB connection
    def new_recall(self, conn):
            with conn.cursor() as cur:

                # Add recall to user_recall
                cur.execute("""INSERT INTO user_recall(user_id) VALUES (%(id)s);""",{'id': session.get('user_id')})
                conn.commit()

                # Get recall ID
                cur.execute("""SELECT recall_id FROM user_recall WHERE user_id=%(id)s ORDER BY recall_id DESC LIMIT 1;""",{'id': session.get('user_id')})
                data = cur.fetchone()
                session['recall_id'] = data[0]

    
    # Called when user is trying to update the information in this session's recall.
        # Deletes the previous food recall information added during this session so the new information can be added
    # conn: DB connection
    def update_recall(self, conn):
            with conn.cursor() as cur:

                # Delete user's current food recall information
                # NOTE: does NOT delete the entry in user_recall since the information in food recall is just going to be deleted and re-added
                cur.execute("""DELETE FROM food_recalls WHERE recall_id = %(recall_id)s;""",{'recall_id': session.get('recall_id')})
                conn.commit()

    # Adds current food recall information to database
    # conn: DB connection
    def add_recall(self, conn):
            with conn.cursor() as cur:
                # Gets food recall data to be added to food_recall
                food_data = session.get('user_food')
                # Dynamically build query
                base_query = """INSERT INTO food_recalls(recall_id, food_id, meal, quantity, quantity_unit) VALUES"""
                first = True
                for meal in food_data:
                    for food_list in food_data[meal]:
                        if(not first):
                            base_query += ","
                        else:
                            first = False
                        base_query += "({recall_id},{food_lists},'{meal_name}',{quantity},'{unit}')".format(recall_id = session.get('recall_id'), food_lists = food_list['food_id'], meal_name = meal, quantity = food_list['quantity'], unit = food_list['unit'])
                cur.execute(base_query)
                conn.commit()