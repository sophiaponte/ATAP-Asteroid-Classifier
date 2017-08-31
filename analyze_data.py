
from reader_classv2 import *
from run_classifier_class import *
from email_getter_class import *
from processed_data_load import *
from training_file_converter import *
from gaffey_data import *
from naive_bayes_type_v_class import *
from naive_bayes_pca_v_type import *
import sys
import math
import xlrd
import json
import ast
import os
import xlwt
import matplotlib.pyplot as plt
import numpy as np



def run_all_data():

	#Reader.run_reader() ------------------------------------------------ loads the other, mars, and moon dics to files that can be read. It is faster
	#																	  create the dics once and read them from file every time rather than creating
	#																	  the dics every time. 

	#Gaffey.load_and_classify_all_gaffey_files() ------------------------------- main method for gaffey data. loads unprocessed spectra files to comptuter into spectra_data_unprocessed_gaffey, 
	#																	  classifies them with the demeo classifier, and saves the files to spectra_data_processed_new

	mars_file = open('url_dics_to_load/mars_met_urls.txt', 'r')
	mars_met_dic = ast.literal_eval(mars_file.read())

	other_file = open('url_dics_to_load/other_met_urls.txt', 'r')
	other_met_dic = ast.literal_eval(other_file.read())

	moon_file = open('url_dics_to_load/moon_met_urls.txt', 'r')
	moon_met_dic = ast.literal_eval(moon_file.read())

	sample_file = open('url_dics_to_load/sample_data_dictionary.txt', 'r')
	sample_data_dic = ast.literal_eval(sample_file.read()) #some filepath do not exist in sample id dictionary. MB-TXH-064



	#ScraperMetbull.main() ----------------------------------------------------------------------------------------------loads the name to sample id dictionary and stores it. also loads sample id
	#																													 to subtype_metbull map from metbull data

	name_file = open('name_dic_updated.txt', 'r')
	name_dic = ast.literal_eval(name_file.read())

	subtype_metbull_file = open('id_subclass_map_updated_v2.txt', 'r')
	subtype_metbull_dic = ast.literal_eval(subtype_metbull_file.read()) #--------------------------------------------------id to metbull subtype


	tax_to_complex_map = read_mapping('tax_to_complex.txt')
	complex_to_complex_prime_map = read_mapping('complex_to_complex_prime.txt')
	type_complex_map = read_mapping('type_complex_table.txt')
	type_complex_prime_map = read_mapping('type_complex_table_level_2.txt')

	#met filenames before checking whether their formats match the classifier requirements (in Moon_Met folder)
	moon_met_list = Classify.get_filenames_for(moon_met_dic.keys(), 'Moon_Met')
	mars_met_list = Classify.get_filenames_for(mars_met_dic.keys(), 'Mars_Met')
	other_met_list = Classify.get_filenames_for(other_met_dic.keys(), 'Other_Met')



	#Classify.do_exports(mars_met_dic, moon_met_dic, other_met_dic, mars_met_list, moon_met_list, other_met_list) -----------loads unprocessed spectra files
	#																													     to computer. also exports edited files
	#																														 to fit classifier requirements to computer

	moon_met_list_edited = Classify.get_edited_filenames(moon_met_list, 'Moon_Met_edited') #---------------------------------lists of all edited files that were sent to email.
	mars_met_list_edited = Classify.get_edited_filenames(mars_met_list, 'Mars_Met_edited')
	other_met_list_edited = Classify.get_edited_filenames(other_met_list, 'Other_Met_edited')
	
	files_before_processing = moon_met_list_edited + mars_met_list_edited + other_met_list_edited # ------------------------format spec__samp


	#Classify.classify_all(moon_met_list_edited, mars_met_list_edited, other_met_list_edited) ------------------------------- runs all files thru classifier, sends emails

	#Email_getter.get_all_email_data("Mars_Met", "Other_Met", "Moon_Met")---------------------------------------------------- extract data from emails and saves data to spectra_data_processed_all folders


	moon_met_processed_files = Email_getter.get_processed_filenames("Moon_Met")# -------------------------------------------- at this point, all classified files are loaded into the computer
	mars_met_processed_files = Email_getter.get_processed_filenames("Mars_Met")
	other_met_processed_files = Email_getter.get_processed_filenames("Other_Met")
	gaffey_processed_files = Email_getter.get_processed_filenames("Gaffey")

	remove_deleted_gaffey_files(gaffey_processed_files)

	files_after_processing =  moon_met_processed_files + mars_met_processed_files + other_met_processed_files # ------------ all filenames that have been processed by demeo classifier

	edited_subtype_metbull_dic = Reader.fix_dic(subtype_metbull_dic, files_before_processing) #
	edited_name_dic = Reader.fix_dic(name_dic, files_before_processing)
	sample_data_dic = Reader.fix_dic(sample_data_dic, files_before_processing)

	all_unique_ids = get_all_unique_ids("spectra_data_processed_all", "spectra_data_processed_new") #---------------------------new filenames (spectra_data_processed_all is mets, spectra_data_processed_new is gaffey )

	id_type_map = Reader.get_meteorite_types(sample_data_dic, all_unique_ids) #------------------------------------------------uniqueid --> [type1/subtype]
	id_type_map_regex = Reader.get_id_type_map_regex(id_type_map) #------------------------------------------------------------regex --> [type/subtype] want (uniqueid --> regex)

	'''
	we want to make the meteorites have the regexed types (but full names)
	'''
	moon_met_meteorites = convert_to_meteorites(moon_met_processed_files, "Moon_Met", id_type_map, id_type_map_regex, edited_subtype_metbull_dic, edited_name_dic, tax_to_complex_map, type_complex_map, type_complex_prime_map)
	mars_met_meteorites = convert_to_meteorites(mars_met_processed_files, "Mars_Met", id_type_map, id_type_map_regex, edited_subtype_metbull_dic, edited_name_dic, tax_to_complex_map, type_complex_map, type_complex_prime_map)
	other_met_meteorites = convert_to_meteorites(other_met_processed_files, "Other_Met", id_type_map, id_type_map_regex, edited_subtype_metbull_dic, edited_name_dic, tax_to_complex_map, type_complex_map, type_complex_prime_map)
	gaffey_meteorites = convert_to_meteorites(gaffey_processed_files, "Gaffey", id_type_map, id_type_map_regex, edited_subtype_metbull_dic, edited_name_dic, tax_to_complex_map, type_complex_map, type_complex_prime_map)

	all_meteorites = moon_met_meteorites + mars_met_meteorites + other_met_meteorites + gaffey_meteorites

	#export_to_r(all_meteorites) #------------ exports all meteorites into a filet hat can be read in r

	#Trainer.create_all_files_random(all_meteorites) -- to create the 'random' training files
	#Trainer.create_robust_files(all_meteorites) -- creates the training files for robust training 

