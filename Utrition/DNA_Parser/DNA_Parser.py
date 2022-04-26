#!/usr/bin/python3

import psycopg2
import configparser
import re
from flask import session 
import os
import logging

#This class parses and uploads various DNA files for given users.
class DNAParser:

	# Change to your path (location where the DNA file is located)
	FILEPATH="/Users/stuti/Desktop/"
	ANCESTRY="AncestryDNA"
	_23ANDME="23andMe"
	
	#Initializes a DNA Parser.
	def __init__(self):
		# DNA connection information
		self.config = configparser.ConfigParser()
		self.config.read('db.ini')

		# Regex for rsid and allele formats
		self.rsid_pattern = re.compile("^rs[0-9]+$")
		self.allele_pattern = re.compile("^(A|G|C|T|-)$")

		# Logging
		self.log = logging.getLogger('UtritionLogger')
		return

	#Uploads the given DNA file to the database using for the the given user.
	#Filename - The filename of the DNA file that was uploaded.
	def upload(self, filename):
		self.log.debug("Establishing DB Connection")
		with psycopg2.connect(host = self.config['utrition_dna']['host'],database=self.config['utrition_dna']['db'], user=self.config['utrition_dna']['user'], password=self.config['utrition_dna']['pass']) as conn:
			self.__parse(DNAParser.FILEPATH + filename)
			self.__dbupload(conn)
			# Deletes the intermediate cleanedDNA file
			self.log.debug("Deleting cleanedDNA.txt")
			os.remove('cleanedDNA.txt')
			self.log.debug("Successfully deleted cleanedDNA.txt")
	
	#Parses the given DNA file.
	#Filename - The filename of the DNA file to parse.
	def __parse(self, filename):
		with open(filename,'r') as file:
			self.log.debug("Detecting file format")
			filetype = self.__detect_format(file)
			self.log.debug("Successfully detected format")
			# Cleaned DNA data that's added to the DB
			with open('cleanedDNA.txt','w') as cleaned:
				
				# File was from Ancestry
				if filetype == 0:
					self.log.debug("Format detected: Ancestry")
					return self.__parse_ancestry(file, cleaned)
				
				# File was from 23andMe
				elif filetype == 1:
					self.log.debug("Format detected: 23andMe")
					return self.__parse_23andme(file, cleaned)
				
				# File was of invalid/unsupported format. Raising error
				else:
					self.log.debug("Format detected: INVALID")
					raise TypeError()

		
	#Determines which format the DNA file is in.
	#File - The open DNA file to be checked.
	#Returns the format type of the DNA file as an integer.
	#	-1 - Type Unknown, 0 - Type Ancestry, 1 - Type 23AndME
	def __detect_format(self, file):
		
		filetype = -1
		
		line = file.readline()
		words = line.strip('#').split()
		
		for word in words:
			if word == DNAParser.ANCESTRY:
				filetype = 0
				break
			elif word == DNAParser._23ANDME:
				filetype = 1
				break

		return filetype
		
	# Parses an Ancestry formatted DNA file.
	# File - The open DNA file to be parsed.
	# Cleaned: Open txt file that cleaned data is written to
	def __parse_ancestry(self, file, cleaned):
		
		#Iterates past all the comments at the start of the DNA file.
		self.log.debug("Iterating past comments")
		line = file.readline()
		while line[0] == '#':
			line = file.readline()
		line = file.readline()	#gets rid of the header

		# DNA array holding one row of cleaned data
		dna = [str(session['user_id']), 'DummyrsID_1', 'DummyAllele1_2', 'DummyAllele2_3']
		self.log.debug("Beginning writing to cleaned DNA file")
		for line in file:
			dna_temp = line.split()
			
			# Checks if rsid and alleles are in the correct format
			if(self.rsid_pattern.match(dna_temp[0]) and self.allele_pattern.match(dna_temp[3]) and self.allele_pattern.match(dna_temp[4])):
				dna[1:4]= dna_temp[0], dna_temp[3], dna_temp[4]

				# writes cleaned data to cleaned DNA file
				cleaned.write('\t'.join(dna) + '\n')
		self.log.debug("Completed writing to cleaned DNA file")
		
	# Parses a 23AndMe formatted DNA file.
	# Andee Assumption - For genes with only one allele [ie mitochondria DNA] it does not matter which position it is stored in.
	# So, allele2 and allele1 will both have the value of the allele so it's compatible with queries
	# File - The open DNA file to be parsed.
	# Cleaned: Open txt file that cleaned data is written to
	def __parse_23andme(self, file, cleaned):
		
		#Iterates past all the comments at the start of the DNA file.
		self.log.debug("Iterating past comments")
		line = file.readline()
		while line[0] == '#':
			line = file.readline()

		# DNA array holding one row of cleaned data
		dna = [str(session['user_id']), 'DummyrsID_1', 'DummyAllele1_2', 'DummyAllele2_3']
		self.log.debug("Beginning writing to cleaned DNA file")
		for line in file:
			validEntry=False
			dna_temp = line.split()

			# Checks if rsid and first allele are in correct format
			if(self.rsid_pattern.match(dna_temp[0]) and self.allele_pattern.match(dna_temp[3][0])):
				# rsID has one allele
				if(len(dna_temp[3]) == 1):
					dna[1:4]= dna_temp[0], dna_temp[3][0], dna_temp[3][0]
					validEntry=True
				# rsID has two alleles; checks if second allele is in correct format
				elif(len(dna_temp[3]) == 2 and self.allele_pattern.match(dna_temp[3][1])):
					dna[1:4]= dna_temp[0], dna_temp[3][0], dna_temp[3][1]
					validEntry=True
				
				# If entry was completely valid, write entry to cleaned DNA file
				if validEntry:
					cleaned.write('\t'.join(dna) + '\n')
		self.log.debug("Completed writing to cleaned DNA file")

	# Adding DNA to database
	# uses a pythonic version of psql's 'COPY' command
	# Lets us insert a large number of records very quickly
	def __dbupload(self, conn):
		self.log.debug("Opening cleaned DNA file for insertion/reading")
		with open('cleanedDNA.txt','r') as cleaned:
			with conn.cursor() as cur:
				self.log.debug("Inserting DNA data")
				cur.copy_from(cleaned, 'dna', columns=('user_id','rsid','allele1','allele2'))
				self.log.debug("Successfully inserted DNA data")