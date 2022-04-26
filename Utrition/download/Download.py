#!/usr/bin/python3

import psycopg2
import configparser
from flask import session
import logging
class Download:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('db.ini')
        self.log = logging.getLogger('UtritionLogger')
        return 


    '''
    Query explanations:

    In order to generate the "Eat This, Not That" report, queries are run to do the following:
    1) Generate a list of diseases that the user is susceptible to based on their DNA information
    2) Generate a list of foods that downregulate those diseases ["Eat This"]
    3) Generate a list of foods that upregulate those diseases ["Don't Eat This"]


    Query 1: Creating a view consisting of the diseases that the user is pre-disposed to. This view is dropped after the downloading process is complete
    The original version of this query included joining on the rsID table and had an extra WHERE clause condition isolating rsID where at least one of the DNA alleles wasn't the reference allele.
    Considering that the goal of this query is just to find the diseases that a user is susceptible to based on the information in the database alone, there wasn't much of a need to join with the rsID table.
    That being said, this method excludes DNA where the mutation isn't in the mutation table (because it wasn't reported on clinVar) and info for rsIDs not in the database.
    The main way the second problem can be mitigated is by collecting more data and expanding the types of supported mutations.
        
        CREATE VIEW userDisease AS  -- Creates the view
            SELECT 
                dis.name AS name  -- View consists of a list of diseases
            FROM 
                dna as d
                    INNER JOIN mutated_rsid as mr ON mr.rsid = d.rsid 
                    INNER JOIN disease AS dis ON dis.id = mr.disease_id 
            WHERE 
                d.user_id=[USER_ID]               -- Isolates results so they only apply to the current user
                AND (d.allele1 LIKE mr.allele     -- Isolates DNA information where the mutation is in the mutation table
                    OR d.allele2 LIKE mr.allele)


    Query 2: Provides information on flavonoids that regulate the diseases found from Query 1, along with whether those flavonoids up or downregulate a disease from Query 1
        Direction 1: Downregulates
        Direction 2: Upregulates

        SELECT 
            DISTINCT LOWER(compound_tag), direction -- Returns flavonoids and their direction
        FROM compound 
        WHERE 
            disease_tag IN                      -- Isolating diseases that the user is susceptible to
                (SELECT name 
                FROM userDisease) 
            AND UPPER(compound_tag) IN          -- Isolates only flavonoids that are in the flavonoid table
                (SELECT UPPER(COLUMN_NAME) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'flavonoid');


    Query 3: Provides a list of foods that up/down regulate the diseases
        This provides a list of foods whose flavonoid values for the flavonoids that up/down regulate diseases are not 0/null for at least one of the flavonoids from Query 2
        Note: While only one query is down here, there are two versions of this query that look the same but check for different things. 
        One checks for foods that upregulate diseases, and the other checks for foods that downregulate diseases.

        This query is being built dynamically - both in the number of flavonoids as well as which flavonoids. As a result, this query is unfortunately vulnerable to SQL injection.
        All of the information used in this query came from data from external, reputable databases. 
        The only information from the user (DNA info) used anywhere in the process of building the report (Only used in Query 1) was cleaned properly prior to entering into the database.
        As a result, the chance of SQL injection is very low.

        SELECT food_info.short_food_description 
        FROM flavonoid JOIN food_info ON food_info.food_id = flavonoid.food_id 
        WHERE (flavonoid.[flavonoidName] IS NOT null AND flavonoid.[flavonoidName] > 0) OR (flavonoid.[flavonoid2Name] IS NOT null AND flavonoid.[flavonoid2Name] > 0) OR ...
        
    '''

    # outputFile: The report to be downloaded
    def download(self, outputFile):

        self.log.debug("Connecting to Database")
        with psycopg2.connect(host = self.config['utrition_dna']['host'],database=self.config['utrition_dna']['db'], user=self.config['utrition_dna']['user'], password=self.config['utrition_dna']['pass']) as conn:
            with conn.cursor() as cur:

                # QUERY 1

                # Create view of diseases
                self.log.debug("Executing Query 1")
                cur.execute("""CREATE VIEW userDisease AS SELECT dis.name AS name FROM dna as d INNER JOIN mutated_rsid as mr ON mr.rsid = d.rsid INNER JOIN disease AS dis ON dis.id = mr.disease_id WHERE d.user_id=%(id)s AND (d.allele1 LIKE mr.allele OR d.allele2 LIKE mr.allele)""",{'id': session['user_id']})
                conn.commit()
                
                # QUERY 2
                
                # Find all flavonoids regulating relevant diseases and info on whether they up or down regulate a disease
                self.log.debug("Executing Query 2")
                cur.execute("""SELECT DISTINCT LOWER(compound_tag), direction FROM compound WHERE disease_tag IN (SELECT name FROM userDisease) AND UPPER(compound_tag) IN (SELECT UPPER(COLUMN_NAME) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'flavonoid');""")
                
                # List of flavonoids that downregulate user diseases
                dir_1 = []

                # List of flavonoids that upregulate user diseases
                dir_2 = []
                
                data = cur.fetchone()
                
                # Depending on the direction listed for the flavonoid, the flavonoid is either added to the upregulating or downregulating lists
                while data is not None:
                    if data[1] == 1:
                        dir_1.append(data[0])
                    elif data[1] == 2:
                        dir_2.append(data[0])
                    data = cur.fetchone()
                
                len1 = len(dir_1)
                len2 = len(dir_2)

                # QUERY 3

                s_dir1 = """SELECT food_info.short_food_description FROM flavonoid JOIN food_info ON food_info.food_id = flavonoid.food_id WHERE"""  
                s_dir2 = """SELECT food_info.short_food_description FROM flavonoid JOIN food_info ON food_info.food_id = flavonoid.food_id WHERE"""
                s_disease = """SELECT name FROM userDisease"""

                # dynamically build sql query for direction 1
                for id in dir_1:
                    len1 = len1 - 1
                    if len1 == 0:
                        s_dir1 += " (flavonoid."+id+" IS NOT null AND flavonoid."+id+" > 0)"
                    elif len1 > 0: s_dir1 += " (flavonoid."+id+" IS NOT null AND flavonoid."+id+" > 0) OR"

                # dynamically build sql query for direction 2
                for id in dir_2:
                    len2 = len2 - 1
                    if len1 == 0:
                        s_dir2 += " (flavonoid."+id+" IS NOT null AND flavonoid."+id+" > 0)"
                    elif len2 > 0: s_dir2 += " (flavonoid."+id+" IS NOT null AND flavonoid."+id+" > 0) OR"

                self.log.debug("Direction 1 Query: %s", s_dir1)
                self.log.debug("Direction 1 Query: %s", s_dir2)

                # 1: DISEASE
                
                self.log.debug("[Initial] Writing Disease into to file")

                # Write output of sql query to outputFile
                SQL_for_file_output = "COPY ({0}) TO STDOUT".format(s_disease)
                cur.copy_expert(SQL_for_file_output, outputFile)
                
                # Reset pointer to beginning of file
                outputFile.seek(0)

                # String containing everything in the file
                disease = outputFile.read()
                count = disease.count('\n') - 1

                # Replacing new lines with line breaks [HTML formatting]
                disease = disease.replace('\n','<br><li>',count)
                
                # Clear file contents
                outputFile.seek(0)
                outputFile.truncate(0)


                # 2: DOWNREGULATION/DIRECTION 1 [Same steps as for # 1: DISEASE]
                self.log.debug("[Initial] Writing Direction 1 foods into file")
                SQL_for_file_output = "COPY ({0}) TO STDOUT".format(s_dir1)
                cur.copy_expert(SQL_for_file_output, outputFile)
                outputFile.seek(0)
                dir_1 = outputFile.read()
                count = dir_1.count('\n') - 1
                dir_1 = dir_1.replace('\n','<br><li>',count)
                outputFile.seek(0)
                outputFile.truncate(0)
                
                
                # 3: UPREGULATION/DIRECTION 2 [Same steps as for # 1: DISEASE]
                self.log.debug("[Initial] Writing Direction 2 foods into file")
                SQL_for_file_output = "COPY ({0}) TO STDOUT".format(s_dir2)
                cur.copy_expert(SQL_for_file_output, outputFile)
                outputFile.seek(0)
                dir_2 = outputFile.read()
                count = dir_2.count('\n') - 1
                dir_2 = dir_2.replace('\n','<br><li>',count)
                outputFile.seek(0)
                outputFile.truncate(0)
                
                # Report construction
                # HTML headers
                outputFile.write('<!doctype html><html lang="en" ng-app="nutritionApp"><head><meta charset="utf-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=0.5"><title>Utrition Analysis</title><link rel="stylesheet" href="/Users/stuti/Desktop/Utrition/static/lib/bootstrap/css/bootstrap.css"/><link rel="stylesheet" href="/Users/stuti/Desktop/Utrition/static/lib/bootstrap/css/bootstrap-theme.css"/><link rel="stylesheet" href="/Users/stuti/Desktop/Utrition/static/css/app.css"/><style>ul {list-style: none} h1 {text-align: center;} li { background: white; }li:nth-child(odd) { background: #D3D3D3; }h2 {text-align: center;} div.report {font-size: 25px} p {text-align: center; font-size: 25px}</style></head><body><div class="header"><img class="logo" src="/Users/stuti/Desktop/Utrition/static/images/EngageHealth-Color-P.png" alt="Engage Health"/></div><h1>Utrition Analysis Report</h1>')
                outputFile.write('<p>Note: There may be overlap between the "Eat This" and "Do Not Eat This" lists.</p><p> Out of the diseases you may be genetically predisposed to, certain foods may help regulate one disease while simultaneously promoting another disease.</p>')

                # Write disease information
                self.log.debug("[Final] Writing Disease into file")
                outputFile.write('<h2>Diseases you may be genetically pre-disposed to:</h2><div class="report"><ul><li>')
                outputFile.write(disease)

                # Write foods that downregulate diseases
                self.log.debug("[Final] Writing Direction 1 Foods into file")
                outputFile.write('</ul></div><br><h2>"Eat This" Recommendations based on diseases you may be genetically pre-disposed to</h2><div class="report"><ul><li>')
                outputFile.write(dir_1)
                
                # Write foods that upregulate diseases
                self.log.debug("[Final] Writing Direction 2 Foods into file")
                outputFile.write('</ul></div><br><h2>"Do Not Eat This" Recommendations based on diseases you may be genetically pre-disposed to</h2><div class="report"><ul><li>')
                outputFile.write(dir_2)
                outputFile.write("</ul></table></div></body></html>")

                # Drop view
                self.log.debug("Dropping view from Query 1")
                cur.execute("""DROP VIEW userDisease""")
                conn.commit()