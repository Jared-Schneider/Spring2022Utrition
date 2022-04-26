#!/usr/bin/python3

import psycopg2
import configparser
from flask import session
import logging

# Class for Logging in
class Login:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('db.ini')
        self.log = logging.getLogger('UtritionLogger')
        return 

    """
    The login method attempts to log the user into the Utrition WebApp and outlines the three different routes a user can take after logging in.
    Route 1: The user isn't in the database (i.e a new user) and thus they don't have any DNA information in the database either.
        In app.py, this result will cause the user to be redirected to the registration page
    Route 2: The user is in the database (i.e a returning user) but doesn't have any DNA information in the database
        NOTE: In production, this route really won't be taken since users are required to upload their DNA information prior to continuing to the food-recall page.
              This route will most commonly be used in testing, or if something goes wrong, or a user closes out of the web app after registering but before uploading DNA info
       In app.py, this result will cause the user to be redirected to the DNA upload page
    Route 3: The user is in the database and has DNA information in the database
        In app.py, this result will cause the user to be redirected to the food recall page.
    """ 
    # Email: The email the user used to log in
    def login(self, email):
        # Establish DB Connection
        self.log.debug("Establishing DB Connection")
        with psycopg2.connect(host = self.config['utrition_dna']['host'],database=self.config['utrition_dna']['db'], user=self.config['utrition_dna']['user'], password=self.config['utrition_dna']['pass']) as conn:
            with conn.cursor() as cur:
                self.log.debug("LOGIN")
                # Try to get the user_id corresponding to the entered email
                self.log.debug("Entered email: %s", email)
                cur.execute("""SELECT id, first_name, last_name FROM users WHERE email = %(email)s;""", {'email': email})
                data = cur.fetchone()

                # Route 1
                if data is None:
                    return {'id':0, 'dna':-1}
                else: 
                    self.log.debug("User not in database")
                    cur.execute("""SELECT user_id FROM dna WHERE user_id = %(data)s;""", {'data': data[0]})
                    dna_id = cur.fetchone()
                    
                    # Route 2
                    if dna_id is None:
                        self.log.debug("User in database but no DNA information in database")
                        return {'id':data[0], 'dna':-1}
                    
                    # Route 3
                    else: 
                        self.log.debug("User in database and has DNA information in database")
                        return {'id':data[0], 'dna':dna_id[0]}



# Class for Registering new users
class Register:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('db.ini')
        self.log = logging.getLogger('UtritionLogger')
        return 


    """
    The register method registers new users.
    Upon successful registration, the user is redirected to the DNA upload page in app.py.
    Note that if an invalid email that violates email constraints is added (if the constraint misses a type of valid email), the invalidness will only appear after the user tries to register.
    An error during registration redirects the user back to the registration page.
    """ 
    # f_name: first name entered during registration
    # l_name: last name entered during registration
    def register(self, f_name, l_name):
        # Establish DB Connection
        self.log.debug("Establishing DB Connection")
        with psycopg2.connect(host = self.config['utrition_dna']['host'],database=self.config['utrition_dna']['db'], user=self.config['utrition_dna']['user'], password=self.config['utrition_dna']['pass']) as conn:
            with conn.cursor() as cur:
                self.log.debug("REGISTRATION")
                # Insert user into users table in DB
                self.log.debug('Entered first name: %s, Entered last name: %s, Entered email: %s', f_name, l_name, session.get('email'))
                cur.execute("""INSERT INTO users (first_name, last_name, email) VALUES (%(f_name)s, %(l_name)s, %(email)s);""", {'email': session.get('email'), 'f_name': f_name, 'l_name': l_name})
                conn.commit()

                # Get user_id
                self.log.debug("Successful insertion. Getting user id")
                cur.execute("""SELECT id FROM users WHERE email = %(email)s;""", {'email': session.get('email')})
                row = cur.fetchone()
                user_id = row[0]
        return user_id