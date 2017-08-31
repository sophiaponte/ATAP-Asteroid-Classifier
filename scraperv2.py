import sys
import math
import xlrd
import json
from lxml import html
import requests
import urllib2
import time


'''
	open a session
	submit form 1
	session info is implicitly kept track of (?)
	submit form 2

	

'''
class Scraperv2:


	@staticmethod
	def get_code(response_text, code):
		line_code = []
		code_value = ""

		for item in response_text.split("\n"):
			if code in item:
				line_code = item.strip()

		for item in line_code.split(" "):
			if "value" in item:
				code_value = item.strip().split("\"")[1] 
				
		return code_value


	@staticmethod
	def submit_form1(filename, range_):

		print filename

		url_1 = 'http://smass.mit.edu/cgi-bin/busdemeoclass-cgi'
		spa_1 = "input"
		sfn_1 = open(filename, "rb")
		lun_1 = "um" # microns
		tax_1 = range_
		sls_1 = "sloped"
		slv_1 = ""
		_int_1 = "0" 
		sms_1 = "unsmoothed"
		smv_1 = "1.00"
		submit = "Next >"

		form_params_1 = {
			"spa": spa_1,
			"lun": lun_1,
			"tax": tax_1,
			"sls": sls_1,
			"slv": slv_1,
			"int": _int_1,
			"sms": sms_1,
			"smv": smv_1,
			"sub1": submit
		}

		file_params_1 = (
			("sfn", sfn_1),
		)

		s = requests.Session()
		response1 = s.post(url_1, data=form_params_1, files=file_params_1)

		tfc = Scraperv2.get_code(response1.text, "tfc")
		pfc = tfc #pfc and tfc are the same


		url_2 = "http://smass.mit.edu/cgi-bin/busdemeoclass-cgi"
		spa_2 = "resmooth"
		sfn_2 = open(filename, "rb")
		lun_2 = "um"
		tax_2 = range_
		sls_2 = "sloped"
		slv_2 = ""
		int_2 = "0"
		osv_2 = "1.00"
		sms_2 = "smoothed"
		submit_2 = "Next"


		form_params_2 = {
			"spa" : spa_2,
			"pfc" : pfc,
			"tfc" : tfc,
			"sfn" : sfn_2,
			"lun" : lun_2,
			"tax" : tax_2,
			"sls" : sls_2,
			"slv" : slv_2,
			"int" : int_2,
			"osv" : osv_2,
			"sms" : sms_2,
			"sub2":submit_2
		}

		file_params_2 = {
			"sfn" : sfn_2
		}

		response2 = s.post(url_2, data=form_params_2, files = file_params_2)

		rfc = Scraperv2.get_code(response2.text, "rfc")

		url_3 = "http://smass.mit.edu/cgi-bin/busdemeoclass-cgi"
		spa_3 = "resultun"
		sfn_3 = open(filename, "rb")
		lun_3 = "um"
		tax_3 = range_
		sls_3 = "sloped"
		slv_3 = ""
		_int_3 = "0"
		sms_3 = "smoothed"
		smv_3 = "1.00"
		ema_3 = "m.atap.data@gmail.com"
		sub_3 = "Send results"


		form_params_3 = {
			"spa" : spa_3,
			"pfc" : pfc,
			"tfc" : tfc,
			"rfc" : rfc,
			"sfn" : sfn_3,
			"lun" : lun_3,
			"tax" : tax_3,
			"sls" : sls_3,
			"slv" : slv_3,
			"int" : _int_3,
			"sms" : sms_3,
			"smv" : smv_3,
			"ema" : ema_3,
			"sub3" : sub_3
		}

		file_params_3 ={
			"sfn" : sfn_3
		}
		response3 = s.post(url_3, data=form_params_3, files = file_params_3)
