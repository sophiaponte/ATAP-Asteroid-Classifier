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

class Email_getter:

	'''
	MAIN METHOD
	PARAMS:
		mars_met : "Mars_Met"
		other_met : "Other_Met"
		moon_met : "Moon_Met"
	connects to account for mars met files, moon met files, other met files
	'''
	@staticmethod
	def get_all_email_data(mars_met, other_met, moon_met):
		Email_getter.connect_to_account("send", mars_met) 
		Email_getter.connect_to_account("send", moon_met)
		Email_getter.connect_to_account("send", other_met)

	'''
	gets email data for gaffey files, saves gaffey files to 'spectra_data_processed_new' folder
	'''
	@staticmethod
	def get_all_email_data_gaffey():
		Email_getter.connect_to_account("send", "Gaffey")

	'''
	PARAMS:
		function : whether to send emails and get list of processed files, or to simply get a list of processed filenames
		mbox : inbox
	RETURNS:
		list of files that have been processed

	This program handles accessing the data from the emails sent by the Bus-Demeo website. 
	in connect_to_account() this program opens a connection with the gmail account 
	m.atap.data@gmail.com. get_all_emails takes the email object and extracts the 
	subject name and text from the body of the email. This program then exports all the 
	emails to spectra_data_processed. Currently only running on the gaffey data. 

	'''
	@staticmethod
	def connect_to_account(function, mbox):
		list_of_files = []
		M = imaplib.IMAP4_SSL('imap.gmail.com')
		user = 'm.atap.data@gmail.com'
		_pass = 'meteorite'
		rv, data = M.login(user, _pass)
		rv, mailboxes = M.list()
		if rv == 'OK':
			print "Mailboxes:"
			print mailboxes
		rv, data = M.select(mbox)# --------------------- only select inbox
		if rv == 'OK':
			print "Processing mailbox...\n"
			if function == "send":
				Email_getter.get_all_emails(M, mbox)# ---------------------------- extracts data from emails and saves it to computer
			if function == "list":
				list_of_files = Email_getter.get_list_of_processed_files(M)
			else:
				print "ERROR: please select a function"
			M.close()
		else:
			print "ERROR: Unable to open mailbox ", rv

		M.logout()
		return list_of_files


	'''
	PARAMS: 
		M : Mail object
		mbox: moon, mars, or other
	extracts email and useful information into email_body_text and exports it to file_to_export
	'''
	@staticmethod
	def get_all_emails(M, mbox):
		print "failed!!!"
		typ, data = M.search(None, 'ALL')
		for num in data[0].split():
			typ, data = M.fetch(num, '(RFC822)')
			#print 'Message %s\n%s\n' % (num, data[0][1])
			raw_email = data[0][1]
			email_message = email.message_from_string(raw_email)
			subject = email_message['Subject']
			filename = subject.split(' ')[-1].replace('/','-')
			file_to_export = ""
			if mbox == "Gaffey":
				file_to_export = 'spectra_data_processed_new/' + filename + '.txt'
			else:
				file_to_export = 'spectra_data_processed_all/' + mbox + '/' + filename + '.txt'
			email_body_text = ""
			if email_message.is_multipart():
				for payload in email_message.get_payload():
					email_body_text = payload.get_payload()
			else:
				email_body_text = email_message.get_payload()
   			time.sleep(2)			
   			Email_getter.export_string(email_body_text, file_to_export)
			print file_to_export + " .....working......"


	'''
	PARAMS: 
		M : mailbox object
	RETURNS: 
		list of processed filenames
	gets a list of the demeo classifier processed filenames from the emails
	'''

	@staticmethod
	def get_list_of_processed_files(M):
		list_of_files = []
		typ, data = M.search(None, 'ALL')
		for num in data[0].split():
			typ, data = M.fetch(num, '(RFC822)')
			#print 'Message %s\n%s\n' % (num, data[0][1])
			raw_email = data[0][1]
			email_message = email.message_from_string(raw_email)
			subject = email_message['Subject']
			filename = subject.split(' ')[-1].replace('/','-')
			file_to_export = 'spectra_data_processed_new/' + filename + '.txt'
			list_of_files.append(file_to_export)
			print "appending: " + file_to_export
		Email_getter.export_string(str(list_of_files), "temp_export_file.txt")	
		return list_of_files


	'''
	PARAMS: 
		data : data to export
		file_to_export: filename
	'''
	@staticmethod
	def export_string(data, file_to_export):
		with open(file_to_export, "w") as text_file:
			text_file.write(data)

	'''
	PARAMS 
		met: met type
	RETURNS
		list of spectra_data_processed filenames -- obtained from OS as opposed to email server
	'''
	@staticmethod
	def get_processed_filenames(met):
		files = []
		if met == "Gaffey":
			directory = 'spectra_data_processed_new'
			for filename in os.listdir(directory):
				files.append(filename)
			return files

		else:	
			directory = 'spectra_data_processed_all/' + met
			for filename in os.listdir(directory):
				files.append(filename)
			return files

