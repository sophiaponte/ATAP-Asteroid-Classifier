import sys
import math
import xlrd
import json
import re


class Names:
#----------------------------------------------------------------------------------------------------------------------------------------------------
	#reads sample data dictionary and extracts name info. creates a new dictionary mapping from sample_id to name only
	@staticmethod
	def get_names(dic):
		counter = 0
		name_dic = {}
		name_list = []
		for key in dic.keys():
			values = dic[key]
			name_vals = []
			for value in values:
				
				name = value[1]
				name_vals.append(name)
				name_list.append(name)
			name_dic[key] = name_vals

		print_visual(name_dic, 'meteorite_names.txt')
		return name_dic

	#dictionary names had to be manually edited in a txt file, so this function prints the dic to a file in a way that is easy to edit
	@staticmethod
	def print_visual(dic, filename):
		with open(filename, 'w') as f:
			for k,v in dic.items():
				str_ = str(k) + " : " + str(v[0]) + '\n'
	 			f.write(str_);

	#after the names have been manually edited, this file reads the new name dictionary in and cuts out whitespace and stuff. 
	@staticmethod
	def read_names(file_):
		name_dic = {}
		with open(file_, 'r') as f:
			lines = f.readlines()
			for line in lines:
				curr = line.rstrip('\n').split(":")
				key = curr[0]
				val = curr[1]
				if "!" in val:
					name_dic[key] = ""
				elif "!" not in val:
					val = val.rstrip().lstrip()
					key = key.rstrip().lstrip()
					name_dic[key] = val
		print name_dic
		return name_dic

	@staticmethod
	def export(dic, filename):
		with open(filename, "w") as output:
			output.write(str(dic))

	'''
	Main method
	'''
	@staticmethod
	def run():
		#Names.get_names(filtered_sample_data_dic) #-- uses filtered dictionary from analyze-data.py
		name_dic = Names.read_names("meteorite_names.txt") #name dictionary
		#Names.export(name_dic, "names_to_classify.txt")

run()
#-----------------------------------------------------------------------------------------------------------------------------------------------