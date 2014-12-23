
import xapian
import sys
import string
import os 

import utilsXapian


""" Classe permettant l'indexation de fichier xapian."""
class IndexationXapian:


	# Initialise l'indexation avec le chemin de la base de donnees Xapian.
	def __init__(self):
		try:
			self.extract  = utilsXapian.Extract()
			self.indexer  = xapian.TermGenerator()
			stemmer       = xapian.Stem("french")
			self.indexer.set_stemmer(stemmer)
			self.fichier  = ""
			self.database = xapian.WritableDatabase()

		except Exception, e:
			print >> sys.stderr, "Exception: %s" % str(e)
			sys.exit(1)	


	def open(self):
		try:
			db = self.extract.xapianDatabase() 	# Retrieve database path.
			self.database = xapian.WritableDatabase(db, xapian.DB_CREATE_OR_OPEN)
			self.indexer.set_database(self.database)
			self.indexer.set_flags(xapian.TermGenerator.FLAG_SPELLING)	

		except Exception, e:
			print >> sys.stderr, "Exception: %s" % str(e)
			sys.exit(1)


	def close(self):
		self.database.close()


	def indexation(self, text):
		doc = xapian.Document()
		doc.set_data(text)
		self.indexer.set_document(doc)

		self.indexer.index_text(text)
		pid = self.database.add_document(doc)

		self.extract.closeFile
		os.system("rm " + self.extract.getFileName())

		return pid


	# Fonction permettant d'indexer un document pdf.
	# Le parametre filePath correspond au path reel du fichier a indexer.
	# Le parametre fileName correspond au path/nom du fichier qu'on retrouvera dans la base de donnee.
	def index(self, filePath, fileName):
		text = self.getText(filesPath, fileName) # On recupere le texte.
		if text == -1:				   			 # Si on a pas reussi a recuperer le texte
			return                    			 # On passe au suivant.
		self.open()                  			 # On ouvre la base de donnees.
		pid = self.indexation(text)  			 # On indexe le texte.
		self.closeFile                 			 # On ferme la base de donnees.

		return pid					   			 # On retourne le pid du document indexe.


	def getText(self, filePath, fileName):
		# Si le fichier n'existe pas, on passe au suivant.
		if not os.path.exists(filePath):
			print "Warning : " + filePath + " not exist."
			return -1

		# Si le fichier est vide, on passe au suivant.
		if os.path.getsize(filePath) <= 0:
			print "Warning : " + filePath + " is empty."
			return -1

		if filePath.find(".html") !=-1:
			allText = self.extract.extractText(filePath, "html")
		elif filePath.find(".pdf") !=-1:		
			allText = self.extract.extractText(filePath, "pdf")
		else:
			# Si le fichier n'est pas un fichier html ou pdf,
			# On passe au suivant.
			print "Warning : " + filePath + " is not a pdf or html file."
			return -1

		text = "url="+fileName + "\n"
		text += "sample="

		for line in allText:
			text += line	

		return text	

	def indexAll(self, filesPath, filesNameList):
		pid = {}
		self.open()
		for _file in filesNameList:
			text = self.getText(filesPath+_file, _file)	# On recupere le texte.
			if text != -1:
				pid[self.indexation(text)] = _file			# On indexe le texte.
		self.close()
		return pid


	# Fonction permettant de desindexer un document pdf.
	def deindexOnePdf(self,pid):
		try:
			self.open()
			self.database.delete_document(int(pid))
		except Exception, e:
				print >> sys.stderr, "Erreur: %s" % str(e)
		finally:
			self.close()
