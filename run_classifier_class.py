from scraperv2 import *
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
import os

class Classify:

#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
# 	The following methods are used to load spectra files from relab data website. These files have not yet been formatted to fit the classifier. 
#	They are stored in the folders Moon_Met, Mars_Met, Other_Met


	'''
	MAIN METHOD
	PARAMS:
		unique_id_url_dic : moon_met, mars_met, or other_met dic. mapping of unique id to spectra file url for each met
		met : indicated whether moon , mars or other met. 
	This function load  all spectra files from relab data website and saves them each in a file on computer. 

	'''
	@staticmethod
	def load_unprocessed_files(unique_id_url_dic, met):
		numfiles = len(unique_id_url_dic.keys())
		print numfiles

		for key in unique_id_url_dic.keys():
			filename = ""
			if met == 'Gaffey':
				name = key.split('__')[1].rstrip() + '-' + key.split('__')[0]
				filename = "spectra_data_unprocessed_gaffey/" + name + '.txt'
			else:
				filename = "spectra_data_unprocessed_all/" + met +'/' + key + ".txt"
			curr_url = unique_id_url_dic[key]
			Classify.get_spec_data_for_id(curr_url, filename)
			time.sleep(2)


	'''
	PARAMS:
		curr_url : current url for spectra file
		filename : filename to save the spectra file to
	this funciton sends a request to the relab site that has all the spectra files. It then saves the file associtated with this specific
	url to the computer

	'''
	@staticmethod
	def get_spec_data_for_id(curr_url, filename):
		try:
			response = urllib2.urlopen(curr_url)
			data = response.read()
			Classify.export(data, filename)

		except urllib2.HTTPError, e:
			
			print e.code

	'''
	PARAMS:
		data : spectra data from url 
		file_to_export : name of file in which this data gets saved
	'''
	@staticmethod
	def export(data, file_to_export):
		with open(file_to_export, "w") as text_file:
			text_file.write(data)


	'''
	PARAMS:
		list_ : list of sample ids for each met type (other, mars, moon)
		met: indicates which met type this list belongs to
	RETURNS:
		list of all unprocesed filenames for meteorite spectra 
	'''
	@staticmethod
	def get_filenames_for(list_, met):
		newl= []
		if met == 'Gaffey':
			for elem in list_:
				newelem = 'spectra_data_unprocessed_new/' + str(elem) + '.txt'
				newl.append(newelem)
		else:		
			for elem in list_:
				newelem = 'spectra_data_unprocessed_all/' + met + '/' + str(elem) + '.txt'
				newl.append(newelem)
		return newl

	# @staticmethod
	# def get_files_for_met(dic, met):
	# 	filenames = []
	# 	for key in dic.keys():
	# 		filename = 'spectra_data_unprocessed_all/' + met + '/' + key + '.txt'
	# 		filenames.append(filename)
	# 		print filename
	# 	return filenames