#	Bayes_Name.test_robustness(3, True, 'complex_prime_type')
#	Bayes_Pca.test_robustness(3, True, 'complex_prime_type')






'''
PARAMS:
	gaffey_processed_files: list of gaffey processed filenames
removes weird deleted one
'''
def remove_deleted_gaffey_files(gaffey_processed_files):
	for file_ in gaffey_processed_files:
		if ".DS_Store" in file_:
			gaffey_processed_files.remove(file_)


'''
PARAMS: 
	dic : dictionary to print visually
'''
def print_visual(dic):
	with open('meteorite_names.txt', 'w') as f:
		for k,v in dic.items():
			str_ = str(k) + " : " + str(v[0]) + '\n'
 			f.write(str_);

'''
PARAMS: 
	filename : name of dictionary file to read : format 'key__value'
RETURNS: 
	dictionary representation of this file
'''
def read_mapping(filename):
	dic = {}
	with open(filename, 'r') as f:
		for line in f:
			class_ = line.split('__')[0].rstrip().lstrip()
			complex_class = line.split('__')[1].rstrip().lstrip()
			dic[class_] = complex_class
	return dic


'''
PARAMS:
	meteorites: list of meteorite objects
writes all meteorites to r file : "r_file_final_v2.csv"
'''
def export_to_r(meteorites):
	writer = csv.writer(open("r_file.csv", 'w'))
	first_line = ["uniqueID", "spectrumID", "name", "asteroid classes", "slope", "sampleID", "pca_1","pca_2", "pca_3","pca_4","pca_5", "General Type", "Type 1", "subtype", "metbull type", "clan subtype", "class subtype"]
	writer.writerow(first_line)
	for meteorite in meteorites:
		data_list = []
		data_list.append(meteorite.unique_id)
		data_list.append(meteorite.spec_id)
		data_list.append(meteorite.name)
		classes_ = "__".join(meteorite.classes)
		data_list.append(classes_)
		data_list.append(meteorite.slope)
		data_list.append(meteorite.sample_ID)
		data_list.append(meteorite.pca_components[0])
		data_list.append(meteorite.pca_components[1])
		data_list.append(meteorite.pca_components[2])
		data_list.append(meteorite.pca_components[3])
		data_list.append(meteorite.pca_components[4])
		types = meteorite.types[0].split('__')
		for type_ in types:
			data_list.append(type_)
		data_list.append(meteorite.subtype)
		data_list.append(meteorite.complex_type)
		data_list.append(meteorite.complex_prime_type)
		writer.writerow(data_list)



