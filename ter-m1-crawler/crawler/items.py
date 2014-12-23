# -*- coding: utf-8 -*- 
# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class CrawlerItem(Item):
	entityName = Field(default="") #Nom de l’entité d’achat : exemple Communauté Urbaine Toulouse Métropole
	objet = Field(default="") #Intitulé de l'avis
	marketType = Field(default="") #Type de marchés : Travaux, fourniture ou services
	procedureType = Field(default="") #Type de la procédure : Adaptée, Appel d'Offres Ouvert , etc.
	executionPlace = Field(default="") #Lieu d’exécution de la prestation
	departement = Field(default="") #Lieu d’exécution de la prestation
	cpvCode = Field(default="") #Code CPV
	publicationDate = Field(default="") #Date de publication
	deliveryDate = Field(default="") #Date limite de remise des offres
	numberOfBatch = Field(default="") #Nombre de lots
	reference = Field(default="") #Référence de l’appel d’offre (donné par l’entité d’achat)
	text = Field(default="") #Texte intégral de l’annonce pour indexation
	technicalId = Field(default="") #Identifiant technique de l’appel d’offre (donnée par le site)
	directUrl = Field(default="") #URL du site d’accès direct à l’appel d’offre
	thisUrl = Field(default="") #Site sur lequel l’appel d’offre a été scraper