import networkx
import re
from tools.logger import Output
import tools.whois


class OutputBilder(object):

	"""
	Class for building output

		- Graph for Gephi or other tools
		- Output csv file with processed domains
	"""

	def __init__(self):
		self.o = Output()
		self.tracking_code = {}

	def graph_connections(self, connections, domains, graph_file):
		"""
		Graph the connections so we can visualize in Gephi or other tools
		:param connections: founded connections
		:param domains: original input domains
		:param graph_file: output gephi file
		:return: True (method created gephi file)
		"""

		graph = networkx.Graph()

		for connection in connections:

			# add the tracking code to the graph
			graph.add_node(connection, type="tracking_code")
			self.tracking_code[connection] = []

			for domain in connections[connection]:

				# if it was one of our original domains we set the attribute appropriately
				if domain in domains:

					graph.add_node(domain, type="source_domain")
					self.tracking_code[connection].append(Domain(domain, True))

				else:

					# this would be a discovered domain so the attribute is different
					graph.add_node(domain, type="domain")
					self.tracking_code[connection].append(Domain(domain, False))

				# now connect the tracking code to the domain
				graph.add_edge(connection, domain)

		networkx.write_gexf(graph, graph_file)

		self.o.log("[*] Wrote out graph to %s", graph_file)

		return

	def summary(self, connections, domains, csv_file):

		if 'gexf' in csv_file:
			csv_file = csv_file.replace('gexf', 'csv')

		if len(self.tracking_code) == 0:
			self.graph_connections(connections, domains, csv_file)

		outfile = open(csv_file, "w")
		# header
		outfile.writelines("{}; {}; {}; {}; {}; {}; {}\r\n".format("tracking code", "domain", "is source domain", "status", "organization", "country", "alternative country"))

		# body
		for k, v in self.tracking_code.items():
			self.o.log("[*] writing key	 %s to csv file", k)
			for d in v:
				if d.is_source:
					outfile.writelines("{};{};{};{};\r\n".format(k, d.name, True, self._print_info(d.info)))
					#print("Source domain: %s %s", d.name, self._print_info(d.info))
				else:
					outfile.writelines("{};{};{};{}\r\n".format(k, d.name, False, self._print_info(d.info)))
					#print("Related domain: %s %s", d.name, self._print_info(d.info))

		outfile.close()
		self.o.log("[*] Wrote out csv summary to %s", csv_file)

		return

	def _print_info(self, info):
		"""
		Parsing output to csv string
		:param info: list of WHOIS result dictionary
		:return: parsed csv string
		"""
		status = ""
		address = []
		organization = ""
		state = ""

		if info is None:
			return ""

		for item in info:

			if 'status' in item.keys():
				status = item['status']
			if 'address' in item.keys():
				if re.match("^\D+$", item['address']):
					if item['address'] not in address:
						address.append(item['address'])

			if 'Organization' in item.keys() and organization == "":
				organization = item['Organization']

			if 'Country Code' in item.keys() and state == "":
				state = item['Country Code']

		size = 999
		res = ""
		if len(address) > 0:
			for i in address:
				if size >= len(i):
					size = len(i)
					res = i

		return "{}; {}; {}; {}".format(status, organization, res, state)
		#return res


class Domain(object):

	def __init__(self, name, is_source):
		self.name = name
		self.is_source = is_source
		#self.info = tools.whois.WhoIs.get_info(name)
		self.info = tools.whois.Command.get_info(name)
		#self.info = tools.whois.WhoIsCom.get_info(name)