'''
PARAMS:
	files: list of processed filenames that contain processed spectra data from demeo classifier
	met: type of meteorite (moon, mars, other, gaffey)
	id_type_map : mapping of unique id to relab type1/subtype
	id_type_map_regex : mapping of regular expression of subtype to actual subtype
	subtype_metbull_dic : mapping of sample id to metbull subtype
	name_dic : mapping of sample id to name 
	tax_to_complex_map : mapping of asteroid tax class to its complex type
	type_complex_map : mapping of meteorite type to its complex type (clan)
	type_complex_prime_map : mapping of meteorite type to its complex prime type (class)
RETURNS: 
	list of meteorite objects
This funciton takes all the different data files and dics that we have created with Reader class, Email_getter class, scraper classes etc 
and creates a list of meteorite objects containing all this data 
'''
def convert_to_meteorites(files, met, id_type_map, id_type_map_regex, subtype_metbull_dic, name_dic, tax_to_complex_map, type_complex_map, type_complex_prime_map):
	meteorites = []
	if met == "Gaffey":
		for elem in files:
			meteorite_file = 'spectra_data_processed_new/' + elem
			with open (meteorite_file, "r") as f:
				meteorite_text=f.readlines()
				meteorite = Meteorite(meteorite_text, meteorite_file, id_type_map, id_type_map_regex, subtype_metbull_dic, name_dic, tax_to_complex_map, type_complex_map, type_complex_prime_map)
				meteorites.append(meteorite)
	else:
		for elem in files:
			meteorite_file = 'spectra_data_processed_all/' + met + '/' + elem
			with open (meteorite_file, "r") as f:
				meteorite_text=f.readlines()
				meteorite = Meteorite(meteorite_text, meteorite_file, id_type_map, id_type_map_regex, subtype_metbull_dic, name_dic, tax_to_complex_map, type_complex_map, type_complex_prime_map)
				meteorites.append(meteorite)

	return meteorites

def get_all_unique_ids(spectra_data_processed_all, spectra_data_processed_new):
	all_files = []
	for filename in os.listdir(spectra_data_processed_all + '/Moon_Met'):
		all_files.append(filename)
	for filename in os.listdir(spectra_data_processed_all + '/Mars_Met'):
		all_files.append(filename)
	for filename in os.listdir(spectra_data_processed_all + '/Other_Met'):
		all_files.append(filename)
	for filename in os.listdir(spectra_data_processed_new):
		if filename == "":
			print "missing file = " + filename
		all_files.append(filename)

	
	return all_files

















run_all_data()


#particular to this gaffey dataset. 
# def run_gaffey_data():
	
# 	#----------load id path mapping dic'''
# 	gaffey_data = Reader.read_gaf_data(GAFFEY_XFILE, GAFFEY_SHEET_IN_FILE) # -------------------------- this is a dictionary of a SampleID to path mapping for every gaffey data spectrumID listed
# 	#Reader.export(gaffey_data, GAFFEY_ID_PATH_MAPPTING_OUTPUT)

# 	#---------scrape '''
# 	#Scraper.send_emails_for_files()
# 	#Scraper.send_files_to_computer()

# 	#----------get data from emails, load to computer file spectra_data_processeed_new '''
# 	#Email_getter.connect_to_account();
# 	#list_of_processed_files = Email_getter.connect_to_account("list")

# 	#temp_export_file = open('temp_export_file.txt', 'r')
# 	#list_of_processed_files = ast.literal_eval(temp_export_file.read()) #read in entire list as a string
# 	#print list_of_processed_files

# 	#-----------create asteroid objects, put them into dic'''

# 	list_of_processed_files = get_processed_filenames("Gaffey")

# 	list_of_meteorites = []

# 	for meteorite_file in list_of_processed_files:
# 		#create new meteorite object
# 		with open (meteorite_file, "r") as myfile:
# 			meteorite_text=myfile.readlines()
# 			meteorite = Meteorite(meteorite_text, meteorite_file)
# 			Meteorite.print_meteorite(meteorite)


# 	#print list_of_processed_files
# 	#print gaffey_data











# def bar_plots(meteorites,type_complex_map, level_2_map, complex_class_map):

# 	classes_list = []
# 	dic = {}

# 	for meteorite in meteorites:
# 		classes = meteorite.classes
# 		for class_ in classes:
# 			class_ = class_.split('-')[0]
# 			if class_ == 'indeterminate':
# 				class_ = 'unk'
# 			classes_list.append(class_)
# 			if class_ not in dic.keys():
# 				dic[class_] = 1
# 			elif class_ in dic.keys():
# 				val = dic[class_]
# 				val+=1
# 				dic[class_] = val
# 			if class_ not in dic.keys():
# 				dic[class_] = 1
# 			elif class_ in dic.keys():
# 				val = dic[class_]
# 				val+=1
# 				dic[class_] = val
# 	classes = set(classes_list)
# 	class_list = []
# 	count_list = []
# 	for elem in classes:
# 		class_list.append(elem)
# 		count_list.append(dic[elem])

# 	# ['Svw', 'Cgh', 'Sqw', 'Sq', 'A', 'C', 'B', 'D', 'Qw', 'Sr', 'K', 'Sw', 'L', 'O', 'Sv', 'Q', 'S', 'R', 'Srw', 'V', 'X', 'Sa', 'Xk', 'Ch', 'Xn', 'Xc', 'Cb', 'Cg', 'Xe', 'Vw', 'unk', 'T']
# 	# [10,     104,    8,    460, 218, 880, 384, 226,  24,   254, 708,  30,  364, 302,  36,  1012, 282, 86,   24,  1042, 332, 64, 1022,   592, 1022, 446,   22,   54,  1770,  38,   148,   6]

