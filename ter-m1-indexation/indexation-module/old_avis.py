
import sys,os
import ConfigParser
import MySQLdb as mdb
import datetime
import indexationXapian

# Classe permettant de desindexer de la base de donnees les vieux avis.
class OldAvis:

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

			self.ind = indexationXapian.IndexationXapian()

		except Exception, e:
			print >> sys.stderr, "Exception: %s" % str(e)
			sys.exit(1)	


	def deindexOldAvis(self):
		try:
			requete =  " SELECT DISTINCT avis.fileId, avis.id"
			requete += " FROM avis "
			requete += " WHERE avis.fileId is not null AND ((avis.endDate < NOW()) OR (avis.doublon=1))"

			self.cur.execute(requete)
			rows = self.cur.fetchall()
			
			for row in rows:
				if row['fileId'] != None:
					self.ind.deindexOnePdf(row['fileId'])
					self.cur.execute("UPDATE avis SET avis.fileId=null WHERE avis.id="+str(row['id']))

		except Exception, e:
			print >> sys.stderr, "Exception: %s" % str(e)
			sys.exit(1)

if __name__ == "__main__":
	odl = OldAvis()
	old.deindexOldAvis()