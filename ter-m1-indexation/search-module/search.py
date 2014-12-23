#!/usr/bin/env python
#
# Search in a database.
#

import sys
import xapian
    
# Start script with : python search.py PATH_TO_DATABASE PAGE NB_RESULT SEARCH
if len(sys.argv) < 5:
    print >> sys.stderr, "Usage: python %s PATH_TO_DATABASE PAGE NB_RESULT SEARCH" % sys.argv[0]
    sys.exit(1)

try:
    # Open the database for searching.
    database = xapian.Database(sys.argv[1])
    page     = int(sys.argv[2]) -1
    nbResult = int(sys.argv[3])

    # Start an enquire session.
    enquire = xapian.Enquire(database)

    # Combine the rest of the command line arguments with spaces between
    # them, so that simple queries don't have to be quoted at the shell
    # level.
    query_string = str.join(' ', sys.argv[4:])

    # Parse the query string to produce a Xapian::Query object.
    qp = xapian.QueryParser()
    stemmer = xapian.Stem("french")
    qp.set_stemmer(stemmer)
    qp.set_database(database)
    qp.set_stemming_strategy(xapian.QueryParser.STEM_SOME)

    query = qp.parse_query(query_string, qp.FLAG_SPELLING_CORRECTION|qp.FLAG_BOOLEAN|qp.FLAG_LOVEHATE|qp.FLAG_PHRASE)

    enquire.set_query(query)

    # Find the top 10 results for the query.
    matches = enquire.get_mset(page*nbResult, nbResult)
    
    sug = qp.get_corrected_query_string() + "[separatorSug]"
    print sug

    print str(matches.get_matches_estimated()) + "[separatorNb]"

    # Display the results.
    for m in matches:
        separatorAvis    = "[separatorAvis]"
        separatorInfo    = "[separatorInfo]"
        percent          = m.percent
        documentInfo     = m.document.get_data()

        debutURL         = documentInfo.find('url=')
        finURL           = documentInfo.find('.pdf')
        url              = documentInfo[debutURL+4:finURL] 

        debutResume      = documentInfo.find('sample=')
        resume           = documentInfo[debutResume+7:]

        print "%s%% %s %s.pdf %s %s %s" % (percent, separatorInfo, url, separatorInfo, resume, separatorAvis)

except Exception, e:
    print >> sys.stderr, "Exception: %s" % str(e)
    sys.exit(1)