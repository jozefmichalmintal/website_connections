import argparse
import re
import sys
import json

import requests
from tools.logger import Output
from tools.wayback import Wayback
from tools.output_builder import OutputBilder
from tools import cache


o = Output()
out = OutputBilder()
cache = cache.DbCache("cache.db")

spyonweb_access_token = "ACCES TOKEN HERE"
spyonweb_url = "https://api.spyonweb.com/v1/"

google_adsense_pattern = re.compile("pub-[0-9]{1,}", re.IGNORECASE)
google_analytics_pattern = re.compile("ua-\d+-\d+", re.IGNORECASE)

wayback_past_years = 0  # how many years to past

# setup the commandline argument parsing
parser = argparse.ArgumentParser(description='Generate visualizations based on tracking codes.')

parser.add_argument("--graph",
					help="Output filename of the graph file. Example: bellingcat.gexf",
					default="connections.gexf")

parser.add_argument("--domain",
					help="A domain to try to find connections to.", )

parser.add_argument("--file",
					help="A file that contains domains, one per line.")

parser.add_argument("--wayback",
					help="How many years will the WayBack API crawl to past",
					default=0)

parser.add_argument("--apikey",
					help="SpyOnWeb API key")

args = parser.parse_args()


#
# Clean tracking code
#
def clean_tracking_code(tracking_code):
	if tracking_code.count("-") > 1:

		return tracking_code.rsplit("-", 1)[0]

	else:

		return tracking_code


#
# Extract tracking codes from a target domain.
#
def extract_tracking_codes(base_domains):
	site_connections = {}

	w = Wayback()
	ext_domains = base_domains[:]

	# get history of domains (wayback machine api)
	if wayback_past_years > 0:
		for domain in ext_domains:
			wayback_urls = w.closest(domain, years=wayback_past_years)
			base_domains.extend(_unique_list(wayback_urls))
			o.log("[*] Getting wayback url for %s .", domain)

	for domain in base_domains:
		if domain is "":
			continue

		# send a request off to the website
		try:

			o.log("[*] Checking %s for tracking codes.", domain)
			site = domain
			if domain.startswith("www"):
				domain = domain[4:]

			if not domain.startswith("http"):
				site = "http://" + domain

			response = requests.get(site)

		except requests.exceptions.RequestException as e:

			o.error("[!] Failed to reach site {}. \n{}", param=domain, error=e)

			continue

		# extract the tracking codes
		extracted_codes = []
		adsense_codes = google_adsense_pattern.findall(response.content)
		extracted_codes.extend(_unique_list(adsense_codes))

		analytics_codes = google_analytics_pattern.findall(response.content)
		extracted_codes.extend(_unique_list(analytics_codes))

		# loop over the extracted tracking codes
		for code in extracted_codes:

			# remove the trailing dash and number
			code = clean_tracking_code(code)

			# if code.lower() not in tracking_codes:

			o.log("[*] Discovered: %s", code.lower())

			if code not in site_connections.keys():
				site_connections[code] = [domain]
			else:
				site_connections[code].append(domain)

	return site_connections


def _unique_list(source):
	result = []
	for item in source:
		if item not in result:
			result.append(item)
	return result
#
# Send a request off to Spy On Web
#
def spyonweb_request(data, request_type="domain"):
	"""
	A Request to api.spyonweb.com
	The request https://api.spyonweb.com/v1/adsense/pub-1556223355139109?access_token=DjlnNO8Hbl3o
	and example of the response:
	{
		"status": "found",
		"result": {
			"adsense": {
			"pub-1556223355139109": {
				"fetched": 42,
				"found": 42,
							"items": {
								"bakertillysh.com": "2018-10-04",
								"brassbandtube.blogspot.com": "2012-04-23",
								"breathe07.blogspot.com": "2013-07-29",
								"chicago24.net": "2012-02-23",
								"cityoftime-roleplay.com": "2018-10-05",
								...
							}
				}
			}
		}
	}
	:param data: can be domain url [http://something.com], analytics code [UAXXXXXX] or
	adsence code [pub1234567890123456]
	:param request_type: can be 'domain', 'analytics' or 'adsense'
	:return json of result or None if it has found nothing
	"""

	params = {'access_token': spyonweb_access_token}

	url = spyonweb_url + request_type + "/" + data

	if not cache.is_cached(url):
		response = requests.get(url, params=params)
		cache.cache(url, json.dumps(response.json()))
		result = response.json()
	else:
		o.log("  ... cached url %s", url)
		result = json.loads(cache.get_cache(url))

	#if response.status_code == 200:
	if 'status' in result:

		#result = response.json()

		if result['status'] != "not_found" and result['status'] != "error":
			return result
	else:
		o.log("Request to SpyOnWeb API failed. Response : %s", result)

	return None


def spyonweb_analytics_codes(connections):
	"""
	Function to check the extracted analytics codes with Spyonweb API
	"""

	request_type = "domain"

	# use any found tracking codes on Spyonweb
	for code in connections:

		# send off the tracking code to Spyonweb
		if code.lower().startswith("pub"):

			request_type = "adsense"

		elif code.lower().startswith("ua"):

			request_type = "analytics"

		o.log("[*] Trying code: %s on Spyonweb.", code)

		results = spyonweb_request(code, request_type)

		print (results)

		if results and ('result' in results):

			for domain in results['result'][request_type][code]['items']:
				o.log("[*] Found additional domain: %s", domain)

				connections[code].append(domain)

	return connections


#
# Use Spyonweb to grab full domain reports.
#
def spyonweb_domain_reports(connections):
	# now loop over all of the domains and request a domain report
	tested_domains = []
	all_codes = connections.keys()

	for code in all_codes:

		for domain in connections[code]:

			if domain not in tested_domains:

				tested_domains.append(domain)

				o.log("[*] Getting domain report for: %s", domain)

				results = spyonweb_request(domain)

				if results and ('result' in results):

					# loop over adsense results
					adsense = results['result'].get("adsense")

					if adsense:

						for code in adsense:

							code = clean_tracking_code(code)

							if code not in connections:
								connections[code] = []

							for domain in adsense[code]['items'].keys():

								if domain not in connections[code]:
									o.log("[*] Discovered new domain: %s", domain)

									connections[code].append(domain)

					analytics = results['result'].get("analytics")

					if analytics:

						for code in analytics:

							code = clean_tracking_code(code)

							if code not in connections:
								connections[code] = []

							for domain in analytics[code]['items'].keys():

								if domain not in connections[code]:
									o.log("[*] Discovered new domain: %s", domain)

									connections[code].append(domain)

	return connections


# build a domain list either by the file passed in
# or create a single item list with the domain passed in

o.log("\n[*] Start crawling ...")

if args.apikey:
	spyonweb_access_token = args.apikey

if args.wayback:
	wayback_past_years = int(args.wayback)

if args.file:

	with open(args.file, "rb") as fd:

		domains = fd.read().splitlines()

else:

	domains = [args.domain]

# extract the codes from the live domains

connections = extract_tracking_codes(domains)

if len(connections.keys()):

	# use Spyonweb to find connected sites via their tracking codes
	connections = spyonweb_analytics_codes(connections)

	# request full domain reports from Spyonweb to tease out any other connections
	connections = spyonweb_domain_reports(connections)

	# now create a graph of the connections
	out.graph_connections(connections, domains, args.graph)

	# summary of whole process will be in output csv file
	out.summary(connections, domains, args.graph)

else:

	o.log("[!] No tracking codes found!")
	sys.exit(0)

o.log("[*] Finished! Open %s in Gephi!", args.graph)