# 	#





# 	# dic_ = {}
# 	# for elem in class_list:
# 	# 	index = class_list.index(elem)
# 	# 	if elem == 'unk':
# 	# 		elem = 'indeterminate'
# 	# 	complex_ = complex_class_map[elem]
# 	# 	if complex_ not in dic_.keys():
# 	# 		if complex_ == 'indeterminate':
# 	# 			complex_ = 'unk'
# 	# 		dic_[complex_] = count_list[index]
# 	# 	elif complex_ in dic_.keys():
# 	# 		val = dic_[complex_]
# 	# 		val += count_list[index]
# 	# 		dic_[complex_] = val

# 	# count_list_=[]
# 	# for elem in dic_.keys():
# 	# 	count_list_.append(dic_[elem])


# 	f = np.arange(len(set(dic_.keys())))

# 	plt.bar(f, count_list_, align='center', alpha=0.5)
# 	plt.xticks(rotation=90)
# 	plt.xticks(f, dic_.keys())

# 	plt.tick_params(labelsize=5)
# 	plt.ylabel('num')
# 	plt.title('asteroid class complex &')
 
# 	plt.show()

# 	met_dic = {}
# 	for meteorite in meteorites:
# 		type_ = 'unk'
# 		if type_ == None:
# 			type_ = meteorite.types[0].split('__')[2]
# 		else:
# 			type_ = meteorite.subtype
# 		if type_ not in met_dic.keys():
# 			met_dic[type_ ] = 1
# 		elif type_ in met_dic.keys():
# 			val = met_dic[type_]
# 			val +=1
# 			met_dic[type_] = val

# 	met_count_list = []
# 	met_type_list = met_dic.keys()
# 	for met in met_type_list:
# 		met_count_list.append(met_dic[met])

# 	a = np.arange(len(set(met_type_list)))	
# 	b = met_count_list




# 	complex_met = {}
# 	for met_ in met_type_list:
# 		if met_ is not None:
# 			comp = type_complex_map[met_]
# 			if comp not in complex_met.keys():
# 				complex_met[comp] = met_dic[met_]
# 			elif comp in complex_met.keys():
# 				val = complex_met[comp]
# 				val += met_dic[met_]
# 				complex_met[comp] = val

# 	comp_met_type_list = complex_met.keys()
# 	comp_met_count_list = []
# 	for comp_met in comp_met_type_list:
# 		comp_met_count_list.append(complex_met[comp_met])

# 	c = np.arange(len(set(comp_met_type_list)))


# 	complex_level_2_dic = {}
# 	for type_ in complex_met.keys():
# 		level_2 = level_2_map[type_]
# 		if level_2 not in complex_level_2_dic.keys():
# 			complex_level_2_dic[level_2] = complex_met[type_]
# 		elif level_2 in complex_level_2_dic.keys():
# 			val = complex_level_2_dic[level_2]
# 			val += complex_met[type_]
# 			complex_level_2_dic[level_2] = val


# 	comp_met_type_list_2 = complex_level_2_dic.keys()
# 	comp_met_count_list_2 = []
# 	for met in comp_met_type_list_2:
# 		comp_met_count_list_2.append(complex_level_2_dic[met])

# 	e = np.arange(len(set(comp_met_type_list_2)))

# 	# plt.bar(e, comp_met_count_list_2, align='center', alpha=0.5)
# 	# plt.xticks(rotation=90)
# 	# plt.xticks(e, comp_met_type_list_2)

# 	# plt.tick_params(labelsize=5)
# 	# plt.ylabel('num')
# 	# plt.title('met types -- class')
 
# 	# plt.show()




# 	# plt.bar(c, comp_met_count_list, align='center', alpha=0.5)

# 	# plt.xticks(rotation=90)
# 	# plt.xticks(c, comp_met_type_list)

# 	# plt.tick_params(labelsize=5)
# 	# plt.ylabel('num')
# 	# plt.title('met types -- clan')
 
# 	# plt.show()



# 	# plt.bar(a, met_count_list, align='center', alpha=0.5)

# 	# plt.xticks(rotation=90)
# 	# plt.xticks(a, met_type_list)

# 	# plt.tick_params(labelsize=5)
# 	# plt.ylabel('num')
# 	# plt.title('met types')
 
# 	# plt.show()


# 	# y = np.arange(len(classes))
# 	# x = count_list
 
# 	# plt.bar(y, count_list, align='center', alpha=0.5)
# 	# plt.xticks(y, class_list)
# 	# plt.ylabel('num')
# 	# plt.title('Class types')
 
# 	# plt.show()





