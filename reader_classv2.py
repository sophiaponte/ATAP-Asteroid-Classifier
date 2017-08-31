import sys
import math
import xlrd
import json
import re


#notes : some sampleIDs associated with spectrum IDs dont even exist in the sample catalogue. (find a list of these)
#there are some duplicate unique ids-- see note


#want this to get data from spectra and source catalogs for ALL data. then can use this to parse out stuff from source
class Reader:
	

	''' MAIN METHOD
		creates sample_data dictionary
		gets list of unique_ids for each sample_id/spectra_id pair
		creates unique_id --> url dictionary for met types needed and exports them so they can be loaded easily
	'''
	@staticmethod
	def run_reader():
		dic = Reader.get_sample_data_info("Sample_Catalogue.xls", 'Sample_Catalog2003809')
		unique_ids = Reader.get_unique_ids("Spectra_Catalogue.xls", 'Spectra_Catalogue.tab')
		
		other_met_urls = Reader.get_urls_to_load("Other-Met", unique_ids, dic)
		moon_met_urls = Reader.get_urls_to_load("Moon-Met", unique_ids, dic)
		mars_met_urls = Reader.get_urls_to_load("Mars-Met", unique_ids, dic)

		Reader.export(dic, "url_dics_to_load/sample_data_dictionary.txt")
		Reader.export(mars_met_urls, "url_dics_to_load/mars_met_urls.txt")
		Reader.export(other_met_urls, "url_dics_to_load/other_met_urls.txt")
		Reader.export(moon_met_urls, "url_dics_to_load/moon_met_urls.txt")

		# Reader.export(mars_met_urls, "url_lists_to_load/mars_met_urls.txt")
		# Reader.export(other_met_urls, "url_lists_to_load/other_met_urls.txt")
		# Reader.export(moon_met_urls, "url_lists_to_load/moon_met_urls.txt")


	'''
	PARAMS
		filename : Sample cat filename
		sheetname : sample cat sheetname
	RETURNS:
		dictionary of each sampleID each meteorite mapped to the rest of its data from sample catalogue.
	A few sample IDs have multiple entries associated with them. Each sampleID's value in the dictionary is mapped to a list of its entries from 
	the catalogue
	'''
	@staticmethod
	def get_sample_data_info(filename, sheetname):
		workbook = xlrd.open_workbook(filename)
		data_set_xl = workbook.sheet_by_name(sheetname)
		labels = data_set_xl.row_values(0)		
		num_rows = data_set_xl.nrows 
	 	num_cols = data_set_xl.ncols
	 	id_index = labels.index('SampleID')

	 	dic = {}

	 	for i in range(1, num_rows):
	 		values = []
	 		curr_set = data_set_xl.row_values(i)
	 		key = curr_set[id_index]
	 		if key in dic.keys():
				dic[key].append(curr_set)
			else:
				values.append(curr_set)
				dic[key] = values
		return dic


	'''
	PARAMS:
		filename : Spectra_Catalogue filename
		sheetname: Spectra_Catalogue sheetname
	RETURNS:
		list of uniqueids for all meteorites
	In the spectra and sample catalogues, we have multiple spectra id associated with each sample id, which is normal. But we also
	have multiple sample_id associated with some spectra id, which is bad, bc we want some knid of unique identifier. 
	the format for each uniqueid is "spectrumid__sampleid"
	'''
	@staticmethod
	def get_unique_ids(filename, sheetname):
		workbook = xlrd.open_workbook(filename)
		data_set_xl = workbook.sheet_by_name(sheetname)
		labels = data_set_xl.row_values(0)		
		num_rows = data_set_xl.nrows 
	 	num_cols = data_set_xl.ncols

	 	sample_id_index = labels.index('SampleID')
	 	spectrum_id_index = labels.index('SpectrumID')

	 	unique_ids = []

	 	for i in range(1, num_rows):
	 		curr_row = data_set_xl.row_values(i)
	 		spectrum_ID = curr_row[spectrum_id_index]
	 		sample_ID = curr_row[sample_id_index]
 
	 		unique_indentifier = spectrum_ID + "__" + sample_ID
	 		unique_ids.append(unique_indentifier)

	 	return unique_ids


	'''
	 PARAMS 
	 	met_type: whether this is for other , moon , or mars  meteorites 
	 	unique_ids : list of all unique ids for all meteorites in sample catalogue
	 	sample_dic : sample data dictionary 
	 RETURNS 
	 	dictionary of unique id for each met to the url in which its spectra data is stored 
	 	in relab
	'''
	@staticmethod
	def get_urls_to_load(met_type, unique_ids, sample_dic):
	 	list_for_met_type = []
	 	unique_id_to_path_mapping = {}
	 	for elem in unique_ids:
	 		sample_id = elem.split("__")[1]
	 		if sample_id in sample_dic.keys():
	 			value_for_sample_id = sample_dic[sample_id][0]
	 			met = value_for_sample_id[5]
	 			if met == met_type:
	 				path = Reader.construct_path(elem)
	 				if elem in unique_id_to_path_mapping:
	 					print "duplicate unique id found for " + elem
	 					# the duplicates are literal duplicates, there is no difference between them except for sometimes a description. 
	 					# I think we can just ignore them, or grab whichever table value is fullest 
	 				else:
	 					unique_id_to_path_mapping[elem] = path
	 				list_for_met_type.append(path)

	 	return unique_id_to_path_mapping


	'''
	PARAMS
		unique_id : unique id for meteorite
	RETURNS
		path (url for this meteorites sepctra data) in relab database website
	'''
	@staticmethod
	def construct_path(unique_id):
		sample_id = unique_id.split("__")[1]
		base_path = sample_id.split('-')
		spectra_id = unique_id.split("__")[0]
		path = 'http://www.planetary.brown.edu/relabdata/data' + '/' + base_path[1].lower() + '/' + base_path[0].lower() + '/' + spectra_id.lower() + '.txt'
		return path
		#print path

	'''
	PARAMS
		url_dic : dictioanry to export
		filename : filename for this dictionary
	'''
	@staticmethod
	def export(url_dic, filename):
		with open(filename, "w") as output:
			output.write(str(url_dic))


