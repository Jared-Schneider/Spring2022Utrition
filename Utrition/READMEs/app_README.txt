
DISCLAIMER: 
	- General app structure was implemented by previous teams
	- ElasticSearch usage/food lookup was also completed by previous teams
	- Structure for the start page, DNA upload page, food-recall page, and download pages were completed by previous groups

Utrition4 added/added to the following aspects of the web application:

1) Front-end/back-end connection
	- Previously, the web app was not connected to the database what-so-ever
	- This means functionality like DNA upload and report download would crash the app
	- User information didn't persist

2) Login functionality
	- This page existed before Utrition4
	- However, the user could proceed to food-recall even if: no email was entered or the "email" entered wasn't actually an email (eg. 'bucks')
	
	Changes added by Utrition4:
		- emails must be in email format
		- email value cannot be empty
		- Depending on if the user's email is already in the database, the user is taken to one of three different pages.
		- Error handling

3) Registration functionality
	- This functionality did not exist before Utrition4

	- This page is accessed if the email entered in the start/login page didn't exist in the database (i.e new user)
	Changes added by Utrition4:
		- Users enter their first and last name corresponding to the email entered in the start/login page
		- first and last name cannot be empty
		- On submission, user information is added to the database.
		- Added data persists, meaning the next time the user accesses the web app and enters their email, this page will be skipped and not shown to the user.
		- On submission, user is redirected to DNA upload page
		- Error handling

4) DNA Upload
	- Previously, this page existed, but was inaccessible from the UI
	- Users needed to enter their email (again)
	- Filename was incorrectly retrieved [caused the app to crash. Once this was fixed, DNA upload worked fine] 
		- The 'filename' was just the part of the email before the @ sign. 
		- Eg. if the entered email was a@osu.edu, DNA upload would think that the name of the uploaded file was 'a', and not the actual uploaded filename
	
	- This page is accessed in two ways: 1) User in the DB who doesn't have DNA info in the DB [from Login page], or 2) New User [from Register page]
	Changes added by Utrition4:
		- Filename is retrieved correctly
		- Users no longer needed to re-type email
		- Page is accessible from the UI
		- Uploaded file is not saved to the Desktop
	- See parser_README.txt for information on how DNA parsing was changed

5) Food Recall
	- Previously, this page existed, and was 'functional'
	- Food recall information was not accessible after submission since the way it was delivered to app.py from the food controller was incorrect

	Changes added by Utrition4:
		- Food cannot be added if the 'food' and 'quantity' fields are empty, if 'quantity' is not a number, or if 'quantity' is less than 1
		- Food recall cannot be submitted if no foods have been added
		- Submitted food recall information is accessible to be added to the database
		- Food and user recall information added to the database upon submission
		- Food recall information in the database is updated if the user returns to the food recall page after form submission
		- Food id was also added as a piece of information hidden from the user but accessible for easy database insertion
		

6) Download Report
	- Previously this page existed, but attempting to download would crash the web app.
	- Framework to download report did not work

	Changes added by Utrition4:
		- Framework to download works
	- See the comments in download/Download.py for information on how downloading was implemented

7) Updates to styling
	- Engage Health banner size reduced
	- 'Pink' color scheme updated to a gray color to provide contrast between the colors of the logo and the background color
		
		