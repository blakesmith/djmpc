from twisted.web import client
from twisted.internet import reactor
import sys

def printPage(data):
    print data
    reactor.stop()

def printError(failure):
    print >> sys.stderr, "Error:", failure.getErrorMessage()
    reactor.stop()

if len(sys.argv) == 2:
    url = sys.argv[1]
    client.getPage(url).addCallback(printPage).addErrback(printError)
    reactor.run()
else:
    print "Usage: webcat.py <url>"
