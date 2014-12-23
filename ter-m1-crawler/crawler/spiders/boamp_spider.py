# -*- coding: utf-8 -*- 
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

class BoampSpider(CrawlSpider):
	name = "boamp"
	allowed_domains = ["boamp.fr"]
	start_urls = ['http://www.boamp.fr/recherche/avancee']

	def __init__(self, day=None, month=None, year=None):
		today = datetime.date.today()
		if day is None:
			day = today.day
		if month is None:
			month = today.month
		if year is None:
			year = today.year
		self.date = datetime.date(int(year),int(month),int(day))

	def parse(self, response):
		today = self.date.strftime('%d/%m/%Y')

		# on effectue la recherche initiale
		yield FormRequest.from_response(response,
			formname='formRecherche',
			formdata={'dateparutionmin': today,
			'dateparutionmax': today,
			'estrecherchesimple':'0', 
			'archive':'0',
			'idweb':'',
			'nomacheteur':'',
			'prestataire':'',
			'datelimitereponsemin':'',
			'datelimitereponsemax':'',
			'typeseuil':'',
			'fulltext':''},
			callback=self.parse_page_resultat)

	def parse_page_resultat(self, response):
		selector = Selector(response)
		linesResult = selector.xpath('//form[@id="results"]//table//tr[@class="corps"]').extract()

		for lineResult in linesResult:
			lineSelector = BeautifulSoup(lineResult.encode("utf8"))

			obj = lineSelector.select('td.tabObjet p') 
			url = obj[1].find_all("a",href=True)
			obj = obj[0].get_text().strip()

			# récupération des informations disponible sur la page de recherche
			acheteur = lineSelector.select('td.tabAcheteur')[0].get_text().strip()
			publication = lineSelector.select('td.tabPublication')[0].get_text().strip()
			reponse = lineSelector.select('td.tabReponse')[0].get_text().strip()
			lieu = lineSelector.select('td.tabLieu')[0].get_text().strip()
			typeAvis = lineSelector.select('td.tabAvis')[0].get_text().strip()
			procedure = lineSelector.select('td.tabProcedure')[0].get_text()

			# création de l'item avec les informations que l'on a déjà
			item = CrawlerItem()
			item["objet"] = obj.encode('utf8')
			item["entityName"] = acheteur.encode('utf8')
			item["publicationDate"] = publication.encode('utf8')
			item["deliveryDate"] = reponse.encode('utf8')
			item["departement"] = lieu.encode('utf8')
			item["marketType"] = ' '.join(typeAvis.encode('utf8').split())
			item["procedureType"] = procedure.encode('utf8')

			# on effectue la recherche si le lien est bien relatif à un avis
			if "avis/detail/" in url[0].get('href'):
				request = Request("http://www.boamp.fr" + url[0]['href'], callback=self.parse_item)
				request.meta['item'] = item
				yield request

		# suivit des pages de la pagination
		pagination = selector.xpath('//div[@class="pagination"]//span[@class="passif"]/following-sibling::a/@href').extract()
		
		if len(pagination) > 0:
			yield Request("http://www.boamp.fr" + pagination[0], callback=self.parse_page_resultat)


	def parse_item(self, response):
		selector = Selector(response)
		#sélection du lien officiel dans les onglets
		url = selector.xpath('//div[@id="infos"]/p[@class="officiel"]/a/@href').extract()
		if len(url) == 1: # on l'a trouvé, on le suit
			item = response.meta['item']
			request = Request("http://www.boamp.fr" + url[0], callback=self.parse_official_link)
			request.meta['item'] = item
			return request
		else: # il n'existe pas, on tente notre chance sur la page courrant qui est souvent celle au format officiel
			if len(selector.css(".officielOnly").extract()) == 1:
				item = response.meta['item']
				selector = Selector(response)
				html = selector.css("#avisOfficiel").extract()
				references = selector.css("#references").extract()
				return self.extract_data(html, references, response.url,item)

	def parse_official_link(self, response):
		item = response.meta['item']
		selector = Selector(response)
		html = selector.css("#avisOfficiel").extract()
		references = selector.css("#references").extract()
		return self.extract_data(html, references, response.url,item)
		

	def extract_data(self, html, references, url,item):
		""" Dans cette fonction on parse les informations trouvés via des regex.
		Plusieurs cas sont parfois possible et de nombreux nettoyages sont nécessaires"""

		html = "".join(html)
		soup = BeautifulSoup(html)

		text = soup.prettify().encode("utf-8")
		
		marketType = soup.find_all(text=re.compile("Type de march. de"))

		if len(marketType) == 1:
			marketType = marketType[0][18:-2].encode('utf8').split(":")[0].strip()
		elif len(marketType) > 1:
			marketType = [s[0][18:-2].encode('utf8').split(":")[0].strip() for s in marketType]
			", ".join(marketType)[:-2]
		else:
			marketType = ""
		
		cpvCode = self.find_element(soup, "C.P.V.")
		if cpvCode != None :
			pass
		else:
			cpvCode = self.find_element(soup, "CPV") # second format d'écriture des codes cpv

		executionPlace = self.find_element(soup, "Lieu d.ex.cution")
		if executionPlace and "NUTS" in executionPlace: # parfois le lieu d'execute ne contient que NUTS, dans ce cas on n'a pas le lieu d'execution
			executionPlace = ""

		numberOfBatch = self.find_element(soup, "Renseignements relatifs aux lots")
		if numberOfBatch != None:
			numberOfBatch = BeautifulSoup(str(numberOfBatch))
			numberOfBatch = len(numberOfBatch.find_all("tr"))
		else:
			numberOfBatch = 0

		reference = self.find_element(soup, "Num.ro de r.f.rence attribu.")

		
		technicalId = url.split("/")[-2]

		item['text'] = text.replace("%%", '%')
		item['executionPlace'] = executionPlace
		if len(marketType) > 2: 
			item['marketType'] = marketType
		item['cpvCode'] = cpvCode
		item['numberOfBatch'] = numberOfBatch
		item['reference'] = self.striphtml(reference)
		item['technicalId'] = technicalId
		item['directUrl'] = None
		item['thisUrl'] = url
		return item

	def find_element(self, soup, text):
		""" Cette fonction recherche le text sous forme de regex et renvoie l'élément suivant. 
		Si l'élément est un saut de ligne on cherche encore le suivant"""

		elem = soup.find_all(text=re.compile(text.replace(".", ".{1,2}")))
		if len(elem) == 1:
			if "<br" in elem[0].next_element.encode('utf8'):
				elem[0] = elem[0].next_element
			elem = elem[0].next_element.encode('utf8')
		else:
			elem = None

		return elem

	def striphtml(self, data):
		if isinstance(data,str):
			p = re.compile(r'<.*?>')
			return p.sub('', data)
		else:
			return data