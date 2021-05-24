#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

import datetime


class Wayback(object):

	API_WAYBACK_URL = 'http://archive.org/wayback/available'

	def __init__(self):
		"""
		Initialize Wayback.

		"""

		self._clean()

	def _clean(self):
		self.archive_timestamp = None
		self.archive_url = ''
		self.archive_timestamps = []
		self.archive_urls = []

		self.url = ''
		self.timestamp = None
		self.status_code = None

	def _parse_response(self, resp):

		""" Example of response (web.archive.org)

		{
			"url": "morione.sk",
			"archived_snapshots": {
				"closest": {
				"status": "200",
				"available": true,
				"url": "http://web.archive.org/web/20181203110026/http://www.morione.sk/",
				"timestamp": "20181203110026"
				}
			}
		}

		"""

		self.archive_timestamp = None
		self.archive_url = None
		self.status_code = resp.status_code

		if self.status_code == 200:
			rdict = resp.json()
			if rdict['archived_snapshots']:
				closest = rdict['archived_snapshots']['closest']
				self.archive_timestamp = closest.get('timestamp', None)
				self.archive_url = closest.get('url', '')

	def closest(self, url, timestamp=None):
		"""
		Get the closest snapshot.

		Args:
			url: A string containing the URL to check.

			timestamp: A string containing the timestamp to look up.
				(Default: None)

		Raises:
			requests.exceptions.HTTPError

		Returns:
			A string containing the URL of the closest snapshot, or the
			empty string, if none is available.

		"""
		self._clean()
		resp = self._get_response(url, timestamp)
		self._parse_response(resp)

		return self.archive_url

	def closest(self, url, timestamp=None, years=0):
		"""
		Get the closest snapshots from timestamp counting by years to past.

		Args:
			url: A string containing the URL to check.

			timestamp: A string containing the timestamp to look up.
				(Default: None)

			years: A integer of years to past

		Raises:
			requests.exceptions.HTTPError

		Returns:
			An array of string containing the URL from timestamp counting by years to past, or the
			empty array, if none is available.

		"""
		self._clean()
		resp = self._get_response(url, timestamp)
		self._parse_response(resp)
		actual_timestamp = self.archive_timestamp

		if actual_timestamp is None:
			return self.archive_urls

		for i in range(0, years):
			resp = self._get_response(url, self._get_year(actual_timestamp, i))
			self._parse_response(resp)
			self.archive_timestamps.append(self.archive_timestamp)
			self.archive_urls.append(self.archive_url)

		return set(self.archive_urls)

	def _get_response(self, url, timestamp=None):

		self.url = url
		self.timestamp = timestamp

		data = {
			'url': self.url,
		}
		if self.timestamp is not None:
			data['timestamp'] = self.timestamp

		return requests.get(self.API_WAYBACK_URL, params=data)

	def _get_year(self, timestamp, years):
		ts_format = "%Y%m%d%H%M%S"
		days_per_year = 365.24
		ts = datetime.datetime.strptime(timestamp, ts_format)
		result = ts - datetime.timedelta(days=(years * days_per_year))
		return result.strftime(ts_format)


if __name__ == '__main__':
	pass
