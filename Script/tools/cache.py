import sqlite3


class DbCache:

	def __init__(self, db_name):
		self.db_name = db_name
		self._create_table()

	def is_cached(self, key):
		result = self._select("SELECT count(*) from cache WHERE key='{}'".format(key))
		return True if result[0] > 0 else False

	def cache(self, key, value):
		self._insert(key, value)

	def get_cache(self, key):
		result = self._select("SELECT value from cache WHERE key='{}'".format(key))
		return result[0]

	def _execute(self, sql):
		self.conn = sqlite3.connect(self.db_name)
		self.conn.execute(sql)
		self.conn.commit()
		self.conn.close()

	def _select(self, sql):
		self.conn = sqlite3.connect(self.db_name)
		c = self.conn.cursor()
		c.execute(sql)
		return c.fetchone()

	def _create_table(self):
		self._execute('''CREATE TABLE IF NOT EXISTS cache (key text, value text)''')

	def _insert(self, key, value):
		self._execute("INSERT INTO cache (key, value) values ('{}','{}')".format(key, value))
