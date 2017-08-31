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

import re
import csv

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from sklearn.neighbors import KernelDensity
from scipy.stats import norm

from scipy.stats.kde import gaussian_kde
from numpy import linspace

from random import randint




'''want this: given some ASTEROID TYPE, what is the probability that you get a certain MET TYPE
	

	P(MET TYPE | instance of PCAS) = P(instance of PCAS | MET TYPE) * P(MET TYPE) / P(instance of PCAS)

	P(instance | Met type ) = P(pca1 | met type)*P(pca2 | met type) ...

	P(PCAx | Met type) = get_independent_probability()



'''

class Bayes_Pca:

	training_data = []
	test_data = []
	type_count_dic = {}

	'''
	PARAMS : 
		filename : filename for this training or test data
	RETURNS
		list of tuples containing either training or test data. Each tuple is a list of pca components and a met type
	'''
	@staticmethod
	def load_data(filename):
		index = 0
		if slope:
			index = 6
		else:
			index = 5
		data = []
		with open(filename, 'r') as f:
			for line in f:
				pca = line.rstrip().split('__')[:index]
				type_ = line.rstrip().split('__')[index]
				data.append((pca,type_))
		return data

	'''
	creates type count dic. Each type in the set is a key, each value is the number of times this met type appears
	'''
	@staticmethod
	def get_type_count_dic():
		index = 1
		dic = {}
		for tup in Bayes_Pca.training_data:
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
		met_type : meteorite type
		pca_arr : list of pca components we are assessing probability of, given a certain met type
		slope : whether slope is on or off
	RETURNS: probability of getting this pca list given the meteorite type

	'''
	@staticmethod
	def find_probability_of(met_type, pca_arr, slope):
		p_of_met_type = Bayes_Pca.type_count_dic[met_type]/float(len(Bayes_Pca.training_data))


		p_pca1 = Bayes_Pca.get_independent_probability(pca_arr[0], met_type, 0)
		p_pca2 = Bayes_Pca.get_independent_probability(pca_arr[1], met_type, 1)
		p_pca3 = Bayes_Pca.get_independent_probability(pca_arr[2], met_type, 2)
		p_pca4 = Bayes_Pca.get_independent_probability(pca_arr[3], met_type, 3)
		p_pca5 = Bayes_Pca.get_independent_probability(pca_arr[4], met_type, 4)

		p_slope = 1
		if(slope):
			p_slope = Bayes_Pca.get_independent_probability(pca_arr[5], met_type, 5)
		

		p_likelihood = p_pca5*p_pca4*p_pca3*p_pca2*p_pca1*p_slope

		p_predictor_prior = Bayes_Pca.get_predictor_prior(pca_arr, slope)

		if float(p_likelihood) == 0.0 and float(p_predictor_prior) == 0.0:
			return 0.0

		probability = p_likelihood * float(p_of_met_type) /float(p_predictor_prior)

		return probability


	#number of instances of pc type in total number of met types

	'''
		say were looking at pca1
		.02 -- > met1
		.02 --> met 2
		.4 --> met 2
		.05 ---> met5
		.032 --> met1
		.2353 --> met 1
		.0634 --> met 2

		we want probability that pca1 is .4 given met 1
		so out of all the met ones, we have pca = .02, pca = .032, pca = .235
 
	'''
	

	'''
	PARAMS:
		pca_arr : instance of prior (pc1, pc2, pc3, pc4, pc5)
		slope:	wehether slope is true or not
	RETURNS:
		probability of observing this prior. Computes kde estimated probability of each pc indepenedently and then multiplies them
	'''
	#probability of observing instance (pc1, pc2, pc3, pc4, pc5)
	@staticmethod
	def get_predictor_prior(pca_arr, slope):
		
		probability = 1.0
		for i in range(0,5): #0 - 4 is pca, 5 is slope
			pca_list = Bayes_Pca.get_pcas_for_index(i)
			probability *= Bayes_Pca.get_kde_probability_estimate(pca_arr[i], pca_list)
		return probability

	'''
	PARAMS:
		pca: pca component we are finding probability of 
		pca_list : list of points that will make up the kde 
	*integrates kde formed out of pca list and integrates on box around the value of pca
	RETURNS:
		proability for this new pca giving the kde from the pca_list
	'''
	@staticmethod
	def get_kde_probability_estimate(pca, pca_list):
		if len(pca_list) <=1:
			return 0
		if len(set(pca_list)) == 1:
			return 0
		kde = gaussian_kde( pca_list ) #--------------------------------------------gaussian_kde() is from scipy.stats
		high = float(pca) - .01
		low = float(pca) + .01

		probability =  kde.integrate_box_1d(high, low)

		if probability <= .0001:
			probability = 0
		return probability


	'''
	PARAMS:
		index : index of pca 
	RETURNS:
		list of pca components of this index
	'''
	@staticmethod
	def get_pcas_for_index(index):
		list_ = []
		for tup in Bayes_Pca.training_data:
			list_.append(float(tup[0][index]))
		return list_


	'''
	finidng p(pcax | type)
	PARAMS:
		pca : we want to find the probability for this pca component 
		type_ : the types for which we are finding the independent probability of  
		index : index of pca component 
	RETURNS : independent probability for this pca component
	'''
	@staticmethod
	def get_independent_probability(pca, type_, index):
		pca_arr = [] #all pca's for given index that are in this met type
		for tup in Bayes_Pca.training_data:
			if tup[1] == type_:
				pca_arr.append(float(tup[0][index]))

		probability = Bayes_Pca.get_kde_probability_estimate(pca, pca_arr)

		return probability
	
		# plt.plot(x,kde(x),'r',label="KDE estimation",color="blue")
		# plt.hist(pca_arr,normed=1,color="cyan",alpha=.8)
		#plt.show()

	'''
	PARAMS: 
		pca_arr: array of pca components for the asteroid we are trying to find a match for
		slope : whether or not we are including slope
	RETURNS: 
		type that has the highest matching probability to this pca_arr
	'''
	@staticmethod
	def get_highest_probability_for(pca_arr, slope):
		max_prob = 0
		max_type = ""
		for type_ in Bayes_Pca.type_count_dic.keys():
			prob = Bayes_Pca.find_probability_of(type_, pca_arr, slope)
			if prob > max_prob:
				max_prob = prob
				max_type = type_
		return max_type 

	'''
	PARAMS : slope
	RETURNS : accuracy for the naive bayes pca algorithm performs on this test set
	This funciton runs the test on the algorithm to see wehther it finds accurate matches
	'''
	@staticmethod
	def test(slope):
		counter = 0
		total = 0
		for tup in Bayes_Pca.test_data:
			pca_arr = tup[0]
			type_ = Bayes_Pca.get_highest_probability_for(pca_arr, slope)
			if type_ == tup[1]:
				#print 'match'
				counter +=1
			#else:
				#print 'not match'
			total += 1
		accuracy = counter/float(total)
		print accuracy
		return accuracy



	'''
	PARAMS: 
		slope : whether or not to include slope
		level : level of complexity 
	runs algorithm on robust file once. picks a random number to select which lines will 
	be in the test file and which will be training. This way we get different test sets every time we test.
	'''
	@staticmethod
	def run_algo_robust(slope, level):
		robust_file = ""
		if slope and level == 'complex_prime_type':
			robust_file = 'robust_files/naive_bayes_pca_complex_prime_type_slope.txt'
		elif slope and level == 'complex_type':
			robust_file = 'robust_files/naive_bayes_pca_complex_type_slope.txt'
		elif not slope and level == 'complex_type':
			robust_file = 'robust_files/naive_bayes_pca_complex_type.txt'
		elif not slope and level == 'complex_prime_type':
			robust_file = 'robust_files/naive_bayes_pca_complex_prime_type.txt'

		interval = randint(17,20)
		print interval

		Bayes_Pca.training_data = Bayes_Pca.load_training_data_robust(robust_file,interval, slope)
		Bayes_Pca.test_data = Bayes_Pca.load_test_data_robust(robust_file,interval, slope)

		Bayes_Pca.type_count_dic = Bayes_Pca.get_type_count_dic()
		acccuracy = Bayes_Pca.test(slope)
		return acccuracy

	'''
	PARAMS: 
		filename : name of file to load test and training data from
		interval : determines which lines in file become training set and which lines become test set
		slope : wehether or not slope is included
	RETURNS: 
		list of tuples containing training data 
	'''
	@staticmethod
	def load_training_data_robust(filename, interval, slope):
		counter = 0
		with open(filename, 'r') as f:
			index = 0
			if slope:
				index = 6
			else:
				index = 5

			data = []
			for line in f:
				pca = line.rstrip().split('__')[:index]
		 		type_ = line.rstrip().split('__')[index]
				if counter % interval != 0:
					data.append((pca,type_))
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
	def load_test_data_robust(filename, interval, slope):
		counter = 0
		with open(filename, 'r') as f:
			index = 0
			if slope:
				index = 6
			else:
				index = 5
			data = []
			for line in f:
				pca = line.rstrip().split('__')[:index]
		 		type_ = line.rstrip().split('__')[index]
				if counter % interval == 0:
					data.append((pca,type_))
				counter +=1
		return data


	'''
	MAIN METHOD
	for robust testing
	params: 
		num : number of times to test for robustness 
		slope : whether slope is included as a feature
		level: meteorite type complexity level (class or clan)
	PRINTS: accuracy for robustness testing
	'''
	@staticmethod
	def test_robustness(num, slope, level):
		accuracy = 0
		for i in range(0,num):
			accuracy += Bayes_Pca.run_algo_robust(slope, level)
		print accuracy/float(num)



		




