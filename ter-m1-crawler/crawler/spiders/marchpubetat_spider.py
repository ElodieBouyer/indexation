# -*- coding: utf-8 -*- 
#https://www.marches-publics.gouv.fr/index.php5?page=entreprise.EntrepriseAdvancedSearch&AllCons
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy import log

from datetime import datetime
from bs4 import BeautifulSoup
from scrapy.http import FormRequest
from crawler.items import CrawlerItem
import datetime
import re

class MarchpubetatSpider(CrawlSpider):
	name = "marchpubetat"
	allowed_domains = ["marches-publics.gouv.fr"]
	start_urls = ['https://www.marches-publics.gouv.fr/index.php5?page=entreprise.EntrepriseAdvancedSearch&AllCons']
	download_delay = 0

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
		"""
		Cette fonction se charge de lancer la recherche des avis du jour.
		"""
		today = self.date.strftime('%d/%m/%Y')

		selector = Selector(response)
		prado = selector.xpath('//input[@name="PRADO_PAGESTATE"]/@value').extract()

		yield FormRequest("https://www.marches-publics.gouv.fr/index.php5?page=entreprise.EntrepriseAdvancedSearch&searchAnnCons",
			#formname='main_form',
			formdata={
			'PRADO_PAGESTATE':prado[0],
			'PRADO_POSTBACK_TARGET':'ctl0$CONTENU_PAGE$AdvancedSearch$lancerRecherche',
			'PRADO_POSTBACK_PARAMETER':'undefined',
			'ctl0$menuGaucheEntreprise$quickSearch':'Recherche rapide',
			'ctl0$CONTENU_PAGE$AdvancedSearch$orgNameAM':'',
			'ctl0$CONTENU_PAGE$AdvancedSearch$reference':'',
			'ctl0$CONTENU_PAGE$AdvancedSearch$procedureType':'0',
			'ctl0$CONTENU_PAGE$AdvancedSearch$categorie':'0',
			'ctl0$CONTENU_PAGE$AdvancedSearch$clauseSociales':'0',
			'ctl0$CONTENU_PAGE$AdvancedSearch$ateliersProteges':'0',
			'ctl0$CONTENU_PAGE$AdvancedSearch$clauseEnvironnementale':'0',
			'ctl0$CONTENU_PAGE$AdvancedSearch$idsSelectedGeoN2':'',
			'ctl0$CONTENU_PAGE$AdvancedSearch$idAtexoRef$UrlRef':'/atexo.referentiels/referentiel.jsp?&clef=ctl0_CONTENU_PAGE_AdvancedSearch_idAtexoRef&locale=fr&cheminFichierConfigXML=/ressources/referentiels-new/cpv-config.xml&urlBase=https://mpe3-docs.local-trust.com&styleCSS=https://www.marches-publics.gouv.fr/themes/cpv/css/cpv.css',
			'ctl0$CONTENU_PAGE$AdvancedSearch$idAtexoRef$casRef':'cas6',
			'ctl0$CONTENU_PAGE$AdvancedSearch$idAtexoRef$codeRefPrinc':'',
			'ctl0$CONTENU_PAGE$AdvancedSearch$idAtexoRef$codesRefSec':'',
			'ctl0$CONTENU_PAGE$AdvancedSearch$idAtexoRef$defineCodePrincipal':'(Code principal)',
			'ctl0$CONTENU_PAGE$AdvancedSearch$dateMiseEnLigneStart':'',
			'ctl0$CONTENU_PAGE$AdvancedSearch$dateMiseEnLigneEnd':'',
			'ctl0$CONTENU_PAGE$AdvancedSearch$dateMiseEnLigneCalculeStart': today,
			'ctl0$CONTENU_PAGE$AdvancedSearch$dateMiseEnLigneCalculeEnd': today,
			'ctl0$CONTENU_PAGE$AdvancedSearch$keywordSearch':'',
			'ctl0$CONTENU_PAGE$AdvancedSearch$rechercheFloue':'ctl0$CONTENU_PAGE$AdvancedSearch$floue',
			'ctl0$CONTENU_PAGE$AdvancedSearch$orgNamesRestreinteSearch':'0',
			'ctl0$CONTENU_PAGE$AdvancedSearch$refRestreinteSearch':'',
			'ctl0$CONTENU_PAGE$AdvancedSearch$accesRestreinteSearch':''
			},
			callback=self.parse_page_resultat)
	
	def parse_page_resultat(self, response):
		"""
			Cette fonction parse la page contenant les résultats.
		"""
		i = 0 # compteur de résultats, utilisé dans les sélecteurs
		html = response.body
		selector = Selector(response, type="html")

		


		# sélecteur pour identifier les lignes du tableau de résultat
		lines = selector.xpath('//div[@id="tabNav"]//table[@class="table-results"]/tr').extract()
		
		for line in lines:
			lineSelector = BeautifulSoup(line.encode("utf8"))

			# Sélection des informations récupérable sur cette page
			procedureType = lineSelector.select('div#typeProcedure_'+str(i)+'_fr')
			marketType = lineSelector.select('div#categorie_'+str(i)+'_fr')
			publicationDate = lineSelector.select('td')[1].select("div")

			consultation = lineSelector.select('div#consultation_'+str(i)+'_fr')
			reference = consultation[0].select("span#ctl0_CONTENU_PAGE_resultSearch_tableauResultSearch_ctl"+str(i+1)+"_langagesConsultations_ctl0_reference")
			intitule = consultation[0].select("div#ctl0_CONTENU_PAGE_resultSearch_tableauResultSearch_ctl"+str(i+1)+"_langagesConsultations_ctl0_infosIntitule")
			objet = consultation[0].select("div#ctl0_CONTENU_PAGE_resultSearch_tableauResultSearch_ctl"+str(i+1)+"_langagesConsultations_ctl0_infosObjet")

			acheteur = consultation[0].select("div.objet-line span")

			lieu = lineSelector.select('div#ctl0_CONTENU_PAGE_resultSearch_tableauResultSearch_ctl'+str(i+1)+'_langagesLieuxExecution_ctl0_ctl0_infosLieuExecution')
			lieu = re.sub(r' ?\(([^)]*)\)([^,]*)',r'\1',lieu[0].get_text().strip())

			endDate = lineSelector.select('td[headers="cons_dateEnd"] div:first')

			# création de l'objet avec les informations que nous avons pu récupérer.
			item = CrawlerItem()
			item["objet"] = objet[0].get_text().strip()
			item["entityName"] = acheteur[len(acheteur)-1].get_text().strip()
			item["publicationDate"] = datetime.datetime.strptime(publicationDate[len(publicationDate)-1].get_text().strip(), '%d/%m/%Y')
			item["deliveryDate"] = datetime.datetime.strptime(endDate[0].get_text().strip(), '%d/%m/%Y%H:%M')
			item["departement"] = lieu.replace(',',';')
			item["marketType"] = marketType[0].get_text().strip()
			item['reference'] = reference[0].get_text().strip()
			item["procedureType"] = procedureType[0].get_text().strip()

			url = lineSelector.select('div#ctl0_CONTENU_PAGE_resultSearch_tableauResultSearch_ctl'+str(i+1)+'_panelAction a')

			if "DetailConsultation" in url[0]['href']:
				request = Request("https://www.marches-publics.gouv.fr/" + url[0]['href'], callback=self.parse_item)
				request.meta['item'] = item
				yield request
			i = i+1

		# on vérifie s'il est possible d'aller à la page suivante. Si ce n'est pas possible, on s'arrête là.
		nextIsPresent = selector.css("#ctl0_CONTENU_PAGE_resultSearch_PagerTop_ctl2").extract()
		if len(nextIsPresent) == 0:
			return

		page = selector.css("#ctl0_CONTENU_PAGE_resultSearch_numPageTop").extract()
		page = page[0].split('value="')[1].split('"')[0]

		# on suit la pagination :
		prado = selector.xpath('//input[@name="PRADO_PAGESTATE"]/@value').extract()
		yield FormRequest.from_response(response,
			formname='main_form',
			formdata={'PRADO_PAGESTATE':prado[0],
			'PRADO_POSTBACK_TARGET':'ctl0$CONTENU_PAGE$resultSearch$PagerTop$ctl2',
			'PRADO_POSTBACK_PARAMETER':'undefined',
			'ctl0$menuGaucheEntreprise$quickSearch':'Recherche rapide',
			'ctl0$CONTENU_PAGE$resultSearch$listePageSizeTop':'10',
			'ctl0$CONTENU_PAGE$resultSearch$numPageTop':str(int(page)),
			'ctl0$CONTENU_PAGE$resultSearch$listePageSizeBottom':'10',
			'ctl0$CONTENU_PAGE$resultSearch$numPageBottom':str(int(page)),
			'ctl0$CONTENU_PAGE$resultSearch$messageViadeo':'',
			'ctl0$CONTENU_PAGE$resultSearch$urlMPE':'',
			'ctl0$CONTENU_PAGE$resultSearch$urlViadeo':''},
					callback=self.parse_page_resultat)

	def parse_item(self, response):
		item = response.meta['item']
		html = response.body
		selector = Selector(response, type="html")

		content = selector.css("#recap-consultation").extract()
		content = content[0]
		bsSelector = BeautifulSoup(content.encode("utf8"))

		
		nbLots = bsSelector.select('span#ctl0_CONTENU_PAGE_idEntrepriseConsultationSummary_nbrLots')
		nbLots = [int(s) for s in nbLots[0].get_text().split() if s.isdigit()]
		if len(nbLots) > 0:
			nbLots = nbLots[0]
		else: 
			nbLots = 0

		lieuExec = bsSelector.select('span#ctl0_CONTENU_PAGE_idEntrepriseConsultationSummary_lieuxExecutionSuite')
		lieuExec = lieuExec[0].get_text()

		
		cpv = bsSelector.select('span#ctl0_CONTENU_PAGE_idEntrepriseConsultationSummary_idAtexoRef_scriptRef script')
		cpv = [s for s in str(cpv[0]).split('"') if s.isdigit() and len(s) == 8]
		

		autreUrl = bsSelector.select('div#ctl0_CONTENU_PAGE_panelOnglet1 .form-field .form-bloc .content ul li a')
		autreUrl = [s['href'] for s in autreUrl if "http://" in s['href']]

		item['thisUrl'] = response.url
		item['directUrl'] = autreUrl
		item['cpvCode'] = cpv
		item['executionPlace'] = lieuExec
		item['numberOfBatch'] = nbLots
		item['technicalId'] = response.url.split("refConsultation=")[1].split("&")[0]

		for tag in bsSelector():
			if tag.get("style") and "none" not in tag.get("style"):
				del tag["style"]
			if tag.get('id') == "infosPrincipales":
				del tag["style"]
		
		item['text'] = str(bsSelector)
		
		return item