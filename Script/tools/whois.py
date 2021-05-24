import os
import tempfile
import shlex
import requests
from abc import ABCMeta, abstractmethod
from subprocess import Popen, PIPE
from threading import Timer
from bs4 import BeautifulSoup


class WhoIs(object):
	"""
	Abstract class for WhoIs functionality
	"""

	__metaclass__ = ABCMeta

	@staticmethod
	@abstractmethod
	def get_info(domain):
		return

	@classmethod
	def _parse_info(cls, content):
		return

	def parse_file(self, filename):
		out = dict()
		with open(filename) as fp:
			for cnt, line in enumerate(fp):
				print("whois for: {}".format(line))
				out[line] = (self.get_info(line))
		return out


class WhoIsCom(WhoIs):
	"""
	The WHOIS implementation by www.whois.com api. No obligations, no need to have API KEY
	"""

	@staticmethod
	def get_info(domain):
		api_url = "https://www.whois.com/whois/"
		site = api_url + domain
		try:
			response = requests.get(site)
			return WhoIsCom._parse_info(response.content)
		except requests.exceptions.RequestException as e:
			print(e)
		return ""

	@classmethod
	def _parse_info(cls, content):
		soup = BeautifulSoup(content, 'html.parser')
		out = []
		if soup.select(".df-raw"):
			raw = soup.select(".df-raw")[0].text
			lines = raw.split("\n")
			for line in lines:
				x = line.split(":", 1)
				if len(x) == 2:
					out.append({x[0].strip(): x[1].strip()})
		return out


class Command(WhoIs):

	@staticmethod
	def get_info(domain):
		"""
		Get info about domain. It is used linux command 'whois' for this purpose.

		Example of response :

		{'City': 'Banska Bystrica', 'domain': 'SK', 'Tech Contact': 'WEBS-0001', 'Postal Code': '97405',
		'Email': 'helpdesk@websupport.sk', 'Name': 'Ing. Michal Kalman', 'Updated': '2018-01-11',
		'whois': 'whois.sk-nic.sk', 'source': 'IANA', 'organisation': 'SK-NIC, a.s.',
		'Admin Contact': 'WEBS-0001', 'Phone': '+421.220608080', 'e-mail': 'tech-c@sk-nic.sk',
		'Street': 'Radvanska 508/20', 'Organization ID': '50964186', 'refer': 'whois.sk-nic.sk',
		'status': 'ACTIVE', 'fax-no': '+421 2 350 350 39', 'Created': '2018-01-11', 'Country Code': 'SK',
		'EPP Status': 'ok', '% for more information on IANA, visit http': '//www.iana.org',
		'phone': '+421 2 350 350 30', 'Contact': 'WS-38126', 'Registrar': 'WEBS-0001',
		'address': 'Slovakia', 'remarks': 'Registration information: http://www.sk-nic.sk',
		'Organization': 'Morione s.r.o.', 'Nameserver': 'ns3.websupport.sk', 'Domain': 'morione.sk',
		'name': 'Technical Director', 'created': '1993-03-29',
		'nserver': 'H.TLD.SK 212.18.249.16 2a04:2b00:13ff:0:0:0:0:16', 'Valid Until': '2019-07-07',
		'changed': '2018-10-19', 'contact': 'technical', 'Registrant': 'WS-38126'}
		"""
		out = []

		if domain.startswith('http://web.archive.org/') or domain == "":
			return out

		f = tempfile.NamedTemporaryFile(delete=False)
		exec_command = "whois " + domain + " > " + f.name
		tt = Command._run(exec_command, 15)

		if tt:
			for t in tt.split("\r"):
				x = t.split(":", 1)
				if len(x) == 2:
					out.append({x[0].strip(): x[1].strip()})
		else:
			for line in open(f.name, "r"):
				x = line.split(":", 1)
				if len(x) == 2:
					out.append({x[0].strip(): x[1].strip()})

		os.unlink(f.name)
		return out

	@classmethod
	def _run(cls, cmd, timeout_sec):
		proc = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
		timer = Timer(timeout_sec, proc.kill)
		try:
			timer.start()
			stdout, stderr = proc.communicate()
			return stdout
		finally:
			timer.cancel()