#-----------------------------------------------------------------------------------------------------------------------------------------------#

	@staticmethod
	def get_meteorite_types(sample_dic, list_of_ids):

		dic = {}
		for uniqueid in list_of_ids: #
			n = uniqueid.split('-')[:-1]
			sampleid = "-".join(n)
			# if str(uniqueid) == ".DS_Store":
			# 	print "" 
			if str(uniqueid) != ".DS_Store":
				id_info_list = sample_dic[sampleid] #multiple entries in catalogue with same sampleid
				list_of_meteorite_data = [] #list of lists. If sample ID has 3 entries, then for this dic[unique id] --> [[Type1, subtype], [type1, subtype]...]
				for entry in id_info_list: #for each value list associated with this sampleid 
					#meteorite_types = []
					general = entry[6]
					type1 = entry[8]
					sub_type = entry[10]
					full_type = general.strip() + '__' + type1.strip() + '__' + sub_type.strip()
					# if str(sub_type) == "":
					# 	print uniqueid	
					list_of_meteorite_data.append(full_type)
		 		dic[uniqueid.split('.')[0]] = list_of_meteorite_data
		return dic

	@staticmethod
	def get_id_type_map_regex(id_type_map):
		set_list = []
		set_  = set()
		map_ = {} #regex --> orig_name
		for elem in id_type_map.keys():
			val = id_type_map[elem]
			s = re.sub('[^0-9a-zA-Z]+', '*', val[0])
			if s not in map_:
				map_[s] = val
		return map_

#-------------------------------------------------------------------------------------------------------------------------------------------------#
	
	'''
	PARAMS: 
		list_of_files: list of unprocessed filenames
	RETURNS:
		dictioanry of old sample_ids to new sample_ids
	'''
	@staticmethod
	def get_sketchy_mapping(list_of_files):
		old_to_new = {}
		for file_ in list_of_files:
			with open(file_, "r") as f:
				old_samp_id = file_.split('/')[-1].split('__')[1].split('.')[0]
				first_line = f.readline()
				samp_id_in_file = first_line.split(" ")[-1].split('/')[0]
				if old_samp_id != samp_id_in_file:
					old_to_new[old_samp_id] = samp_id_in_file
		return old_to_new


	'''
	PARAMS: 
		data_dic : data dictionary to be fixed ( replace old sample id keys with new sample id keys)
		files_before_processing: list of unprocessed file names
	RETURNS : 
		fixed data dictionary
	'''
	@staticmethod
	def fix_dic(data_dic, files_before_processing):
		old_id_to_new_ids = Reader.get_sketchy_mapping(files_before_processing)
		for old in old_id_to_new_ids.keys():
			if old in data_dic.keys():
				value = data_dic[old]
				new_key = old_id_to_new_ids[old]
				if new_key not in data_dic.keys():
					data_dic[new_key] = value
					#del data_dic[old]
		return data_dic






