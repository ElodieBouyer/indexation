# -*- coding: utf8 -*- 
import sys
import MySQLdb
import hashlib
from scrapy.exceptions import DropItem
from scrapy import signals
from scrapy.http import Request
from scrapy.utils.project import get_project_settings
import uuid
from scrapy import log
import datetime
import ho.pisa as pisa
import os

class CrawlerPipeline(object):


	def __init__(self):
		""" Initialise la connexion au serveur MySQL """
		settings = get_project_settings()
		self.conn = MySQLdb.connect(user=settings.get('DB_USER'), 
									passwd=settings.get('DB_PASSWD'), 
									db=settings.get('DB_DATABASE'), 
									host=settings.get('DB_HOST'), charset="utf8", use_unicode=True)
		self.cursor = self.conn.cursor()

		pdfPath = get_project_settings().get('PDF_DIR')
		self.pdfPath = pdfPath

		if not os.path.isdir(pdfPath): # vérification de l'existance du répertoire contenant les PDF.
			os.makedirs(pdfPath) # on créé le répertoire.
		self.fullRepositoryExist = False


	def process_item(self, item, spider):	
		""" Cette fonction est chargée d'enregistrer les données en base ainsi que de créer les pdf. """
		pdfPath = self.pdfPath

		if not self.fullRepositoryExist:
			if not os.path.isdir(pdfPath+spider.name + "/"): # vérification de l'existance du répertoire contenant les PDF.
				os.makedirs(pdfPath+spider.name + "/") # on créé le répertoire.
			self.fullRepositoryExist = True

		filename = str(uuid.uuid4()) + ".pdf"

		publicationDate = item['publicationDate']
		deliveryDate = item['deliveryDate']

		if isinstance(publicationDate, str):
			try:
				publicationDate = datetime.datetime.strptime(publicationDate, "%d/%m/%Y")
			except Exception:
				publicationDate = None

			try:
				deliveryDate = datetime.datetime.strptime(deliveryDate, "%d/%m/%Y")
			except Exception:
				deliveryDate = None
			
		else:
			try:
				publicationDate = publicationDate.strftime("%Y-%m-%d %H:%M:%S")
			except Exception:
				publicationDate = None

			try:
				deliveryDate = deliveryDate.strftime( "%Y-%m-%d %H:%M:%S")
			except Exception:
				deliveryDate = None
			
		try:
			
			self.cursor.execute("""INSERT INTO `avis` (buyingEntity, object, marketType, procedureType, departement, executionPlace, publicationDate, endDate, 
			numberOfBatch, reference, textName, technicalReference, scrapperName, doublon, id_avis)
			VALUES
			(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", 
			(item['entityName'],
			item['objet'],
			item['marketType'],
			item['procedureType'],
			item['departement'],
			item['executionPlace'],
			publicationDate,
			deliveryDate,
			item['numberOfBatch'],
			item['reference'],
			spider.name + "/" + filename,
			item['technicalId'],
			spider.name,0,0))
			self.conn.commit()
		except MySQLdb.Error, e:
			print e
			return # Duplicate, don't store it.

		idInsert = self.cursor.lastrowid
		
		if idInsert : # l'avis a bien été enregistré.

			fileSys = file(pdfPath + spider.name + "/" + filename, "wb")
			pisa.CreatePDF(item['text'], fileSys) # Création du PDF
			fileSys.close()

			if isinstance(item['cpvCode'], str):
				if type(item['cpvCode']):
					item['cpvCode'] = [item['cpvCode']]
			if item['cpvCode']:
				for value in item['cpvCode']:
					for cpv in [int(s) for s in value.split() if s.isdigit()]:
						try:
							self.cursor.execute("""INSERT INTO `cpv` (number, id_avis)
							VALUES
							(%s,%s)""", 
							(cpv,
							idInsert))
						except MySQLdb.Error, e:
							print "Error %d: %s" % (e.args[0], e.args[1])

			if item['thisUrl']:
				try:
					self.cursor.execute("""INSERT INTO `urls` (url, id_avis)
					VALUES
					(%s,%s)""", 
					(item['thisUrl'],
					idInsert))
				except MySQLdb.Error, e:
						print "Error %d: %s" % (e.args[0], e.args[1])

			if item['directUrl']:
				if type(directUrl) == 'str':
					item['directUrl'] = [item['directUrl']]
				try:
					for url in item['directUrl']:
						self.cursor.execute("""INSERT INTO `urls` (url, id_avis)
						VALUES
						(%s,%s)""", 
						(item['directUrl'],
						idInsert))
				except MySQLdb.Error, e:
						print "Error %d: %s" % (e.args[0], e.args[1])

			self.conn.commit()
		return 