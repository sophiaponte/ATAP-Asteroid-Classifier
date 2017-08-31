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
from random import randint



'''want this: given some ASTEROID TYPE, what is the probability that you get a certain MET TYPE
	
	WORKS! THIS VERSION WORKS

	P(MET TYPE | ASTEROID TYPE) = P(ASTEROID TYPE | MET TYPE) * P(MET TYPE) / P(ASTEROID TYPE)

	#want a dic of each type and their counts
	#want a dic of each class and their counts

'''

class Bayes_Name:


	training_data = [] #list of tuples (Asteroidtype, mettype)
	test_data = []
	type_count_dic = {}
	class_count_dic = {}


	'''
	PARAMS: 
		filename : file to load data from (either test or training file)
	RETURNS: 
		data: list of tuples that contain the training or test data. Each tuple is (asteroid_type, meteorite_type)
	'''
	@staticmethod
	def load_data(filename):
		data = []
		with open(filename, 'r') as f:
			for line in f:
				class_ = line.rstrip().split('__')[0]
				type_ = line.rstrip().split('__')[1]
				data.append((class_,type_))
		return data

	'''
	PARAMS:
		type_or_class: indicates whether this funciton should make a type cound dic or a class count dic
	RETURNS:
		dictionary either mapping type count or class count. each class or type is a key, and the number of times it appears in the 
		training set is the value
	'''
	@staticmethod
	def get_count_dics(type_or_class):
		if type_or_class == 'types':
			index = 1
		if type_or_class == 'classes':
			index = 0

		dic = {}
		for tup in Bayes_Name.training_data:
			curr = tup[index]
			if curr not in dic.keys():
				dic[curr] = 1
			elif curr in dic.keys():
				val = dic[curr]
				val += 1
				dic[curr] = val
		return dic


	'''
	PARAMS:
		type_ : type of meteorite
		class_ : type of asteroid 
		type_or_class : indicates whether posterior probability should be P(type | class) or P(class | type)
	RETURNS: 
		posterior probability (either P(type | class) or P(class | type) ) for the type and class in the params
	'''
	@staticmethod
	def get_posterior_probability_for(type_, class_, type_to_class):
		total_num = len(Bayes_Name.training_data)
		probability = 0
		count = 0
		for tup in Bayes_Name.training_data:
			if tup[0] == class_ and tup[1] == type_:
				count +=1

		if type_to_class:
			likelihood = count/float(Bayes_Name.class_count_dic[class_])
			class_prior = Bayes_Name.class_count_dic[class_]/float(total_num)
			predictor_prior = Bayes_Name.type_count_dic[type_]/float(total_num)
			probability = likelihood*class_prior/predictor_prior
		else:		
			likelihood = count/float(Bayes_Name.type_count_dic[type_])
			class_prior = Bayes_Name.type_count_dic[type_]/float(total_num)
			predictor_prior = Bayes_Name.class_count_dic[class_]/float(total_num)
			probability = likelihood*class_prior/predictor_prior

		return probability

	'''
	PARAMS : 
		class_ : find the highest associated probability of type for the given class
		type_to_class : indicates whether finding probability of type given class or probability of class given type
	RETURNS : 
		type with the highest probability for the given class
	'''
	@staticmethod
	def find_highest_probability_for_class(class_, type_to_class):
		max_prob = 0
		max_type = ""
		total_sum = 0
		for type_ in Bayes_Name.type_count_dic.keys():
			probability = Bayes_Name.get_posterior_probability_for(type_, class_, type_to_class)
			if probability >= max_prob:
				max_prob = probability
				max_type = type_
			total_sum += probability
		return max_type

	'''
	PARAMS : 
		type : find the highest associated probability of class for the given type
		type_to_class : indicates whether finding probability of type given class or probability of class given type
	RETURNS : 
		class with the highest probability for the given type
	'''
	@staticmethod
	def find_highest_probability_for_type(type_, type_to_class):
		max_prob = 0
		max_class = ""
		total_sum = 0
		for class_ in Bayes_Name.class_count_dic.keys():
			probability = Bayes_Name.get_posterior_probability_for(type_, class_, type_to_class)
			if probability >= max_prob:
				max_prob = probability
				max_class = class_
			total_sum += probability
		return max_class


	'''
	PARAMS : 
		type_to_class : indicates whether finding probability of type given class or probability of class given type
	this function finds the highest matching class for each type, or the highest matching type for each class depending on the parameter
	type_to_class
	'''
	@staticmethod
	def get_highest_matches(type_to_class):
		if type_to_class:
			for type_ in Bayes_Name.type_count_dic.keys():
				Bayes_Name.find_highest_probability_for_type(type_, type_to_class)
		else:
			for class_ in Bayes_Name.class_count_dic.keys():
				Bayes_Name.find_highest_probability_for_class(class_, type_to_class)

	'''
	this function tests the algorithm against the test set. It counts the number of times the algorithm predicts the correct
	meteorite type for the given class
	'''
	@staticmethod
	def test():
		match_count = 0
		total_count = 0
		for tup in Bayes_Name.test_data:
			
			class_ = tup[0]
			predicted_type = Bayes_Name.find_highest_probability_for_class(class_, False)
			if predicted_type == tup[1]:
				match_count +=1
			total_count +=1

		#print match_count/float(total_count)
		return match_count/float(total_count)



	'''
	PARAMS: 
		weighted : whether or not to weight the meteorites with more than one class
		level : level of complexity 
	runs algorithm on robust file once. picks a random number to select which lines will 
	be in the test file and which will be training. This way we get different test sets every time we test.
	'''
	@staticmethod
	def run_algo_robust(weighted, level):
		robust_file = ""
		if weighted and level == 'complex_prime_type':
			robust_file = 'robust_files/naive_bayes_name_complex_prime_type_weighted.txt'
		elif weighted and level == 'complex_type':
			robust_file = 'robust_files/naive_bayes_name_complex_type_weighted.txt'
		elif not weighted and level == 'complex_type':
			robust_file = 'robust_files/naive_bayes_name_complex_type.txt'
		elif not weighted and level == 'complex_prime_type':
			robust_file = 'robust_files/naive_bayes_name_complex_prime_type.txt'

		interval = randint(18,22)
		print interval

		Bayes_Name.training_data = Bayes_Name.load_training_data_robust(robust_file,interval)
		Bayes_Name.test_data = Bayes_Name.load_test_data_robust(robust_file,interval)
		Bayes_Name.class_count_dic = Bayes_Name.get_count_dics('classes')
		Bayes_Name.type_count_dic = Bayes_Name.get_count_dics('types')
		accuracy = Bayes_Name.test()
		return accuracy

	'''
	PARAMS: 
		filename : name of file to load test and training data from
		interval : determines which lines in file become training set and which lines become test set
		slope : wehether or not slope is included
	RETURNS: 
		list of tuples containing training data 
	'''
	@staticmethod
	def load_training_data_robust(filename, interval):
		counter = 0
		with open(filename, 'r') as f:

			data = []
			for line in f:
				class_ = line.rstrip().split('__')[0]
				type_ = line.rstrip().split('__')[1]
				if counter % interval != 0:
					data.append((class_,type_))
				counter +=1

		return data

	'''
	PARAMS: 
		filename : name of file to load test and training data from
		interval : determines which lines in file become training set and which lines become test set
		slope : wehether or not slope is included
	RETURNS: 
		list of tuples containing test data 
	'''
	@staticmethod
	def load_test_data_robust(filename, interval):
		counter = 0
		with open(filename, 'r') as f:

			data = []
			for line in f:
				class_ = line.rstrip().split('__')[0]
				type_ = line.rstrip().split('__')[1]
				if counter % interval == 0:
					data.append((class_,type_))
				counter +=1

		return data


	'''MAIN METHOD''
	for robustness: 
	PARAMS: 
		num : number of times to test robustness
		weighted: whether the number of votes per meteroite is weighted
		level : whether the meteorite type is class or clan
	PRINTS: The total accuracy 
	'''
	@staticmethod
	def test_robustness(num, weighted, level):
		accuracy = 0
		for i in range(0,num):
			accuracy += Bayes_Name.run_algo_robust(weighted, level)
		print accuracy/float(num)


	'''
	MAIN METHOD RANDOM:
	this is an old implementation -- does not test for robustness. this function just tests on the random training and test files
	'''
	@staticmethod
	def test_random(weighted, level):
		training_filename = ""
		if weighted and level == 'complex_prime_type':
			training_filename = 'robust_files/naive_bayes_name_complex_prime_type_training_weighted.txt'
		elif weighted and level == 'complex_type':
			training_filename = 'robust_files/naive_bayes_name_complex_type_training_weighted.txt'
		elif not weighted and level == 'complex_type':
			training_filename = 'robust_files/naive_bayes_name_complex_type_training.txt'
		elif not weighted and level == 'complex_prime_type':
			training_filename = 'robust_files/naive_bayes_name_complex_prime_type_training.txt'

		test_filename = ""
		if weighted and level == 'complex_prime_type':
			test_filename = 'robust_files/naive_bayes_name_complex_prime_type_test_weighted.txt'
		elif weighted and level == 'complex_type':
			test_filename = 'robust_files/naive_bayes_name_complex_type_test_weighted.txt'
		elif not weighted and level == 'complex_type':
			test_filename = 'robust_files/naive_bayes_name_complex_type_test.txt'
		elif not weighted and level == 'complex_prime_type':
			test_filename = 'robust_files/naive_bayes_name_complex_prime_type_test.txt'

		Bayes_Name.training_data = Bayes_Name.load_data(training_filename) # ~ 59% accurate
		Bayes_Name.test_data = Bayes_Name.load_data(test_filename)

		Bayes_Name.type_count_dic = Bayes_Name.get_count_dics('types')
		Bayes_Name.class_count_dic = Bayes_Name.get_count_dics('classes')
		type_to_class = False
		Bayes_Name.test()



