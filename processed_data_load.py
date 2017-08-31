import sys
import math
import xlrd
import json
from lxml import html
import requests
import urllib2
import time
import imaplib
import email
import matplotlib.pyplot as pl
import numpy as np
from scipy.stats import gaussian_kde
import re
import csv

class Meteorite:
	#global variables for all Asteroids:
	met_count = 0
	meteorites = []

	'''
	meteorite object constructor
	PARAMS:
		self : current meteorite object
		meteorite_file : demeo classified spectra result file 
		id_type_map : mapping of unique_id to subtype from relab
		id_type_map_regex : map of regular expression of subtype to actual subtype
		subtype_dic : mapping of sample id to subtype from metbull
		name_dic : mapping of sample id to correct name from relab
		complex_class_dic : mapping of asteroid class to complex classes
		complex_type_dic : mapping of meteorite type to meteorite type 'clan'
		complex_prime_type_dic : mapping of meteorite type to meteorite type 'class'

	This construcor creates a meteorite object with all of the following attrinutes :
		unique_id, sample_ID, name, spec_id, classes, subtype, slope, pca_components, types, complex_classes, complex_type, complex_prime_type

	'''
	#meteorite_text is a list line by line out the spectra_data_processed_new output
	#meteorite_file is the name of the file (to extract spectra ID)
	def __init__(self, meteorite_text, meteorite_file, id_type_map, id_type_map_regex, subtype_dic, name_dic, complex_class_dic, complex_type_dic, complex_prime_type_dic):
		self.unique_id = Meteorite.get_unique_id(self, meteorite_file)
		self.sample_ID = Meteorite.get_sampleID(self)
		self.name = Meteorite.get_elem_from_sample_id(self, name_dic)
		self.spec_id = Meteorite.get_spec_id(self, meteorite_file)
		self.classes = Meteorite.get_classes(self, meteorite_text)
		self.subtype = Meteorite.get_elem_from_sample_id(self, subtype_dic)
		self.slope = Meteorite.get_slope(self, meteorite_text)
		self.pca_components = Meteorite.get_pca(self, meteorite_text)
		self.types = Meteorite.get_types(self, id_type_map, id_type_map_regex)
		self.complex_classes = Meteorite.get_complex_classes(self, complex_class_dic)
		self.complex_type = Meteorite.get_complex_type(self, complex_type_dic)
		self.complex_prime_type = Meteorite.get_complex_prime_type(self, complex_prime_type_dic)

		Meteorite.meteorites.append(self)
		Meteorite.met_count +=1


	'''
	PARAMS:
		self: meteorite object
		complex_prime_type_dic : mapping of meteorite type to its complex prime, or 'class' types
	RETURNS:
		'class' type for this meteorite 
	'''
	def get_complex_prime_type(self, complex_prime_type_dic):
		return complex_prime_type_dic[self.complex_type]


	'''
	PARAMS:
		self: meteorite object
		complex_type_dic : mapping of meteorite type to its complex prime, or 'clan' types
	RETURNS:
		'clan' type for this meteorite 
	'''
	def get_complex_type(self, complex_type_dic):
		if self.subtype == None:
			subtype = self.types[0].split('__')[2]
			return complex_type_dic[subtype]
		else:
			return complex_type_dic[self.subtype]


	'''
	PARAMS:
		self: meteorite object
		complex_class_dic : mapping of asteroid class to its complex type
	RETURNS:
		list of complex asteroid classes for this meteorite
	'''
	def get_complex_classes(self, complex_class_dic):
		complex_classes = []
		for class_ in self.classes:
			class_ = class_.split('-')[0]
			complex_classes.append(complex_class_dic[class_])
		return list(set(complex_classes))

	'''
	PARAMS
		self: current meteorite
		dic : information dictionary in which the keys are sample ids 
	RETURNS:
		element in dictionary associated with this meteorite's sample id. 
	'''
	def get_elem_from_sample_id(self, dic):

		if self.sample_ID not in dic.keys(): #these are in sample id but since their values are "" they dont show up. This means that they were not in metbull
			return None
		else: 
			return dic[self.sample_ID]

	'''
	PARAMS:
		self: current meteorite
		meteorite_file: processesed spectra filename for this meteorite
	RETURNS : unique_id for this meteorite 
	'''
	def get_unique_id(self, meteorite_file):
		unique_id = meteorite_file.split('/')[-1].split('.')[0]
		return unique_id


	'''
	PARAMS: 
		self: current meteorite object
		id_type_map : map of unique id to type1/subtype from relab
		id_type_map_regex : map of regular expression of subtype to actual subtype (to normalize spellings)
	RETURNS:
		relab subtype for this meteorite 
	'''
	def get_types(self, id_type_map, id_type_map_regex):
		unique_id = self.unique_id
		types = id_type_map[unique_id][0]
		regex = re.sub('[^0-9a-zA-Z]+', '*', types)
		type_ = id_type_map_regex[regex]
		return type_


	'''
	PARAMS: 
		self: current meteorite object
		meteorite_text : meteorite processed spectra file text body
	RETURNS:
		demeo classifier output slope for this meteorite 
	'''
	def get_slope(self, meteorite_text):
		summary_line = meteorite_text[1]
		summary_info = summary_line.split(" ")
		summary_info = filter(None, summary_info)
		slope = summary_info[7]
		return slope

	'''
	PARAMS:
		self: current meteorite object
		meteorite_file : filename for the demeo classifier output of this meteorite 
	RETURNS: 
		spectra_id for this meteorite
	'''
	def get_spec_id(self, meteorite_file):
		spectra_id = meteorite_file.split('-')[-1].split('.')[0]
		return spectra_id


	'''
	PARAMS:
		self: current meteorite object
		meteorite_file : filename for the demeo classifier output of this meteorite 
	RETURNS: 
		sample_ID for this meteorite
	'''
	def get_sampleID(self):
		unique_id = self.unique_id.split('-')
		del unique_id[-1]
		return "-".join(unique_id)


	'''
	PARAMS: 
		self: current meteorite object
		meteorite_text : meteorite processed spectra file text body
	RETURNS: 
		list of asteroid classes for this meteorite
	'''
	def get_classes(self, meteorite_text):
		#print "met text " + str(meteorite_text)
		summary_line =  meteorite_text[1]
		types = ""
		if "visual" in summary_line:
			types = summary_line.split(':')[1]
			types_stripped = str(types).replace(",","").rstrip().split(" ")
			types_stripped.remove('either')
			types_stripped.remove('or')
			types_stripped.pop(0)
			return types_stripped
		else:
			type_list = []
			types = summary_line.rstrip().split(' ')[-1]
			type_list.append(types)
			return type_list

	
	'''
	PARAMS: 
		self: current meteorite object
		meteorite_text : meteorite processed spectra file text body
	RETURNS: 
		list of pca components for this meteorite
	'''
	def get_pca(self, meteorite_text):
		summary_line = meteorite_text[1]
		summary_info = summary_line.split(" ")
		summary_info = filter(None, summary_info)
		components = []
		for index in range (8,13):
			components.append(summary_info[index])
		return components

	'''
	PARAMS: 
		current meteorite object
	prints this meteorite to console
	'''
	def print_meteorite(self):
		print "Meteorite " + str(self.spec_id) + " from SAMPLE_ID " + str(self.get_sampleID)
		print "\t" + "Classes = " + str(self.classes)