# def create_training_and_test_files_complex(meteorites, algorithm, training_num, met_level, ast_level, class_mapping_complex, class_mapping_prime, type_mapping_complex, type_mapping_prime):
# 	num_mets = len(meteorites)
# 	num_training_lines = int(num_mets*training_num)
# 	if algorithm == "naive_bayes_name":
# 		filename = "training_file_" + algorithm + '_complex_all.txt'
# 		with open(filename, 'w') as f:
# 			for i in range(0, num_training_lines):
# 				meteorite = meteorites[i]
# 				for class_ in meteorite.classes:
# 					class_to_write = ""
# 					subtype_to_write = ""

# 					complex_class = class_mapping_complex[class_.split('-')[0]]
# 					complex_prime_class = class_mapping_prime[complex_class]
# 					subtype = ""
# 					if meteorite.subtype == None:
# 						subtype = meteorite.types[0].split('__')[2]
# 					else:
# 					 	subtype = meteorite.subtype
# 					complex_subtype = type_mapping_complex[subtype]
# 					complex_prime_subtype= type_mapping_prime[complex_subtype]
					
# 					if ast_level == 'complex':
# 						class_to_write = complex_class
# 					elif ast_level == 'prime':
# 						class_to_write = complex_prime_class
# 					else:
# 						class_to_write = class_

# 					if met_level == 'complex':
# 						subtype_to_write = complex_subtype
# 					elif met_level == 'prime':
# 						subtype_to_write = complex_prime_subtype	
# 					else:
# 						subtype_to_write = subtype

# 					line = class_to_write + '___' + subtype_to_write + '\n'
# 					f.write(line)

# 		filename = "test_file_" + algorithm + '_complex_all.txt'
# 		with open(filename, 'w') as f:
# 			for i in range(num_training_lines, num_mets):
# 				meteorite = meteorites[i]
# 				for class_ in meteorite.classes:
# 					class_to_write = ""
# 					subtype_to_write = ""

# 					complex_class = class_mapping_complex[class_.split('-')[0]]
# 					complex_prime_class = class_mapping_prime[complex_class]
# 					subtype = ""
# 					if meteorite.subtype == None:
# 						subtype = meteorite.types[0].split('__')[2]
# 					else:
# 					 	subtype = meteorite.subtype

# 					complex_subtype = type_mapping_complex[subtype]
# 					complex_prime_subtype = type_mapping_prime[complex_subtype]

# 					if ast_level == 'complex':
# 						class_to_write = complex_class
# 					elif ast_level == 'prime':
# 						class_to_write = complex_prime_class
# 					else:
# 						class_to_write = class_

# 					if met_level == 'complex':
# 						subtype_to_write = complex_subtype
# 					elif met_level == 'prime':
# 						subtype_to_write = complex_prime_subtype	
# 					else:
# 						subtype_to_write = subtype

# 					line = class_to_write + '___' + subtype_to_write + '\n'
# 					f.write(line)

# 	elif algorithm == "naive_bayes_pca":
# 		filename = "training_file_" + algorithm + '_complex_all.txt'
# 		with open(filename, 'w') as f:
# 			for i in range(0, num_training_lines):
# 				meteorite = meteorites[i]
# 				info = meteorite.pca_components
# 				line = ""
# 				subtype = ""
# 				for elem in meteorite.pca_components:
# 					line += str(elem) + '__'
# 				if meteorite.subtype == None:
# 					subtype = meteorite.types[0].split('__')[2]
# 				else:
# 				 	subtype = meteorite.subtype

# 				subtype_to_write = ""

# 				complex_subtype = type_mapping_complex[subtype]
# 				complex_subtype_level_2 = type_mapping_prime[complex_subtype]
# 				if met_level == 'complex':
# 					subtype_to_write = complex_subtype
# 				elif met_level == 'prime':
# 					subtype_to_write = complex_prime_subtype	
# 				else:
# 					subtype_to_write = subtype

# 				line += complex_subtype_level_2 + '\n'
# 				f.write(line)
# 		filename = "test_file_" + algorithm + '_complex_all.txt'
# 		with open(filename, 'w') as f:
# 			for i in range(num_training_lines, num_mets):
# 				meteorite = meteorites[i]
# 				info = meteorite.pca_components
# 				line = ""
# 				subtype = ""
# 				for elem in meteorite.pca_components:
# 					line += str(elem) + '__'
# 				if meteorite.subtype == None:
# 					subtype = meteorite.types[0].split('__')[2]
# 				else:
# 				 	subtype = meteorite.subtype
# 				subtype_to_write = ""
# 				complex_subtype = type_mapping_complex[subtype]
# 				complex_subtype_level_2 = type_mapping_prime[complex_subtype]
# 				if met_level == 'complex':
# 					subtype_to_write = complex_subtype
# 				elif met_level == 'prime':
# 					subtype_to_write = complex_prime_subtype	
# 				else:
# 					subtype_to_write = subtype
# 				line += subtype_to_write + '\n'
# 				f.write(line)
				


# def create_training_and_test_files_for(meteorites, algorithm, training_num):
# 	num_mets = len(meteorites)
# 	num_training_lines = int(num_mets*training_num)

