import sys
import math
import xlrd
import json
from lxml import html
import requests
import urllib2
import time

class ScraperMetbull:


	#This function takes a file and boolean parameter. The file is always 'meteorite_names.txt' which is a file of format:
	# 'sampleID_1' : name
	# 'sampleID_2' : name
 	# etc ....
 	# This file was created manually by extracting data from the sample catalogue and manually editing the names for whitespace, mispellings 
 	# and other errors so that the names could be searched by this program in the metbull database. 
 	# If a name does not exist in the metbull database, the entry is marked in the file with '!!!!!!!!!!!'

 	# This function takes the manually created meteorite_names.txt file and strips whitespace, converting it into a dictionary mapping 
 	# sample ID to name. If is_name_dic == true, then we keep the non-existant entries (with '!!!!!!!') in. If it is false, we mark the 
 	# non existant entries as "" 
	@staticmethod
	def read_names_into_dic(file_, is_name_dic):
		name_dic = {}
		with open(file_, 'r') as f:
			lines = f.readlines()
			for line in lines:
				curr = line.rstrip('\n').split(":")
				key = curr[0]
				val = curr[1]
				if "!" in val:
					if is_name_dic:
						name_dic[key.lstrip().rstrip()] = val.split('!')[0].lstrip().rstrip()
					else:
						name_dic[key] = ""	

				elif "!" not in val:
					val = val.rstrip().lstrip()
					key = key.rstrip().lstrip()
					name_dic[key] = val
		return name_dic

	#sends a request to metbull.php for a search of a meteorite name and returns the subclass of this meteorite. 
	@staticmethod
	def search_name(name):
		url = 'https://www.lpi.usra.edu/meteor/metbull.php'
		sfor = "names"
		stype = "contains"
		ants = "no"
		falls = "yes"
		page = "0"
		rect = "no"
		phot = "no"
		submit = "Search!"
		sea = name
		form_params = {
			"sfor" : sfor,
			"stype" : stype,
			#"ants" : ants,
			#"falls" : falls,
			"page" : page,
			"rect" : rect,
			#"phot" : phot,
			"sea" : sea,
			"submit" : submit
		}
		s = requests.Session()
		response = s.post(url, data=form_params)
		subclass = ScraperMetbull.extract(response.text)
		return subclass

	#extracts the subclass from the response text from metbull
	@staticmethod
	def extract(text):
		subclass = ""
		for line in text.split('\n'):
			if "metbullclass" in line:
				subclass = line.split(">")[2].split("<")[0]
		return subclass

	#exports a dictionary to string so that it can be read in 
	@staticmethod
	def export(file_to_export, dic):
		with open(file_to_export, "w") as output:
			output.write(str(dic))

	#this function takes the an id-name dictionary and returns an id-subclass dictionary. It then exports the id-subclass dictionary to file_to_export 
	@staticmethod
	def search_all(dic, file_to_export):
		for elem in dic.keys():
			name = dic[elem]
			if name != " ":
				subclass = ScraperMetbull.search_name(name)
				print elem + " ------------> " + subclass
				time.sleep(.5)
				dic[elem] = subclass

		ScraperMetbull.export(file_to_export, dic)

		# with open(file_to_export, "w") as output:
		# 	output.write(str(new_dic))

	'''
	MAIN METHOD -- creates name dictionary and exports it to folder. Then use ID-subclass map to gather name 
	data from metbull in function search_all()
	Returns a sample id to subclass map that is exported to id_subclass_map.txt
	'''
	@staticmethod
	def main():
		name_dic_to_export = ScraperMetbull.read_names_into_dic('meteorite_names_updated.txt', True) #invalid entry names remain
		ScraperMetbull.export('name_dic_updated.txt', name_dic_to_export)
		name_dic_to_search = ScraperMetbull.read_names_into_dic('meteorite_names_updated.txt', False) #invalid entry names set to ""
		ScraperMetbull.search_all(name_dic_to_search, "id_subclass_map_updated_v2.txt")



