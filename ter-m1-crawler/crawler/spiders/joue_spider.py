# -*- coding: utf-8 -*- 
from scrapy.contrib.spiders import CrawlSpider, Rule
from selenium import webdriver
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy import log
from scrapy.http import FormRequest
from bs4 import BeautifulSoup
from crawler.items import CrawlerItem
from twisted.internet import reactor, defer
import re
import datetime
import locale
import os
import subprocess
import time

class JoueSpider(CrawlSpider):
	name = "joue"
	allowed_domains = ["europa.eu"]
	start_urls = ['http://ted.europa.eu/TED/misc/chooseLanguage.do']
	download_delay = 2 # le délais entre deux requêtes est mit à 2s pour éviter d'être banni

	def __init__(self, name=None, day=None, month=None, year=None, **kwargs):
		today = datetime.date.today()
		if day is None:
			day = today.day
		if month is None:
			month = today.month
		if year is None:
			year = today.year
		self.date = datetime.date(int(year),int(month),int(day))

		# On démarre Xvfb (permettant de faire tourner un navigateur sans GUI visible)
		self.procDisplay = subprocess.Popen(['Xvfb :99'], shell=True, stdout=None, stderr=None)
		time.sleep(1)
		self.saveDisplay = os.environ["DISPLAY"] # on sauvegarde l'éventuelle valeur pour la restaurée à la fin
		os.environ["DISPLAY"] = ":99" # on force l'affichage des nouvelles fenetre sur l'écran "void"
		self.driver = webdriver.Firefox()
		super(JoueSpider, self).__init__()

	def spider_closed(self,spider):
		os.environ["DISPLAY"] = self.saveDisplay # restauration de l'ancienne valeur du DISPLAY
		self.procDisplay.terminate()

	def parse(self, response):
		""" La recherche est lancée assez étrangement, elle ne semble pas être lancée via post.
		La solution trouvée est de piloter un navigateur internet pour simuler plus fidèlement une recherche"""

		self.driver.get(response.url)

		# page de sélection de la langue
		frLink = self.driver.find_element_by_xpath('//*[@id="menu"]/ul/li[9]/ins/a')
		frLink.click()

		# sur la page principale, on sélectionne la recherche
		linkFind = False
		while not linkFind:
			try:
				searchLink = self.driver.find_element_by_xpath('//*[@id="menuTabs"]/div/span/ins[1]/a')
				searchLink.click()
				linkFind = True
			except Exception:
				linkFind = False

		# on entre les critères de recherche
		edition = self.driver.find_element_by_id('searchCriteria.searchScopeId')
		for option in edition.find_elements_by_tag_name('option'):
			if "Tous les avis actuels" in option.text:
				option.click()
		pays = self.driver.find_element_by_id('searchCriteria.countryList')
		pays.send_keys('FR')
		type_doc = self.driver.find_element_by_id('searchCriteria.documentTypeList')
		type_doc.send_keys("'Avis de marché'".decode("utf8"))
		datepub = self.driver.find_element_by_id('searchCriteria.publicationDate')
		datepub.send_keys(self.date.strftime('%d-%m-%Y'))
		
		# on clique sur le bouton pour lancer la rechercher
		lancerRecherche = self.driver.find_element_by_css_selector('input[name*=".Rs.search."]')
		lancerRecherche.click()

		
		next = True
		while next:
			selector = BeautifulSoup(self.driver.page_source)
			urls = selector.select('#notice tbody tr a')
			for url in urls:
				# suit les liens vers les avis
				yield Request("http://ted.europa.eu/" + url['href'], callback=self.parse_page_resultat)

			try:
				# on suit la pagination jusqu'a ce que l'on tombe sur une exception
				suivant = self.driver.find_element_by_link_text('Suivant')
				suivant.click()
			except Exception: # le texte suivant n'existait pas, il n'y a pas de page suivante.
				next = False

		self.driver.quit()
	        

	def parse_page_resultat(self, response):
		selector = BeautifulSoup(response.body)
		doc = selector.select("#fullDocument")
		item = CrawlerItem()
		item['text'] = str(doc[0])
		item['thisUrl'] = response.url

		# les urls contiennent TEXT, c'est l'avis au format textuel.
		# en le remplaçant par DATA on tombe sur les données plus structurées
		request = Request(response.url.replace("TEXT", "DATA"), callback=self.parse_page_data)
		request.meta['item'] = item
		yield request

	def parse_page_data(self, response):
		selector = BeautifulSoup(response.body)
		item = response.meta['item']

		infos = selector.select("#docContent table tr")
		item['departement'] = ""
		item['numberOfBatch'] = 0
		item['reference'] = ""
		item['directUrl'] = []
		item['deliveryDate'] = ""
		for info in infos:
			key = info.select("th")[0].get_text()
			value = info.select("td")[1].get_text().encode("utf8")
			# sélection des textes en fonctions des clées
			if key == "TI":
				item['objet'] = "".join(value.split(":")[1:])
			elif key == "ND":
				item['technicalId'] = value
			elif key == "PD":
				item['publicationDate'] = value
			elif key == "TW":
				item['executionPlace'] = value
			elif key == "AU":
				item['entityName'] = value
			elif key == "DT":
				item['deliveryDate'] = value
			elif key == "NC":
				item['marketType'] = "".join(value.split(" - ")[1:]).strip()
			elif key == "PR":
				item['procedureType'] = "".join(value.split(" - ")[1:]).strip()
			elif key == "OC":
				regex = re.compile("[0-9]{8}")

				item['cpvCode'] = list(set(regex.findall(value)))
		return item