# 	if algorithm == "naive_bayes_pca":
# 		filename = "training_file_" + algorithm + '.txt'
# 		with open(filename, 'w') as f:
# 			for i in range(0, num_training_lines):
# 				meteorite = meteorites[i]
# 				info = meteorite.pca_components
# 				line = ""
# 				subtype = ""
# 				for elem in meteorite.pca_components:
# 					line += str(elem) + '__'
# 				if meteorite.subtype == None:
# 					subtype = meteorite.types[0].split('__')[2]
# 				else:
# 				 	subtype = meteorite.subtype
# 				line += subtype + '\n'
# 				f.write(line)

# 		filename = "test_file_" + algorithm + ".txt"
# 		with open(filename, 'w') as f:
# 			for i in range(num_training_lines, num_mets):
# 				meteorite = meteorites[i]
# 				info = meteorite.pca_components
# 				line = ""
# 				subtype = ""
# 				for elem in meteorite.pca_components:
# 					line += str(elem) + '__'
# 				if meteorite.subtype == None:
# 					subtype = meteorite.types[0].split('__')[2]
# 				else:
# 				 	subtype = meteorite.subtype
# 				line += subtype + '\n'
# 				f.write(line)
# 	elif algorithm == "naive_bayes_name":
# 		filename = "training_file_" + algorithm + '.txt'
# 		with open(filename, 'w') as f:
# 			for i in range(0, num_training_lines):
# 				meteorite = meteorites[i]
# 				for class_ in meteorite.classes:
# 					subtype = ""
# 					if meteorite.subtype == None:
# 						subtype = meteorite.types[0].split('__')[2]
# 					else:
# 					 	subtype = meteorite.subtype
# 					line = class_ + '___' + subtype + '\n'
# 					f.write(line)
# 		filename = "test_file_" + algorithm + '.txt'
# 		with open(filename, 'w') as f:
# 			for i in range(num_training_lines, num_mets):
# 				meteorite = meteorites[i]
# 				for class_ in meteorite.classes:
# 					subtype = ""
# 					if meteorite.subtype == None:
# 						subtype = meteorite.types[0].split('__')[2]
# 					else:
# 					 	subtype = meteorite.subtype
# 					line = class_ + '___' + subtype + '\n'
# 					f.write(line)
	 


# 	##elif algorithm == "naive_bayes_name":	

# def create_naive_bayes_pca_training_file(meteorites, filename):
# 	with open(filename, 'w') as f:
# 		for meteorite in meteorites:
# 			info = meteorite.pca_components
# 			line = ""
# 			subtype = ""
# 			for elem in meteorite.pca_components:
# 				line += str(elem) + '__'
# 			if meteorite.subtype == None:
# 				subtype = meteorite.types[0].split('__')[2]
# 			else:
# 			 	subtype = meteorite.subtype
# 			line += subtype + '\n'
# 			f.write(line)



# def create_training_file(meteorites, filename):
# 	with open(filename, 'w') as f:
# 		for meteorite in meteorites:
# 			for class_ in meteorite.classes:
# 				subtype = ""
# 				if meteorite.subtype == None:
# 					subtype = meteorite.types[0].split('__')[2]
# 				else:
# 				 	subtype = meteorite.subtype
# 				line = class_ + '___' + subtype + '\n'
# 				f.write(line)



	

	#Trainer.create_all_files_random(all_meteorites)








# def create_training_and_test_files(meteorites, algorithm, training_num, ast_complexity, met_complexity, slope):
# 	num_mets_train = int(len(meteorites)*training_num)
# 	num_mets_test = len(meteorites) - num_mets_train
# 	if algorithm == 'naive_bayes_name':
# 		create_training_or_test_file(meteorites, algorithm, 0, num_mets_train, ast_complexity, met_complexity, slope)
# 		create_training_or_test_file(meteorites, algorithm, num_mets_train, len(meteorites), ast_complexity, met_complexity, slope)
# 	elif algorithm == 'naive_bayes_pca':
# 		create_training_or_test_file(meteorites, algorithm, 0, num_mets_train, ast_complexity, met_complexity, slope)
# 		create_training_or_test_file(meteorites, algorithm, num_mets_train, len(meteorites), ast_complexity, met_complexity, slope)


# def create_training_and_test_files_random(meteorites, algorithm, met_complexity, slope):

# 	if algorithm == 'naive_bayes_name':
# 		create_training_or_test_file_random(meteorites, algorithm, 'training_file', met_complexity, slope)
# 		create_training_or_test_file_random(meteorites, algorithm, 'test_file', met_complexity, slope)
# 	elif algorithm == 'naive_bayes_pca':
# 		create_training_or_test_file_random(meteorites, algorithm, 'training_file', met_complexity, slope)
# 		create_training_or_test_file_random(meteorites, algorithm, 'test_file', met_complexity, slope)

# def create_training_or_test_file_random(meteorites, algorithm, file_type, met_complexity, slope):


