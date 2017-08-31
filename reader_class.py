#
# import sys
# import math
# import xlrd
# import json
#
# class Reader:
#
# 	# gets first excel row out of excel sheet. This row has the table headers. We put it into a list in this method
# 	@staticmethod
# 	def get_labels(filename, sheetname):
# 		workbook = xlrd.open_workbook(filename)
# 		data_set_xl = workbook.sheet_by_name(sheetname)
# 		labels = data_set_xl.row_values(0)
# 		return labels
#
# 	#creates master dictionary mapping each 'SampleID' to a list of all the properties of that meteorite. 
# 	#params: sample_dict is sample_dictionary, spectra_dict is spectrum dictionary
# 	#if spectrum dictionary !contains a meteorite in sample_dictionary, merge_dict value for that key is just  the list from sample_dict
# 	# would spectra_dict contain meteorites not in sample_dict???????? 
# 	@staticmethod
# 	def merge_dicts(sample_dict, spectra_dict):
# 		merge_dict = {}
# 		for key in sample_dict:
# 			sample_list = sample_dict[key]
#
# 			if key in spectra_dict:
# 				spectra_list = spectra_dict[key]
# 				merge_dict[key] = sample_list + spectra_list
#
# 			else:
# 				merge_dict[key] = sample_list
#
# 		return merge_dict
#
#
# 	#THERE ARE DUPLICATE ENTRIES IN THE EXCEL SHEET FOR SAMPLE DATA
# 	@staticmethod
# 	def read_file_to_dict(filename, sheetname):
# 		workbook = xlrd.open_workbook(filename)
# 		data_set_xl = workbook.sheet_by_name(sheetname)
# 		num_rows = data_set_xl.nrows 
# 		num_cols = data_set_xl.ncols
#
# 		#print "num_rows " + str(num_rows)
# 		dic = {}
#
# 		labels = Reader.get_labels(filename,sheetname)
# 		id_index = labels.index('SampleID')
#
# 		for i in range(1, num_rows):
# 			values = []
# 			curr_set = data_set_xl.row_values(i)
# 			key = curr_set[id_index]
#
# 			if key in dic.keys():
# 			#	print "key!! " + key
# 				dic[key].append(curr_set)
# 			else:
# 				values.append(curr_set)
# 				dic[key] = values
#
# 		return dic
#
#
# 	# Returns a dicitonary mapping between each SampleID and its path in the data directory. For each sample ID we store its path
# 	# in a list. The first element is the first directory, the second element is the next directory. We also store the list of spectra
# 	# id associated with each sample ID. 
# 	#The data structure here is : key = SampleID, value = list of [path] and [spectra ID in this path]
# 	@staticmethod
# 	def get_paths(list_of_IDs, spectra_data):
# 		mapping = {} #Sample_ID mapped to list. first entry is first folder, second endtry is second folder, third entry is spectra ID. 
#
# 		print "list of IDS length  " + str(len(list_of_IDs))
#
# 		for key in list_of_IDs:
# 			if key in spectra_data.keys():
# 				path = key.split('-')
# 				path_in_order = [path[1],path[0]]
# 				filenames = Reader.get_spectrum_ids_for_sample_id(key, spectra_data)
# 				value = []
# 				value.append(path_in_order)
# 				value.append(filenames)
# 				mapping[key]=value
# 			else:
# 				print "missing key " + key
# 		return mapping
#
#
# 	@staticmethod
# 	def print_ID_to_path_mapping(ID_path_mapping):
# 		for key in ID_path_mapping:
# 			print "path for " + key
# 			print ID_path_mapping[key[0]]
# 			print "spectra ID in this path: "
# 			print ID_path_mapping[key[1]]	
#
#
# 	@staticmethod
# 	def get_spectrum_ids_for_sample_id(sample_id, spectra_data):
#
# 		spectrum_ids = []
# 		values = spectra_data[sample_id]
# 		for l in values:
# 			spec_id = l[0]
# 			spectrum_ids.append(spec_id)
# 		return spectrum_ids
#
# 	@staticmethod
# 	def export(data_dict, file_to_export):
# 		with open(file_to_export, 'w') as file:
# 			file.write(json.dumps(data_dict))
#
# 	@staticmethod
# 	def tester():
# 		print "heyyyy"
#
# 	@staticmethod
# 	def read_gaf_data(filename, sheetname):
# 		workbook = xlrd.open_workbook(filename)
# 		data_set_xl = workbook.sheet_by_name(sheetname)
# 		num_rows = data_set_xl.nrows 
# 		num_cols = data_set_xl.ncols
#
# 		dic = {}
#
# 		labels = Reader.get_labels(filename,sheetname)
# 		filename_index = labels.index('Wavelength Corrected File')
# 		id_index = labels.index('Sample ID')
#
# 		for i in range(1, num_rows):
# 			values = []
# 			curr_set = data_set_xl.row_values(i)
# 			key = curr_set[id_index]
#
# 			if key in dic.keys():
# 				dic[key].append(curr_set)
# 			else:
# 				values.append(curr_set)
# 				dic[key] = values
#
#
# 		ID_path_mapping = {}
# 		for key in dic.keys():
# 			value = []
# 			path = key.split('-')
# 			path_in_order = [path[1],path[0]]
# 			filenames = Reader.get_gaffey_filenames(key, dic, filename_index)
# 			value.append(path_in_order)
# 			value.append(filenames)
# 			ID_path_mapping[key] = value
# 		return ID_path_mapping
#
# 	@staticmethod
# 	def get_gaffey_filenames(key, dic, filename_index):
# 		values = dic[key]
# 		filenames = []
# 		for l in values:
# 			filename_dat = l[filename_index]
# 			filename = filename_dat.split('.')[0]
# 			filenames.append(filename)
# 		return filenames	
#
#
# 	@staticmethod
# 	def get_IDs_from_source(met_type, all_data):
# 		keys = []
# 		for key in all_data.keys():
# 			values = all_data[key]
# 			sample_cataloguge_data = values[0]
# 			if sample_cataloguge_data[5] == met_type:
# 				keys.append(key)
# 				#print sample_cataloguge_data[5]
# 		return keys
#
#
#
#
#
# 	#run this if you want over all data in catalogues
#
# 	#debugging : sample_data and spectra_data have less than 13713 entries -- sketchy bc sample_data and spectra_data each have exactly 13713 unique 
# 	#entires in thier excel sheets
# 	@staticmethod
# 	def run_all_data(met_type):
# 		sample_data = Reader.read_file_to_dict('Sample_Catalogue.xls','Sample_Catalog2003809')       # sample_data.keys() and spectra_data.keys() are all the sample ID strings. sample_data.values() are the rest of the data in a list
# 		spectra_data = Reader.read_file_to_dict('Spectra_Catalogue.xls', 'Spectra_Catalogue.tab')
#
#
# 		''' all_data : dictionary storing all information in Sample_Catalogue and Spectra_Catalogue
# 			Current structure of dictionary all_data: 
# 				key: SampleID 
# 				value: List of lists. For a given value, each list is a row from either sample catalogue or spectra catalog. sample catalog is first first list. 
# 					   spectra catalog lists are next. Spectra catalog may have multiple rows per SampleID. 
# 		'''
#
# 		print "sample_data " + str(len(sample_data.keys()))
# 		print "spectra_data " + str(len(spectra_data.keys()))
#
# 		all_data = Reader.merge_dicts(sample_data,spectra_data) #dictionary of each sample_id mapped to all properties in both sample and spectra catalogues
#		
# 		print "merged " + str(len(all_data.keys()))
#
#
# 		# workbook = xlrd.open_workbook("Sample_Catalogue.xls")
# 		# sheet = workbook.sheet_by_index(0)
# 		# list_x = sheet.col(0)
#
# 		# __set = {}
# 		# map(__set.__setitem__, list_x, [])
# 		# samp_list_without_dupes = __set.keys()
#
# 		# print len(samp_list_without_dupes)
#
#
# 		# workbook_ = xlrd.open_workbook("Spectra_Catalogue.xls")
# 		# sheet2 = workbook_.sheet_by_index(0)
# 		# list_spec = sheet.col(1)
#
#
# 		# _set = {}
# 		# map(_set.__setitem__, list_spec, [])
# 		# spec_list_without_dupes = _set.keys()
#
#
# 		#all_IDs = all_data.keys()
#
# 		# print len(list_x)
# 		# print len(spec_list_without_dupes)
#		
# 		# print len(all_IDs)
#
# 		met_IDs = Reader.get_IDs_from_source(met_type, all_data) #returns list of IDs that are for given Met type
#	
# 		print "met_IDs " + str(len(met_IDs))
#
#		
#
#
# 		met_ID_path_mapping = Reader.get_paths(met_IDs, spectra_data) #something is going wrong here
#
#		
#
# 		#print "met_IDs mapping dic len " + str(len(met_ID_path_mapping.keys()))
# 		# file_to_export = met_type + '_ID_path_mapping.txt'
# 		# Reader.export(met_ID_path_mapping, file_to_export)
#
# 		# return met_ID_path_mapping
#
#
# 		# #want to proceed in this order : source = other_met, source = mars_met, source = moon_met
#
#
#
# 		#ID_path_mapping = Reader.get_paths(all_IDs, spectra_data)
# 		#print len(ID_path_mapping.keys())
# 		# export(ID_path_mapping, 'ID_path_mapping.txt')
#
# 	#run this if you just want to do gaffey data
# 	@staticmethod
# 	def run_gaffey_data():
# 		gaffey_data = read_gaf_data('Gaffey_Spectra.xls','gafcat.lst')
# 		export(gaffey_data, 'gaffey_ID_path_mapping.txt')
#
#
# Reader.run_all_data("Other-Met")
#
#
#
#
#