class Meteorite_Analyze:

	@staticmethod
	def chord_diagram_table(meteorites, classes, types):
		limited_set = set()
		for type_ in types:
			
			if type_ not in limited_set:
				limited_set.add(type_)

		types = list(limited_set)

		print types

		print classes

		table= [ [ 0 for i in range(len(limited_set)) ] for j in range(len(classes)) ] # 24 cols, 33 rows
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0] classes
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]  |
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]  |
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]  V
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
		# types ---->

		classes = list(classes)
		for meteorite in meteorites:
			full_type = meteorite.complex_prime_type
			type_stripped = full_type
			full_clases = meteorite.classes
			for class_ in full_clases:
				col = types.index(type_stripped)
				row = classes.index(class_)
				table[row][col] +=1
		for row in range(len(classes)):
			for col in range(len(types)):
				val = table[row][col]
				table[row][col] = str(val)
		table.insert(0, types)

		for i in range(0, len(classes)):
			curr = table[i+1]
			curr.insert(0, classes[i])
		first = table[0]
		first.insert(0, "data")
		Meteorite_Analyze.export_table_to_text(table, len(classes), len(types))

	

	@staticmethod
	def export_table_to_text(table, rows, cols):
		with open("table_from_code_2.txt", 'w') as f:
			writer = csv.writer(f, delimiter=' ')
			writer.writerows(table)


		# for row in range(rows):
		# 	print table[row]
		# 	for col in range(cols):
				

	@staticmethod
	def class_dic(meteorites, keyword):
		dic = {}
		class_to_regex = {}

		for meteorite in meteorites:
			classes = []
			if keyword == "asteroid_class":
				classes = meteorite.classes
			elif keyword == "meteorite_type":
				classes = meteorite.types

			for elem in classes:
				s = re.sub('[^0-9a-zA-Z]+', '*', elem)
				class_to_regex[elem] = s #class --> regex

			for class_ in classes:
				regex = class_to_regex[class_]
				if regex in dic.keys():
					numcount = dic[regex] + 1
					dic[regex] = numcount
				else:
					numcount = 1
					dic[regex] = numcount

		for class_ in class_to_regex.keys():
			regex = class_to_regex[class_]
			if regex in dic.keys() and regex != "indeterminate":
				val = dic[regex]
				dic[class_] = val
				del dic[regex]

		return dic

	@staticmethod
	def get_subtype_info(meteorites):
		metbull_count_dic = {}
		for meteorite in meteorites:
			types = meteorite.types
			subtype_from_relab = types[0].split('__')[2]
			subtype_from_metbull = meteorite.subtype
			if subtype_from_metbull == None or subtype_from_metbull == "":
				subtype_from_metbull = 'relab__' + subtype_from_relab 

			if subtype_from_metbull not in metbull_count_dic.keys():
				metbull_count_dic[subtype_from_metbull] = 1
			else:
				value = metbull_count_dic[subtype_from_metbull]
				value +=1
				metbull_count_dic[subtype_from_metbull] = value
		return metbull_count_dic





	@staticmethod 
	def sort_by_value(mydict):
		for key, value in sorted(mydict.iteritems(), key=lambda (k,v): (v,k)):
			print "%s: %s" % (key, value)

	@staticmethod
	def plot_scatter(meteorites, class_count_dic, type_count_dic):
		#xtics are going to be classes [x, v, a , b]
		#ytics are going to be types

		all_classes = class_count_dic.keys()
		all_types = type_count_dic.keys()
		data_x = []
		data_y = []

		class_to_num = {}
		count_x = 1
		count_y = 1
		for class_ in all_classes:
			class_to_num[class_] = count_x
			count_x +=1

		type_to_num = {}
		for type_ in all_types:
			type_to_num[type_] = count_y
			count_y+=1

		xticks = class_to_num.keys()

		for meteorite in meteorites:
			classes = meteorite.classes
			types = meteorite.subtype
			print types
			if types == None or types == "":
				types = 'relab__' + meteorite.types[0].split('__')[2]
			for elem in classes:
				x = class_to_num[elem]
				y = type_to_num[types]
				data_x.append(x)
				data_y.append(y)

		print "Type mapping legend ------------------------------------------------------------------------ "
		print type_to_num
		print "Class mapping legend ------------------------------------------------------------------------ "
		print class_to_num

		# xy = np.vstack([data_x,data_y])
		# z = gaussian_kde(xy)(xy)
		# print z

		# #fig, ax = pl.subplots()
		# pl.scatter(data_x, data_y, c=z, s=100, edgecolor='')
		# #pl.xticks(data_x,xticks)
		# pl.colorbar()
		# pl.show()
		print len(data_x)
		print len(data_y)
		pl.hist2d(data_x, data_y, (33, 165), cmap=pl.cm.jet)
		pl.colorbar()
		pl.show()




	@staticmethod
	def plot_density(meteorites, class_count_dic, type_count_dic):
		all_classes = class_count_dic.keys()
		all_types = type_count_dic.keys()

		class_to_num = {}
		count_x = 1
		count_y = 1
		for class_ in all_classes:
			class_to_num[class_] = count_x
			count_x +=1

		type_to_num = {}
		for type_ in all_types:
			type_to_num[type_] = count_y
			count_y+=1
		
		data_x = []
		data_y = []

		print class_to_num

		for meteorite in meteorites:
			classes = meteorite.classes
			types = meteorite.types
			for elem in classes:
				data_x.append(elem)
				data_y.append(types)

		print len(data_x)

		print len(data_y)

		X = []
		Y = []


		uniques_x, X = np.unique(data_x, return_inverse=True)
		uniques_y, Y = np.unique(data_y, return_inverse=True)

		xy = np.vstack([X,Y])
		z = gaussian_kde(xy)(xy)

		fig, ax = pl.subplots()
		ax.scatter(X, Y, c=z, s=100, edgecolor='')
		pl.show()


		#pl.scatter(X, Y)
		#pl.show()


		# x = range(1,len(data_x))
		# y = range(1, len(data_y))

		# xticks=['a','b','c','d']
		# x=[1,2,3,4]
		# y=[1,2,3,4]
		# pl.plot(x,y)
		# pl.xticks(x,xticks)
		# pl.show()



##############################-------------------- ------------------- -------------------- -------------------###################################


#want to make a mapping of each SAMPLE_ID (key) with list of asteroids (each asteroid has a diff spec_id)

#for each sample_ID, look up spectra_id and path of that (from dic previous)
#then for each spec id, create an asteroid_object



#create function that extracts classes
#create function that extracts slope
#create function that extracts pca components





	# def get_subtype(self, subtype_dic):
	# 	if self.sample_ID not in subtype_dic.keys(): #these are in sample id but since their values are "" they dont show up. This means that they were not in metbull
	# 		return None
	# 	else: 
	# 		return subtype_dic[self.sample_ID]

	# def get_name(self, name_dic):
	# 	if self.sample_ID not in name_dic.keys():
	# 		return None
	# 	else:
	# 		return name_dic[self.sample_ID]
