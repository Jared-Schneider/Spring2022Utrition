NOTE: In order to successfully upload DNA, please make sure to change the file path in parser.py to the directory that you will be uploading the DNA information from

DISCLAIMER: 
	- Utrition4 redid the parsing and insertion portions of DNA upload. 
	- File format detection was completed by a previous team.
	- Utrition 4 also accessed user ID and email using a session variable rather than running a query multiple times across the web app to retrieve the user ID.
	- Previously, information like email was passed in using function parameters
	- Utrition4 also implemented using a database.ini file (called db.ini) to access database configurations like the database name and password, rather than directly typing that information in.
	- Utrition4 took out two functionalities: Deleting the uploaded file from the user's computer, and deleting the user's DNA information from the database


The way that DNA upload is handled is the following:

1) The format of the file is detected [i.e is the DNA information from Ancestry.com, 23andMe. If neither format is detected, the file is categorized to be an invalid format]
2) If the file is in a valid format, the file is parsed based on its format. 
	- If the file is in an invalid format, a TypeError exception is thrown, and the user is redirected to the error page

	The specifics of parsing work a bit differently between DNA from Ancestry and 23andMe.
	Specifically:
		- Ancestry header is not commented out; 23andMe header is. 
		- Ancestry parsing thus needs an extra 'readLine()'

		- Ancestry alleles are not separated by tabs. i.e, the allele looks like (eg.) 'AA', so the 'AA' needs to be split into 'A' and 'A' during parsing
		- 23andMe alleles ARE tab delineated. So they don't need to be split into two alleles.

		- Only 23andMe (as far as we know) includes mitochondrial DNA (the chromosome is listed as 'MT'). 
		- This DNA only has one allele. 
		- To keep the mitochondrial DNA data compatible with the DNA table constraints and other queries, allele1 and allele2 are both the value of the single allele. 
		- In other words, if the sole allele of one rsID from the mitochondrial DNA was 'C', then allele1 and allele2 are both 'C'.

Otherwise, the logic for parsing is the same:
3) Read through each line of the DNA file
4) If the line contains valid data, the data from the line is written to a file called 'cleanedDNA.txt'.
5) After parsing and writing to 'cleanedDNA.txt' is completed, 'copy_from' is used to add all of the entries to the database in bulk.


Notes:

- copy_from fails if even a single piece of data has even one invalid value. This is why the formatting of DNA entries is carefully checked prior to entering.
	- copy_from was used because it allows us to very quickly insert a large number of rows (eg. inserting 17,000 rows using the corresponding psql command took at most a couple of seconds)
- This method allows us to enter around 600,000 rows of valid DNA information in about 20 seconds.

This was not the method of parsing/upload implemented by previous groups.
Previous groups read through the file once (did not check for as many conditions as the current implementation) and added each row of DNA (a list) to another list called data.
So if the DNA file had 600,000 rows of valid DNA information, after parsing the DNA file, the data list contained 600,000 lists within it, with each list containing multiple values.
Then the data list was read through and each row of data was inserted into the database one row at a time.

This method made uploading DNA information containing rows of valid DNA information difficult for a couple of reasons:
1) It took a long time to upload the DNA file (on the order of minutes)
2) This method required a lot of computing power and often caused computers to heat up quite a bit

Due to these considerations and the desire not to have users wait for minutes to upload a single file and to optimize the process, the methodology described prior to the Notes section was developed and implemented.


