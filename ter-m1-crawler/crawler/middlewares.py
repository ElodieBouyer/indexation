# -*- coding: utf-8 -*- 
from scrapy.utils.project import get_project_settings
import MySQLdb
from scrapy import log
from scrapy.exceptions import IgnoreRequest
import collections

# Middleware générique basée sur la présence d'un id technique déjà crawlé.
class DupFilterMiddleware(object):
	def __init__(self):
		settings = get_project_settings()
		self.conn = MySQLdb.connect(user=settings.get('DB_USER'), 
									passwd=settings.get('DB_PASSWD'), 
									db=settings.get('DB_DATABASE'), 
									host=settings.get('DB_HOST'), charset="utf8", use_unicode=True)
		self.cursor = self.conn.cursor()

		self.ref_set = None

	def process_request(self, request, spider):
		if self.ref_set == None:
			self.ref_set = set()
			self.cursor.execute("SELECT technicalReference FROM avis where scrapperName =\'" + spider.name + "\'")
			for url in self.cursor.fetchall():
				self.ref_set.add(url[0])

		if len([el for el in self.ref_set if isinstance(el, collections.Iterable) and (el in request.url)]) > 0:
			raise IgnoreRequest()
		else:
			return None

# middleware spécifique pour le scraper Achatpublic, basé sur l'url complète
class AchatpublicDupFilterMiddleware(object):
	def __init__(self):
		settings = get_project_settings()
		self.conn = MySQLdb.connect(user=settings.get('DB_USER'), 
									passwd=settings.get('DB_PASSWD'), 
									db=settings.get('DB_DATABASE'), 
									host=settings.get('DB_HOST'), charset="utf8", use_unicode=True)
		self.cursor = self.conn.cursor()

		self.url_set = set()
		self.cursor.execute('SELECT url FROM urls where url like "%achatpublic.com%"')
		for url in self.cursor.fetchall():
			self.url_set.add(url[0])

	def process_request(self, request, spider):
		if request.url in self.url_set:
			raise IgnoreRequest()
		else:
			return None