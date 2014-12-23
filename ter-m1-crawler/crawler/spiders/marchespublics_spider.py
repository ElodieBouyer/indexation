# -*- coding: utf-8 -*- 
#http://www.boamp.fr/avis/liste
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy import log
from scrapy.http import FormRequest
from bs4 import BeautifulSoup
from crawler.items import CrawlerItem
import re
import datetime
import locale

class MarchespublicsSpider(CrawlSpider):
	name = "Marchespublics"
	allowed_domains = ["marches-publics.info"]
	start_urls = ['http://www.marches-publics.info/mpiaws/index.cfm?fuseaction=mpAW.rechM']
	download_delay = 10 # le délais entre deux requêtes est mit à 10s pour éviter d'être banni

	def __init__(self, day=None, month=None, year=None):
		today = datetime.date.today()
		if day is None:
			day = today.day
		if month is None:
			month = today.month
		if year is None:
			year = today.year
		date = datetime.date(int(year),int(month),int(day))

		# le critères de date fonctionne aec une différence en jour entre aujourd'hui et la date souhaitée
		dateDiff = today - date
		if dateDiff.days > 0:
			self.date = dateDiff.days
		else:
			self.date = 0

	def parse(self, response):
		yield FormRequest("http://www.marches-publics.info/mpiaws/index.cfm?fuseaction=mpAW.listeM",
			formdata={'IDE': 'EC',
			'IDN': 'X',
			'IDP':'X', 
			'IDR':'X',
			'dateParution':' = '+str(self.date),
			'annee':'X'},
			callback=self.parse_page_resultat)

	def parse_page_resultat(self, response):
		selector = BeautifulSoup(response.body)
		regex = re.compile("\(([0-9]{2,5})\)[^\[]*(\[réf. ([^\]]*)\])?")
		trs = selector.select("table.AW_Table tr")
		if trs:
			trs = trs[1:]
			i = 0
			for tr in trs:
				#Décalaration de l'item
				item = CrawlerItem()
				for field in item.fields:
					item[field] = ""
				item['numberOfBatch'] = 0

				tds = tr.select("td.AW_Table_Ligne"+str(i))
				if len(tds) > 1: # les données sont séparés dans les différents tds
					""" 
					tds[0] = date de publication 
					tds[1] = date de remise des plis 
					tds[2] = l'entitée acheteur en gras (balise <b>), l'url dans une <table>, l'objet après le premier <br>, le département et la référence avant
					"""
					item['publicationDate'] = datetime.datetime.strptime(tds[0].get_text(), "%d/%m/%y")
					item['deliveryDate'] = datetime.datetime.strptime(tds[1].get_text().encode("utf8"), "%d/%m/%y à %Hh%M")
					
					url = tds[2].table.extract()
					url = url.select('a')[0]['href']
					entity = tds[2].b.extract()
					item['entityName'] = str(entity.get_text().encode('utf8')).strip()
					item['objet'] = str(tds[2].br.next.encode('utf8')).strip()
					valuesDepAndRef = str(tds[2].br.previous.encode('utf8')).strip()
					valuesDepAndRef = regex.findall(valuesDepAndRef)
					if len(valuesDepAndRef[0][0]) > 2:
						item['departement'] = valuesDepAndRef[0][0][:2]
					if len(valuesDepAndRef[0][2]) > 2:
						item['reference'] = valuesDepAndRef[0][2]
					
					for param in url.split("&"):
						if "IDM" in param:
							item['technicalId'] = param[4:]

					request = Request("http://www.marches-publics.info/mpiaws/"+url, callback=self.parse_item)
					request.meta['item'] = item
					yield request

	def parse_item(self, response):
		item = response.meta['item']
		selector = BeautifulSoup(response.body)

		text = selector.select('#AAPCGenere')[0]
		item['text'] = str(text)

		contactTable = selector.select('#AAPCGenere table')[1]
		contact = contactTable.tr.td.extract()
		contact.table.extract()
		item['executionPlace'] = '\n'.join([s for s in contact.get_text().splitlines() if len(s.strip()) > 1]).replace('\t','')

		trs = selector.select('table.AW_TableM tr')
		regexCpv = re.compile("([0-9]{8})")

		for tr in trs:
			tds = tr.select('td.AW_TableM_Bloc1_Clair')
			if len(tds) >= 2:
				key = tds[0].get_text().strip().encode("utf8")
				value = tds[1].get_text().strip().encode("utf8")
				lots_trs = tds[0].select('table tr')

				if key == "Nature":
					item['marketType'] = value
				if key == "Mode":
					item['procedureType'] = " ".join(value.split())
				if key == "Référence":
					item['reference'] = value
				if key == "Nomenclature":
					print regexCpv.findall(value)
				if len(lots_trs) > 0:
					item['numberOfBatch'] = len(lots_trs)
		return item