# 	filename = ""
# 	if file_type == 'training_file' and algorithm == 'naive_bayes_name':
# 		filename = 'training_files_random/' + algorithm  + '_' + met_complexity + '_training.txt'
# 	if file_type == 'test_file' and algorithm == 'naive_bayes_name':
# 		filename = 'test_files_random/' + algorithm  + '_' + met_complexity + '_test.txt'
# 	if file_type == 'training_file' and algorithm == 'naive_bayes_pca':
# 		filename = 'training_files_random/' + algorithm  + '_' + met_complexity + '_training.txt'
# 	if file_type == 'test_file' and algorithm == 'naive_bayes_pca':
# 		filename = 'test_files_random/' + algorithm + '_' + met_complexity + '_test.txt'

# 	if slope:
# 		filename = filename.split('.')[0] + '_slope.txt'

# 	total_range = range(0,len(meteorites))
# 	test_range = range(0,len(meteorites),19)
# 	training_range = [index for index in total_range if index not in test_range]

# 	if(file_type == 'training_file'):
# 		create_file(meteorites, algorithm, filename, training_range, slope, met_complexity)
# 	elif file_type == 'test_file':
# 		create_file(meteorites, algorithm, filename, test_range, slope, met_complexity)


# def create_file(meteorites, algorithm, filename, training_or_test_range, slope, met_complexity):
# 	if algorithm == 'naive_bayes_pca':
# 		subtype = ""
# 		pca_arr = []
# 		with  open(filename, 'w') as f:
# 			for index in training_or_test_range:
# 				meteorite = meteorites[index]
# 				if met_complexity == 'relab_type':
# 					subtype = meteorite.subtype
# 					if subtype == 'None':
# 						subtype = meteorite.types[0].split('__')[2]
# 				elif met_complexity == 'complex_type':
# 					subtype = meteorite.complex_type
# 				elif met_complexity == 'complex_prime_type':
# 					subtype = meteorite.complex_prime_type
# 				pca_arr = meteorite.pca_components
# 				if slope and met_complexity == 'complex_type':
# 					pca_arr.append(meteorite.slope)
# 				write_pca_line_to_file(f, pca_arr, subtype)

# 	elif algorithm == 'naive_bayes_name':
# 		with open(filename, 'w') as f:
# 			subtype = ""
# 			classes = []
# 			for index in training_or_test_range:
# 				meteorite = meteorites[index]
# 				classes = meteorite.classes
# 				if met_complexity == 'relab_type':
# 					subtype = meteorite.subtype
# 					if subtype == 'None':
# 						subtype = meteorite.types[0].split('__')[2]
# 				elif met_complexity == 'complex_type':
# 					subtype = meteorite.complex_type
# 				elif met_complexity == 'complex_prime_type':
# 					subtype = meteorite.complex_prime_type
# 				write_class_line_to_file(f, classes, subtype)


# def create_training_or_test_file(meteorites, algorithm, start, end, ast_complexity, met_complexity, slope):
# 	filename = ""
# 	if start == 0:
# 		filename = 'training_files/' + algorithm + '_' + ast_complexity + '_' + met_complexity + '_training.txt'
# 	else:
# 		filename = 'test_files/' + algorithm + '_' + ast_complexity + '_' + met_complexity + '_test.txt'

# 	classes = []
# 	#subtype = ""
# 	if algorithm == 'naive_bayes_name':
# 		pca = False
# 		with open(filename, 'w') as f:
# 			subtype = ""
# 			pca_arr = []

# 			for i in range(start,end):
# 				meteorite = meteorites[i]
# 				if ast_complexity == 'demeo_class':
# 					classes = meteorite.classes
# 				elif ast_complexity == 'complex_class':
# 					classes = meteorite.complex_classes
# 				if met_complexity == 'relab_type':
# 					subtype = meteorite.subtype
# 					if subtype == 'None':
# 						subtype = meteorite.types[0].split('__')[2]
# 				elif met_complexity == 'complex_type':
# 					subtype = meteorite.complex_type
# 				elif met_complexity == 'complex_prime_type':
# 					subtype = meteorite.complex_prime_type
# 				write_class_line_to_file(f, classes, subtype)
# 	elif algorithm == 'naive_bayes_pca':
# 		if slope:
# 			filename = filename.split('.')[0] + '_slope.txt'
# 		pca = True
# 		with open(filename, 'w') as f:
# 			subtype = ""
# 			pca_arr = []

# 			for i in range(start, end):
# 				meteorite = meteorites[i]
# 				if met_complexity == 'relab_type':
# 					subtype = meteorite.subtype
# 					if subtype == 'None':
# 						subtype = meteorite.types[0].split('__')[2]
# 				elif met_complexity == 'complex_type':
# 					subtype = meteorite.complex_type
# 				elif met_complexity == 'complex_prime_type':
# 					subtype = meteorite.complex_prime_type
# 				pca_arr = meteorite.pca_components
# 				if slope and met_complexity == 'complex_type':
# 					pca_arr.append(meteorite.slope)
# 				write_pca_line_to_file(f, pca_arr, subtype)



