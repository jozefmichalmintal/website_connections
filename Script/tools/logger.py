#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import datetime
# from IPython.display import HTML
# import base64


class Output:

	def __init__(self, filename=None, level=logging.DEBUG):

		self.logfile = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".log"
		if filename:
			self.logfile = filename

		logging.basicConfig(filename=self.logfile, level=level)

	def log(self, message, param=None):
		if param:
			print (message % param)
			logging.info(message, param)
		else:
			print (message)
			logging.info(message)
		return

	def error(self, message, error=None, param=None):
		if error and param:
			print (message.format(param, error))
			logging.error(message.format(param, error))
		elif error:
			#print (message % error)
			print (message)
			#logging.error(message, error)
			logging.error(message)
		else:
			print (message)
			logging.error(message)
		return

	# def create_download_link(self, filename, title="Download file"):
	# 	f = open(filename,"r")
	# 	b64 = base64.b64encode(f.read())
	# 	payload = b64.decode()
	# 	html = '<a download="{filename}" href="data:text/csv;base64,{payload}" target="_blank">{title}</a>'
	# 	html = html.format(payload=payload, title=title, filename=filename)
	# 	return HTML(html)

