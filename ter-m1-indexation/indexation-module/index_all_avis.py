# -*- coding: utf-8 -*-
import sys,os
import ConfigParser
import MySQLdb as mdb
import datetime
import indexationXapian

# Classe permettant d'indexer tous les avis qui ne le sont pas.
class IndexAll:

	# Connection with database.
	def __init__(self):
		try:
			config = ConfigParser.RawConfigParser()
			config.read("/".join(os.path.abspath(__file__).split("/")[:-1]) + '/conf.ini')

			host = config.get('database', 'DB_HOST')
			user = config.get('database', 'DB_USER')
			pwd  = config.get('database', 'DB_PWD')
			name = config.get('database', 'DB_NAME')			

			db = mdb.connect(host, user, pwd, name)
			self.cur = db.cursor(mdb.cursors.DictCursor)

			self.ind  = indexationXapian.IndexationXapian()
			self.path = config.get('xapian','pdf') 

		except Exception, e:
			print >> sys.stderr, "Exception: %s" % str(e)
			sys.exit(1)	


	def indexAllAvis(self):
		try:
			
			requete =  " SELECT DISTINCT textName"
			requete += " FROM avis "
			requete += " WHERE avis.inserted > NOW()-INTERVAL 1 DAY" #
			requete += " and avis.fileId is null"     		      # On prend les avis non indexes ;
			requete += " and avis.doublon = 0"  		      # que ne sont pas des doublons ;
			requete += " and avis.endDate > NOW()"      # et qui ne correspondent pas a des vieux avis.

			self.cur.execute(requete)
			rows = self.cur.fetchall()

			files = []

			for row in rows:
				files.append(row['textName'])

			print "Il y a "+str(len(files))+ " fichier a indexer."
			result = self.ind.indexAll(self.path, files)
			print str(len(result)) + " on été indexés."

			for pid, name in result.items():
				self.cur.execute("UPDATE avis SET fileId=%s WHERE textName=%s", (pid, name))

		except Exception, e:
			print >> sys.stderr, "Exception: %s" % str(e)
			sys.exit(1)

if __name__ == "__main__":
	ind = IndexAll()
	ind.indexAllAvis()