# def write_class_line_to_file(f, arr, subtype):
# 	line = ""
# 	for elem in arr:
# 		f.write(elem + '__' + subtype + '\n')



# def write_pca_line_to_file(f, arr, subtype):
# 	line = ""
# 	for elem in arr:
# 		line += elem + '__'
# 	line += subtype + '\n'
# 	f.write(line)

#def print_type_data(meteorites):
# 	general_list = []
# 	type_1_list = []
# 	combined_list = []
# 	for meteorite in meteorites:
# 		type_ = meteorite.types[0]
# 		general = type_.split('__')[0]
# 		general_list.append(general)

# 		type_1 = type_.split('__')[1]
# 		type_1_list.append(type_1)

# 		combined = general + "__" + type_1
# 		combined_list.append(combined)

# 	gen_set = set(general_list)
# 	type_1_set = set(type_1_list)
# 	combined_set = set(combined_list)

# 	print gen_set
# 	print len(type_1_set)
# 	print len(combined_set)

# 	class_count = {}
# 	for meteorite in meteorites:
# 		classes = meteorite.classes
# 		for class_ in classes:
# 			if class_ in class_count.keys():
# 				val = class_count[class_]
# 				class_count[class_] = val + 1
# 			else:
# 				class_count[class_] = 0

# 	max_ = 0
# 	max_cl = ""
# 	for cl in class_count.keys():
# 		val = class_count[cl]
# 		if val > max_:
# 			max_ = val
# 			max_cl = cl

# 	print max_ 
# 	print max_cl

# 	type_c = {}
# 	for meteorite in meteorites:
# 		type_ = meteorite.types[0]
# 		general = type_.split('__')[0]

# 		type_1 = type_.split('__')[1]

# 		combined = general + "__" + type_1
# 		if combined in type_c.keys():
# 			val = type_c[combined]
# 			type_c[combined] = val + 1
# 		else:
# 			type_c[combined] = 0

# 	max_ = 0
# 	max_cl = ""
# 	for cl in type_c.keys():
# 		val = type_c[cl]
# 		if val > max_:
# 			max_ = val
# 			max_cl = cl

# 	print max_
# 	print max_cl
# def xl_export(dic, filename, sheetname):
# 	workbook = xlwt.Workbook()
# 	worksheet = workbook.add_sheet(sheetname)

# 	master_list = []

# 	if sheetname == "types":
# 		for key in dic.keys():
# 			arr = key.split('__') 
# 			arr.append(str(dic[key]))
# 			master_list.append(arr)
		
# 		for i, l in enumerate(master_list):
# 			for j, col in enumerate(l):
# 				worksheet.write(i, j, col)

# 		workbook.save(filename)
# 	else:
# 		for key in dic.keys():
# 			arr = []
# 			arr.append(key)
# 			arr.append(str(dic[key]))
# 			master_list.append(arr)
		
# 		for i, l in enumerate(master_list):
# 			for j, col in enumerate(l):
# 				worksheet.write(i, j, col)

# 		workbook.save(filename)

	#Meteorite_Analyze.plot_scatter(all_meteorites, class_count_dic,  metbull_type_count_dic)

	#export_to_r(all_meteorites)

	#create_training_file(all_meteorites, "training_file.txt")
	#create_naive_bayes_pca_training_file(all_meteorites, "training_file_bayes_pca.txt")
	#create_training_and_test_files_for(all_meteorites, "naive_bayes_pca", .95)
	#create_training_and_test_files_for(all_meteorites, "naive_bayes_name", .9)
	# slope = True
	# create_training_and_test_files_complex(all_meteorites, "naive_bayes_name", .9, level, tax_to_complex_map, complex_to_complex_prime_map, type_complex_map, type_complex_prime_map, slope)
	# create_training_and_test_files_complex(all_meteorites, "naive_bayes_pca", .9, level, tax_to_complex_map, complex_to_complex_prime_map, type_complex_map, type_complex_prime_map, slope)

	# bar_plots(all_meteorites, type_complex_map, type_complex_prime_map, tax_to_complex_map)
	#Meteorite_Analyze.chord_diagram_table(all_meteorites, class_count_dic.keys(), type_count_dic.keys())


	
	#THIS GOES AFTER ALL UNIQUE IDS
	
	#filtered_sample_dic = {k:v for k,v in sample_data_dic.items() if "Other-Met" in v[0] or "Mars-Met" in v[0] or "Moon-Met" in v[0]}
	
	#id_name_dic = get_names(filtered_sample_dic) #creates name dictionary and writes to file. This dictionary is then manually edited and reloaded
												  #in ScraperMetbull
	# def get_names(dic):
	# 	counter = 0
	# 	name_dic = {}
	# 	name_list = []
	# 	for key in dic.keys():
	# 		values = dic[key]
	# 		name_vals = []
	# 		for value in values:
				
	# 			name = value[1]
	# 			name_vals.append(name)
	# 			name_list.append(name)
	# 		name_dic[key] = name_vals

	# 	#print_visual(name_dic)
	# 	return name_dic
