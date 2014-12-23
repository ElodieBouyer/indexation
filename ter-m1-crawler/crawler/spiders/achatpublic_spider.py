# -*- coding: utf-8 -*- 
from scrapy.contrib.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy import log
from scrapy.http import FormRequest
from bs4 import BeautifulSoup
from crawler.items import CrawlerItem
import re
import datetime
import locale
from scrapy.conf import settings

class AchatpublicSpider(CrawlSpider):
	name = "achatpublic"
	allowed_domains = ["achatpublic.com"]
	start_urls = ['https://www.achatpublic.com/sdm/ent/gen/ent_recherche.do']

	def __init__(self, day=None, month=None, year=None):
		# on spécifie le middleware spécifique pour ce crawler
		settings.overrides['DOWNLOADER_MIDDLEWARES'] = {'crawler.middlewares.AchatpublicDupFilterMiddleware':390}
		# on diminue les requêtes parallèles à 1
		settings.overrides['CONCURRENT_REQUESTS'] = 1
		settings.overrides['CONCURRENT_REQUESTS_PER_DOMAIN'] = 1

		locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
		self.page = 0
		self.max = None
		self.dateFormat = "%d %B %Y %Hh%M"

		today = datetime.date.today()
		if day is None:
			day = today.day
		if month is None:
			month = today.month
		if year is None:
			year = today.year
		self.date = datetime.date(int(year),int(month),int(day))

	def parse(self, response):
		selector = BeautifulSoup(response.body)
		pagination = selector.select('input.formPagination')
		regex = re.compile("numberOrEnter\(event,this,([0-9]+),[0-9]+\);")
		maxiPage = regex.findall(str(pagination[0]))[0]
		
		for page in range(1,int(maxiPage)):
			# la recherche se fait en POST avec un certain nombre de paramètres qui ne bougent pas mise à part la page.
			yield FormRequest('https://www.achatpublic.com/sdm/ent/gen/ent_recherche.do',
				formdata={'consulId':'',
							'act':'sea',
							'reference':'',
							'referenceapc':'',
							'personnepublique':'',
							'procedure':'-1',
							'marche':'-1',
							'intitule':'',
							'region':'',
							'departement':'',
							'objetRecherche':'-1',
							'orderby':'9',
							'page':str(page),
							'nbAffiche':'10',
							'jour':str(self.date.day),
							'mois':str(self.date.month),
							'annee':str(self.date.year),
							'precisionDate':'apres',
							'codeCPV':'',
							'typeLieu':'passation',
							'userRef':''
				},
				callback=self.parse_pagination)

	def parse_pagination(self,response):
		selector = BeautifulSoup(response.body)
		lines = selector.select('#content table tr td div table tr')
		lines = lines[:]
		for line in lines:
			tds = line.findAll("td")
			for td in tds:
				# récupération des identifiants techniques pour former l'adresse "manuellement"
				regex = re.compile("getElementById\('consulId'\),'([^']+)',document.getElementById")
				yield Request('https://www.achatpublic.com/sdm/ent/gen/ent_detail.do?PCSLID='+regex.findall(str(td))[0],
					callback=self.parse_item)
				break


	def parse_item(self, response):
		selector = BeautifulSoup(response.body)
		
		# chaque annonce est divisée en deux tables. On les réunies pour les traiter qu'une seule fois.
		lines = selector.select('#content div div div table')
		lines2 = selector.select('#content div table table')
		lines.extend(lines2)

		# initialisation de l'item
		item = CrawlerItem()
		for field in item.fields:
			item[field] = ""

		nextIsLots = False # les lots sont différents, une ligne "annonce" qu'il y a des lots mais les lots sont dans la ligne suivante
		
		for l in lines:
			for line in l.findAll('tr',recursive=False):
				tds = line.select("td")
				if len(tds) > 1:
					key_brut = tds[0]
					key = str(key_brut)
					value_brut = tds[1]
					value = value_brut.get_text().strip().encode("utf8")

					if nextIsLots: # la ligne précédente annoncait des lots
						lotsTr = key_brut.select('table tr')
						lotsTd = lotsTr[len(lotsTr)-1:][0].select('td')[0].get_text()
						item['numberOfBatch'] = int(lotsTd)
						nextIsLots = False
						continue

					if "Type de procédure" in key:
						item['procedureType'] = value
					if "Organisme" in key:
						item['entityName'] = value
					if "Intitulé de la consultation" in key:
						item['objet'] = value
					if "Référence de la consultation" in key:
						item['reference'] = value
					if "Type de marché" in key:
						item['marketType'] = value
					if "Description" in key:
						item['objet'] = value
					if "Lieu d'exécution" in key:
						item['executionPlace'] = "\n".join(filter(None,value.splitlines()))
					if "Date limite de remise des plis" in key:
						if len(value) > 4:
							try:
								date = " ".join(value.replace('-', '').split('(')[0].strip().split())
								value = datetime.datetime.strptime(date, self.dateFormat)
							except:
								value = None
						item['deliveryDate'] = value
					if "Allotissement" in key: # l'allotissement n'anonce en générale pas les lots, 
						#juste qu'il n'y en a pas. Cf la condition "Lot(s)"
						if "Marché unique" in value:
							value = 0
						item['numberOfBatch'] = int(value)
					if  "Lot(s)" in key:
						nextIsLots = True
					if "Date d'ouverture de la salle" in key:
						if len(value) > 4:
							try:
								date = " ".join(value.replace('-', '').split('(')[0].strip().split())
								value = datetime.datetime.strptime(date, self.dateFormat)
							except:
								value = None
						item['publicationDate'] = value

		if not isinstance(item['numberOfBatch'],int): # si on a pas d'infos sur les lots on les met à 0
			item['numberOfBatch'] = 0

		item['thisUrl'] = response.url
		item['text'] = selector.select("#content .right2")[0].encode('utf8')
		item['technicalId'] = "".join(response.url.split("PCSLID=")[1:])

		return item