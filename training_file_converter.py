
import sys
import math
import xlrd
import json
import ast
import os
#import xlsxwriter
import xlwt
import matplotlib.pyplot as plt
import numpy as np
from processed_data_load import *



class Trainer:


	'''
	ROBUST MAIN METHOD
	Creates robust training files (so that they can be run on and tested multiple times)
	PARAMS:
		meteorites : list of meteorite objects
	'''
	@staticmethod
	def create_robust_files(meteorites):


		Trainer.create_robust_naive_bayes_pca( meteorites, 'complex_type', False)
		Trainer.create_robust_naive_bayes_pca( meteorites, 'complex_prime_type', False)
		Trainer.create_robust_naive_bayes_pca( meteorites, 'complex_type', True)
		Trainer.create_robust_naive_bayes_pca( meteorites, 'complex_prime_type', True)

		Trainer.create_robust_naive_bayes_name(meteorites,'complex_type', True)
		Trainer.create_robust_naive_bayes_name(meteorites, 'complex_type', False)
		Trainer.create_robust_naive_bayes_name(meteorites, 'complex_prime_type', True)
		Trainer.create_robust_naive_bayes_name(meteorites, 'complex_prime_type', False)


	'''
	PARAMS:
		meteorites: list of meteorite objects
		met_complexity: whether meteorites are clan, or class level 
		slope: whether we want to include slope in the training/test file
	creates a robust test and training file for naive bayes pca space
	'''
	@staticmethod
	def create_robust_naive_bayes_pca(meteorites, met_complexity, slope):
		filename = ""
		if slope == True:
			filename = 'robust_files/naive_bayes_pca_' + met_complexity + '_slope.txt' 
		else: 
			filename = 'robust_files/naive_bayes_pca_' + met_complexity + '.txt' 

		with  open(filename, 'w') as f:
			pca_arr = []
			subtype = ""
			for meteorite in meteorites:
				if met_complexity == 'relab_type':
					subtype = meteorite.subtype
					if subtype == 'None':
						subtype = meteorite.types[0].split('__')[2]
				elif met_complexity == 'complex_type':
					subtype = meteorite.complex_type
				elif met_complexity == 'complex_prime_type':
					subtype = meteorite.complex_prime_type
				pca_arr = meteorite.pca_components
				if slope and met_complexity == 'complex_type':
					pca_arr.append(meteorite.slope)
				Trainer.write_pca_line_to_file(f, pca_arr, subtype)


	'''
	PARAMS:
		meteorites: list of meteorite objects
		met_complexity: whether meteorites are clan, or class level 
		weighted: whether we want to include weighting in the training/test file
	creates a robust test and training file for naive bayes name space
	'''
	@staticmethod
	def create_robust_naive_bayes_name(meteorites, met_complexity, weighted):
		filename = ""
		if weighted == True:
			filename = 'robust_files/naive_bayes_name_' + met_complexity + '_weighted.txt' 
		else: 
			filename = 'robust_files/naive_bayes_name_' + met_complexity + '.txt' 
		with open(filename, 'w') as f:
			subtype = ""
			classes = []
			for meteorite in meteorites:
				classes = meteorite.classes
				if met_complexity == 'relab_type':
					subtype = meteorite.subtype
					if subtype == 'None':
						subtype = meteorite.types[0].split('__')[2]
				elif met_complexity == 'complex_type':
					subtype = meteorite.complex_type
				elif met_complexity == 'complex_prime_type':
					subtype = meteorite.complex_prime_type
				Trainer.write_class_line_to_file(f, classes, subtype, weighted)


	''' 
	MAIN METHOD : creates all random training and test files for meteorites. 
	'''
	@staticmethod
	def create_all_files_random(meteorites):

		weighted_pca = False
		weighted = True

		#pca space training files with weighting off and slope off for complex and complex prime met classes
		Trainer.create_training_and_test_files_random(meteorites, 'naive_bayes_pca', 'complex_prime_type', False, weighted_pca)
		Trainer.create_training_and_test_files_random(meteorites, 'naive_bayes_pca', 'complex_type', False, weighted_pca)

		#pca space training files with weighting off and slope on for complex and complex prime met classes
		Trainer.create_training_and_test_files_random(meteorites, 'naive_bayes_pca', 'complex_type', True, weighted_pca)
		Trainer.create_training_and_test_files_random(meteorites, 'naive_bayes_pca', 'complex_prime_type', True, weighted_pca)

		#name space training files with weighting for complex and complex prime met classes
		Trainer.create_training_and_test_files_random(meteorites, 'naive_bayes_name', 'complex_type', False, weighted)
		Trainer.create_training_and_test_files_random(meteorites, 'naive_bayes_name', 'complex_prime_type', False, weighted)


	'''
	PARAMS: 
		meteorites : list of meteorites
		algorithm: indicator for whether these files are going to be used for  pca space or name space classifier
		slope: boolean indicating whether slope is a feature in the training/test sets
		met_complexity: indicates whether we are using 'clan- level' or 'class-level' met taxonomy
		weighted: boolean indicating whether the meteorites will be weighthed on account of the number of asteroid classes 
				  (only valid for name-space classifier)
	This function creates the training and test files by taking the first one out of every NUM of meteorites to be in the test file. 
	This helps to get a more diverse spread of meteorites for the training and test data than simply selecting the last few in the list
	'''
	@staticmethod
	def create_training_and_test_files_random(meteorites, algorithm, met_complexity, slope, weighted):

		if algorithm == 'naive_bayes_name':
			Trainer.create_training_or_test_file_random(meteorites, algorithm, 'training_file', met_complexity, slope, weighted)
			Trainer.create_training_or_test_file_random(meteorites, algorithm, 'test_file', met_complexity, slope, weighted)
		elif algorithm == 'naive_bayes_pca':
			Trainer.create_training_or_test_file_random(meteorites, algorithm, 'training_file', met_complexity, slope, weighted)
			Trainer.create_training_or_test_file_random(meteorites, algorithm, 'test_file', met_complexity, slope, weighted)


	'''
	PARAMS: 
		meteorites : list of meteorites
		algorithm: indicator for whether these files are going to be used for  pca space or name space classifier
		slope: boolean indicating whether slope is a feature in the training/test sets
		file_type : indicates whether or not this is a training or test file
		met_complexity: indicates whether we are using 'clan- level' or 'class-level' met taxonomy
		weighted: boolean indicating whether the meteorites will be weighthed on account of the number of asteroid classes 
				  (only valid for name-space classifier)
	This function defines the filename for the training or test file. Then if slope == true or weighted == true this function adds an 
	indicator to the filename to express that these files include slope(for pca space trainging/test sets) and/or whether they are weighted 
	(for name space training/test sets). 
	test_range and training_range define which mets in the list belong to the training /test sets. The mets in the test set are one out of every 
	NUM
	'''
	@staticmethod
	def create_training_or_test_file_random(meteorites, algorithm, file_type, met_complexity, slope, weighted):

		filename = ""
		if file_type == 'training_file' and algorithm == 'naive_bayes_name':
			filename = 'training_files_random/' + algorithm  + '_' + met_complexity + '_training.txt'
		if file_type == 'test_file' and algorithm == 'naive_bayes_name':
			filename = 'test_files_random/' + algorithm  + '_' + met_complexity + '_test.txt'
		if file_type == 'training_file' and algorithm == 'naive_bayes_pca':
			filename = 'training_files_random/' + algorithm  + '_' + met_complexity + '_training.txt'
		if file_type == 'test_file' and algorithm == 'naive_bayes_pca':
			filename = 'test_files_random/' + algorithm + '_' + met_complexity + '_test.txt'

		if slope:
			filename = filename.split('.')[0] + '_slope.txt'

		if weighted:
			filename = filename.split('.')[0] + '_weighted.txt'

		total_range = range(0,len(meteorites))
		test_range = range(0,len(meteorites),19)
		training_range = [index for index in total_range if index not in test_range]

		if(file_type == 'training_file'):
			Trainer.create_file_random(meteorites, algorithm, filename, training_range, slope, met_complexity, weighted)
		elif file_type == 'test_file':
			Trainer.create_file_random(meteorites, algorithm, filename, test_range, slope, met_complexity, weighted)



	'''
	PARAMS: 
		meteorites : list of meteorites
		algorithm: indicator for whether these files are going to be used for  pca space or name space classifier
		filename : the filename of the training or test file
		training_or_test_range : these indicate whether these are the set of training meteorites or test meteorites. 
		slope: boolean indicating whether slope is a feature in the training/test sets
		met_complexity: indicates whether we are using 'clan- level' or 'class-level' met taxonomy
		weighted: boolean indicating whether the meteorites will be weighthed on account of the number of asteroid classes 
				  (only valid for name-space classifier)
	Creates the actual training and/or test file, based on whether algorithm = 'naive_bayes_pca' or 'naive_bayes_name'. 
	'''
	@staticmethod
	def create_file_random(meteorites, algorithm, filename, training_or_test_range, slope, met_complexity, weighted):
		if algorithm == 'naive_bayes_pca':
			subtype = ""
			pca_arr = []
			with  open(filename, 'w') as f:
				for index in training_or_test_range:
					meteorite = meteorites[index]
					if met_complexity == 'relab_type':
						subtype = meteorite.subtype
						if subtype == 'None':
							subtype = meteorite.types[0].split('__')[2]
					elif met_complexity == 'complex_type':
						subtype = meteorite.complex_type
					elif met_complexity == 'complex_prime_type':
						subtype = meteorite.complex_prime_type
					pca_arr = meteorite.pca_components
					if slope and met_complexity == 'complex_type':
						pca_arr.append(meteorite.slope)
					Trainer.write_pca_line_to_file(f, pca_arr, subtype)

		elif algorithm == 'naive_bayes_name':
			with open(filename, 'w') as f:
				subtype = ""
				classes = []
				for index in training_or_test_range:
					meteorite = meteorites[index]
					classes = meteorite.classes
					if met_complexity == 'relab_type':
						subtype = meteorite.subtype
						if subtype == 'None':
							subtype = meteorite.types[0].split('__')[2]
					elif met_complexity == 'complex_type':
						subtype = meteorite.complex_type
					elif met_complexity == 'complex_prime_type':
						subtype = meteorite.complex_prime_type
					Trainer.write_class_line_to_file(f, classes, subtype, weighted)


	'''
	PARAMS
		f : file to write line to
		arr: list of classes associated with met for this line
		subtype : subtype associated with met for this line
		weighted: boolean indicating whether the meteorites will be weighthed on account of the number of asteroid classes 
				  (only valid for name-space classifier)
	writes a line to the training or test file for name space naive bayes classifier. The boolean weighted indicates
	whether or not we are 'counting votes' for meteorites that have up to 3 asteroid taxonomic classes associated with them. 
	If weighted is on, this function gives mets with one class 6 counts, mets with 2 classes three counts each, and mets with 3 classes
	2 counts each. 
	'''
	@staticmethod
	def write_class_line_to_file(f, arr, subtype, weighted):
		line = ""
		if weighted:
			if len(arr) == 1:
				for i in range(0,6):
					f.write(arr[0] + '__' + subtype + '\n')
			elif len(arr) == 2:
				for elem in arr:
					for i in range(0,3):
						f.write(elem + '__' + subtype + '\n')
			elif len(arr) == 3 :
				for elem in arr:
					for i in range(0,2):
						f.write(elem + '__' + subtype + '\n')
		else:				
			for elem in arr:
				f.write(elem + '__' + subtype + '\n')



	'''
	PARAMS
		f : file to write line to
		arr: list of pca components (and possibly slope) associated with met for this line
		subtype : subtype associated with met for this line
	writes a line to the training or test file for pca space naive bayes classifier. 
	'''
	@staticmethod
	def write_pca_line_to_file(f, arr, subtype):
		line = ""
		for elem in arr:
			line += elem + '__'
		line += subtype + '\n'
		f.write(line)





    #############################################################################################################################################
    #############################################################################################################################################
    ###################################################### PREV IMPLEMENTATION BELOW ############################################################
    #############################################################################################################################################





	@staticmethod
	def create_training_and_test_files(meteorites, algorithm, training_num, ast_complexity, met_complexity, slope):
		num_mets_train = int(len(meteorites)*training_num)
		num_mets_test = len(meteorites) - num_mets_train
		if algorithm == 'naive_bayes_name':
			Trainer.create_training_or_test_file(meteorites, algorithm, 0, num_mets_train, ast_complexity, met_complexity, slope)
			Trainer.create_training_or_test_file(meteorites, algorithm, num_mets_train, len(meteorites), ast_complexity, met_complexity, slope)
		elif algorithm == 'naive_bayes_pca':
			Trainer.create_training_or_test_file(meteorites, algorithm, 0, num_mets_train, ast_complexity, met_complexity, slope)
			Trainer.create_training_or_test_file(meteorites, algorithm, num_mets_train, len(meteorites), ast_complexity, met_complexity, slope)

	@staticmethod
	def create_training_or_test_file(meteorites, algorithm, start, end, ast_complexity, met_complexity, slope):
		filename = ""
		if start == 0:
			filename = 'training_files/' + algorithm + '_' + ast_complexity + '_' + met_complexity + '_training.txt'
		else:
			filename = 'test_files/' + algorithm + '_' + ast_complexity + '_' + met_complexity + '_test.txt'

		classes = []
		#subtype = ""
		if algorithm == 'naive_bayes_name':
			pca = False
			with open(filename, 'w') as f:
				subtype = ""
				pca_arr = []

				for i in range(start,end):
					meteorite = meteorites[i]
					if ast_complexity == 'demeo_class':
						classes = meteorite.classes
					elif ast_complexity == 'complex_class':
						classes = meteorite.complex_classes
					if met_complexity == 'relab_type':
						subtype = meteorite.subtype
						if subtype == 'None':
							subtype = meteorite.types[0].split('__')[2]
					elif met_complexity == 'complex_type':
						subtype = meteorite.complex_type
					elif met_complexity == 'complex_prime_type':
						subtype = meteorite.complex_prime_type
					Trainer.write_class_line_to_file(f, classes, subtype, weighted)
		elif algorithm == 'naive_bayes_pca':
			if slope:
				filename = filename.split('.')[0] + '_slope.txt'
			pca = True
			with open(filename, 'w') as f:
				subtype = ""
				pca_arr = []

				for i in range(start, end):
					meteorite = meteorites[i]
					if met_complexity == 'relab_type':
						subtype = meteorite.subtype
						if subtype == 'None':
							subtype = meteorite.types[0].split('__')[2]
					elif met_complexity == 'complex_type':
						subtype = meteorite.complex_type
					elif met_complexity == 'complex_prime_type':
						subtype = meteorite.complex_prime_type
					pca_arr = meteorite.pca_components
					if slope and met_complexity == 'complex_type':
						pca_arr.append(meteorite.slope)
					Trainer.write_pca_line_to_file(f, pca_arr, subtype)


	@staticmethod
	def create_all_files(meteorites):

		create_training_and_test_files(all_meteorites, 'naive_bayes_pca', .95, 'demeo_class', 'complex_prime_type', False)
		create_training_and_test_files(all_meteorites, 'naive_bayes_pca', .95, 'demeo_class', 'complex_type', False)

		create_training_and_test_files(all_meteorites, 'naive_bayes_pca', .95, 'demeo_class', 'complex_type', True)
		create_training_and_test_files(all_meteorites, 'naive_bayes_pca', .95, 'demeo_class', 'complex_prime_type', True)




