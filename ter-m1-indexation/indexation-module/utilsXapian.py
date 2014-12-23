
import subprocess
import sys
import os
import ConfigParser

# Cette classe extrait des donnees textes provenant d'un pdf.
class Extract:

	def __init__(self):
		self.file_name = ""
		self.fichier = ""


	# Fonction permettant de recuperer le path de la BD Xapian.
	def xapianDatabase(self):	
		try:
			# On ouvre le fichir de config.
			config = ConfigParser.RawConfigParser()
			config.read("/".join(__file__.split("/")[:-1]) + '/conf.ini')

			db = config.get('xapian', 'database')

			# On supprime les espaces.
			db = db.replace(' ','')

			return db
		except Exception, e:
			print "Error: %s" % str(e)
			sys.exit(1)
			

	def openFile(self):
		self.fichier = open(self.file_name, "r")

	def closeFile(self):
		self.fichier.close()

	def getFileName(self):
		return self.file_name

	def extractText(self, fileName, type):
		if type == "html":
			args = ["html2text"]
		else:
			args = ["pdftotext"]

		try:
			args += ["-enc", "UTF-8",fileName] 
			subprocess.check_output(args)

			self.file_name = fileName 
			self.file_name = '.'.join(self.file_name.split('.')[:-1])
			self.file_name += ".txt" 

			self.openFile()

			allText = self.fichier.readlines()

			return allText

		except Exception, e:
			print "Error: %s" % str(e)
			sys.exit(1)