rsID collection works by getting information from NCBI's dbSNP database. This is done through using the Entrez e-utilities found in BioPython. See the Utrition Setup Manual SP'22 for information on how to install BioPython

There are two main functions that are called during the process of actually collecting data:
	- eSearch
		This queries the database based on the input query and returns information such as the web environment, query key, and id list of returned records, and number of records matching the query.
		The web environment and query keys allows the fetching of data from the same web session, thereby avoiding the need to search the database every single time data needs to be fetched.
		eSearch does NOT return specific information about matching records. The id List is simply a list of ids that can be used while actually fetching the data to pinpoint which records to fetch information about.
	- eFetch
		This is what actually fetches records from the database.
		By providing the web environment, query key, and range of values to fetch, control can be maintained over which entries are being fetched.
			This is particularly useful when you want to gather data on multiple different locations or across different machines.
		Completing this step is arguably the slowest part of the process. On average throughout the whole process, 1 record/s is being processed/fetched.
		This step is also the bottleneck for the data collecting operation. The number of queries fetched before a HTTP 500 error is thrown can be very small relative to the number of records that need to be fetched.
		A HTTP 500: Internal Server Error is an error occurring on NCBI's side. 
		This is likely due to NCBI being unable to handle the potential large number of requests it's receiving. 
		Fetching pretty small numbers of records at a time proves to be consistent, but fetching larger numbers of records is rather inconsistent. 
		This is the main reason for 'double batching'.

Data collection uses 4 scripts:
1) ncbi_webscraping.sh - controls the general flow of web scraping, uses psql to parse, clean, and add entries from rsid_searchBatch.json into the database
2) queryCount.py - returns the number of records returned from NCBI that matches the query [uses eSearch]
3) eSearch_webscraping.py - returns information about the web session to be used while fetching (web environment and query key) [uses eSearch]
4) eFetch_webscraping.py - fetches records from dbSNP and writes them to a JSON file called rsid_searchBatch.json [uses eFetch]


In very general terms, the general flow of data collection is the following:

0.5) Setup
1) Get data in batches.
2) After each batch, insert the data into a JSON table (created prior to getting data)
3) After ALL data from ALL batches have been collected and entered into the JSON table, parse and clean the JSON data to retrieve useful information (rsID, reference allele, mutated allele(s), corresponding disease(s))
4) Insert the parsed and cleaned data into the database
4.5) Teardown

Data collection (Step 1 in the general flow) uses 'double batching'. 
This strategy was used in response to the large number of records that need to be fetched, the HTTP 500 Internal Server Error issue, and to avoid writing to the database an unnecessarily large number of times (to lower execution time).

Batching occurs on two levels: The file level and the command level.
'File level' refers to records that one run of the eFetch FILE (script #4) returns.
'Command level' refers to commands that one run of the eFetch COMMAND (run within the eFetch FILE) returns.

Example: [All numbers used are simply for example purposes]
Let's say that the query being searched returns 1000 queries.
If you'd like to have 250 entries entered into the database each time the database is accessed, then each run of the eFetch FILE returns 250 queries, resulting in the eFetch FILE being run a total of 4 times.
If you know that the eFetch COMMAND, run WITHIN the eFetch FILE, can only handle 50 entries before throwing errors, then you want the eFetch COMMAND to return 50 records each time it runs.
So, the eFetch COMMAND is run 5 times each time the eFetch FILE is called once.

In total, to insert 1000 commands:
The eFetch COMMAND is run 20 times. 5 times per run of the eFetch FILE.
The eFetch FILE is run 4 times.