#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
# These methods are used to edit the files so that they work in the classifier. Then they are saved to the folders Moon_Met_edited, Mars_Met_edited
# and Other_Met_edited. 
	
	'''
	MAIN METHOD

	'''
	@staticmethod
	def do_exports(mars_met_dic, moon_met_dic, other_met_dic, mars_met_list, moon_met_list, other_met_list):
		Classify.load_unprocessed_files(mars_met_dic, "Mars_Met") # ----------- load the unprocessed spectra files from relab_data to file once, so that they can 
		Classify.load_unprocessed_files(moon_met_dic, "Moon_Met")            # be accessed every time without having to go to the relab site.
		Classify.load_unprocessed_files(other_met_dic, "Other_Met")

		Classify.export_edited_files(moon_met_list, 'Moon_Met_edited')
		Classify.export_edited_files(mars_met_list, 'Mars_Met_edited')
		Classify.export_edited_files(other_met_list, 'Other_Met_edited')


	'''
	Gaffey files do not need to be edited. 
	'''
	@staticmethod
	def do_exports_gaffey(gaffey_dic):
		Classify.load_unprocessed_files(gaffey_dic, "Gaffey")



	'''
	PARAMS:
		file_list : list of unprocessed file names
		met : met type
	RETURNS
		new file list of edited file names
	'''
	@staticmethod
	def get_edited_filenames(file_list, met):
		new_file_list = []
		for file_ in file_list:
			edited_file_data_list = Classify.edit(file_)
			if edited_file_data_list is not None:
				new_file_path = 'spectra_data_unprocessed_all/' + met + '/' + file_.split('/')[2]
				new_file_list.append(new_file_path)
		return new_file_list
	


	'''
	PARAMS:
		orig_file : original file name
	RETURNS:
		either a none-type or list containing edited file info
	decides which files need to be edited to fit classifier requirements
	'''
	@staticmethod
	def edit(orig_file):
		lines =[]
		if os.path.exists(orig_file):
			with open(orig_file) as f:
				lines = f.read().splitlines()
				headers = lines[0:2]
				del lines[0:2]
				first_pair = lines[0].split('\t')
				first_wavelength = float(first_pair[0])
				last_pair = lines[-1].split('\t')
				last_wavelength = float(last_pair[0])


				empty = []
				#dont do
				if first_wavelength > .85:
					return 

				elif last_wavelength < 2.45:
					return 

				#these are all fine
				elif len(lines) <= 3000 - 2: #-2 for the headers
	 				lines = headers + lines
	 				return lines
				
				#these are too long
				else:
					edited = Classify.cut_file(lines, headers)
					return edited
		else:
			#print ' file doesnt exist ' + orig_file 
			return 

	''' 
	PARAMS:
		lines: list of all lines in this file (minus the first two lines)
		headers : first two lines of file
	RETURNS: 
		either edited[] or shortened[]	
		edited[] is list of file data after taking off the excess on both ends. if there is still too much data, shortened[] is list of file data is after taking out data from intervals within the range
	cuts excess spectra data from files so that they can fit classifier requirements
	'''
	@staticmethod
	def cut_file(lines, headers):
		min_wavelength_1 = .40
		min_wavelength_2 = .80
		max_wavelength = 2.5

		edited = []

		for i in range (0, len(lines)):
			curr_wavelength = float(lines[i].split('\t')[0])
			if (curr_wavelength > min_wavelength_1 or curr_wavelength > min_wavelength_2) and curr_wavelength < max_wavelength:
				edited.append(lines[i])

		shortened = []
		if len(edited) > 3000 :
			difference = len(edited) - 3000
			interval = 3000/difference
			#get an empty file if the interval is 1.
			if interval == 1:
				interval +=1
			counter = 0
			for elem in edited:
				counter+=1
				if counter == interval:
					counter = 0
				else:
					shortened.append(elem)
			shortened = headers + shortened
			return shortened
		else:
			edited = headers + edited
			return edited


	'''
	PARAMS: 
		file_list : list of unedited files
		met : meteorite type (other, mars, moon)
	edits files and exports them to spectra_data_unprocessed_all
	'''
	@staticmethod
	def export_edited_files(file_list, met):
		for file_ in file_list:
			edited_file_data_list = Classify.edit(file_)
			if edited_file_data_list is not None:
				new_file_path = 'spectra_data_unprocessed_all/' + met + '/' + file_.split('/')[2]
				Classify.export_list(edited_file_data_list, new_file_path)	

	'''
	PARAMS:
		edited_file_data_list : edited data to be written to file
		new_file_path : new file name for edited data
	'''
	@staticmethod
	def export_list(edited_file_data_list, new_file_path):
		with open(new_file_path, "w") as text_file:
			for elem in edited_file_data_list:
				text_file.write(str(elem) + '\n')


	

#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#	These methods will run the edited files through the classifier. 
	
	'''
	MAIN METHOD
	PARAMS:
		moon_met_list_edited : list of moon met file names for edited files
		mars_met_list_edited : list of mars met file names for edited files
		other_met_list_edited : list of other met file names for edited files
	runs files in each spectra_data_unprocessed_all met folder through the classifier, and sends emails
	'''
	@staticmethod
	def classify_all(moon_met_list_edited, mars_met_list_edited, other_met_list_edited):
		Classify.run_thru_classifier(moon_met_list_edited)															
		Classify.run_thru_classifier(mars_met_list_edited)					   
		Classify.run_thru_classifier(other_met_list_edited)

	'''
	Submits Gaffey files to classifier and sends them to email
	'''
	@staticmethod
	def classify_gaffey(gaffey_met_list):
		Classify.run_thru_classifier(gaffey_met_list)

	'''
	PARAMS:
		file_list : list of all file names to be run through classifier 
	This function runs files through the BUS-Demeo classifier. The classifier sends results via form of email. 
	'''
	@staticmethod
	def run_thru_classifier(file_list):
		wavelength_range_dic = Classify.get_wavelength_ranges_for_file_list(file_list)
		files = wavelength_range_dic.keys()

		for file_ in files:
			Scraperv2.submit_form1(file_, wavelength_range_dic[file_])
			time.sleep(5)


	'''
	PARAMS: 
		file_list : list of files to be run thru the demeo classifier
	RETURNS:
		dictionary of each file in file_list mapped to either 'visir' or 'ir' for the classifier requirements
	'''
	@staticmethod
	def get_wavelength_ranges_for_file_list(file_list):
		dic = {}
		for file_ in file_list:
			with open(file_) as f:
				lines = f.read().splitlines()
				first_wavelength = lines[2].split('\t')[0]
				if float(first_wavelength) > .45:
					value = 'ir'
					dic[file_] = value
				elif float(first_wavelength) <=.45 :
					value = 'visir'
					dic[file_] = value
		return dic











