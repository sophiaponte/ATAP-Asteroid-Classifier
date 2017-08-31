from run_classifier_class import *
import sys
import math
import xlrd
import json
from lxml import html
import requests
import urllib2
import time
import ast


class Gaffey: 


	'''
	MAIN METHOD
		
	This function loads the gaffey url dic, extracts unprocessed files from relab and saves them to computer, sends them to the demeo
	classifier, and extracts the process files from email (and saves them to sepctra_data_processed_new)

	'''
	@staticmethod
	def load_and_classify_all_gaffey_files():
		sample_file = open('url_dics_to_load/sample_data_dictionary.txt', 'r')
		sample_data_dic = ast.literal_eval(sample_file.read()) #some filepath do not exist in sample id dictionary. MB-TXH-064

		gaffey_url_dic = Gaffey.gaffey_url_dic('Gaffey_Spectra.txt', sample_data_dic)
		gaffey_met_list = Gaffey.get_gaffey_unprocessed_filenames(gaffey_url_dic.keys())
		print gaffey_met_list
		Classify.do_exports_gaffey(gaffey_url_dic)
		Classify.classify_gaffey(gaffey_met_list)
		Email_getter.get_all_email_data_gaffey()

		

	'''
	PARAMS: 
		gaffey_spectra_file : the file containing a list of of all gaffey spectra files 
		sample_data_dic : sample data dictionary
	RETURNS:
		dictioanry mappping of gaffey unique ids to the urls in which their spectra files live on the relab site
	'''
	@staticmethod
	def gaffey_url_dic(gaffey_spectra_file, sample_data_dic):
		gaffey_url_dic = {}
		with open(gaffey_spectra_file, 'r') as f:
			first_line = f.readline()
			for line in f:
				sample_id = line.split('\t')[4]
				spectrum_id = line.split('\t')[3].split('.')[0]
				unique_id = spectrum_id + '__' + sample_id.rstrip()
				url = 'http://www.planetary.brown.edu/relabdata/data/' + sample_id.split('-')[1].lower() + '/' + sample_id.split('-')[0].lower() + '/' + spectrum_id.lower() + '.txt'
				gaffey_url_dic[unique_id] = url
		return gaffey_url_dic
		



	'''
	PARAMS:
		list_ : list of sample ids for each met type (other, mars, moon)
		met: indicates which met type this list belongs to
	RETURNS:
		list of all unprocesed filenames for meteorite spectra 
	'''
	@staticmethod
	def get_gaffey_unprocessed_filenames(list_):
		newl= []
		for elem in list_:
			name = elem.split('__')[1] + '-' + elem.split('__')[0]
			newelem = 'spectra_data_unprocessed_gaffey/' + str(name) + '.txt'
			newl.append(newelem)
		return newl

















