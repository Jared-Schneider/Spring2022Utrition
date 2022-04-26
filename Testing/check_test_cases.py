import psycopg2
import sys

			
def main():
	
	filename = sys.argv[1]			# name of the file to read test cases from
	cases_should_pass = int(sys.argv[2])	# how many test cases should pass
	cases_should_fail = int(sys.argv[3])	# how many test cases should fail
	num_prereqs = int(sys.argv[4])	# how many of the test cases at the beginning of the file are needed to stop 
						# foreign key constraint errors on test cases for this table
	number_passed = 0 			# how many test cases have passed
	number_failed = 0 			# how many test cases have failed
	i = 1					# user for keeping track of when we have transitioned from
						# the pass section of file to fail section of file
	j = 1					# used to keep track of how many prereq insert statements we have executed
	read_EOF = False			# bolean to check for EOF
	test_case = ""				# string used to parse input file
	
	# try to open the file containing test cases
	try:
		test_file = open(filename)
		print("File was successfully opened\n")
	except ValueError:
		print("Error: file could not be opened. Qutiing now. \n")
		return
	
	# try to connect to the database
	try:
		connection = psycopg2.connect(database="utrition_final", user = "jared", password = "Deraj1999", host = "127.0.0.1", port = "5432")
		print("Opened database successfully\n")
	except:
		print("Error: could not connect to database. Quitting now. \n")
		return

	# this allows us to execute commands
	cursor = connection.cursor()
	
	# execute the prereq insert commands
	if num_prereqs > 0:
		# execute line by line
		while j <= num_prereqs:
			test_case = test_file.readline()
			# make sure we dont try to execute a blank line, comment or beginning "\connect" line
			if (test_case[:2] != "--") and (test_case[:1] != "\\") and (test_case[:1] != "\n"):
				try:
					cursor.execute(test_case)
					j += 1
				except:
					print("Prerequisite INSERT statement failed.")
					print(test_case)
					print("Ending execution now. The prerequisite insert statements must pass in order to run test cases.")
					return 
	
	
	
	
	for test_case in test_file:
		# make sure we dont try to execute a blank line, comment or beginning "\connect" line
		if (test_case[:2] != "--") and (test_case[:1] != "\\") and (test_case[:1] != "\n"):
			try:
				cursor.execute(test_case)
				# we will only get to this point in the logic if the case passes.
				# if this case should have passed, increment the number of cases passed. Otherwise, print an error message
				if i <= cases_should_pass:
					number_passed += 1
				else:
					print("Error: The following test case should have failed, but instead passed: ")
					print(test_case)
			except:
				# we will only get to this point in the logic if the case fails.
				# if this case should have failed, increament the number of cases failed. Otherwise, print an error message
				if i > cases_should_pass:
					number_failed += 1
				else:
					print("Error: The following test case should have passed, but instead failed instead: ")
					print(test_case)	
			
			i += 1

	# close the file of test cases
	test_file.close()
	
	# commit changes to db, needed for testing tables with foreign keys who need to refernce data in another table
	# (whose tests you should run first)
	connection.commit()
	connection.close()
	
	print("Results of running the tests: ")
	print("Out of the first", cases_should_pass, "cases that should have passed,", number_passed, "cases did pass and", cases_should_pass - number_passed, "failed.")
	print("Out of the last", cases_should_fail, "cases that should have failed,", number_failed, "cases did fail and", cases_should_fail - number_failed, "passed.")


if __name__ == "__main__":
	main()
	
	
