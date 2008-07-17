from twisted.web import client
import tempfile

def downloadToTempFile(url):
    """Given a url, returns a deferred that will be called back with the name of a temporary file containing the downloaded data."""
    tmpfd, tempfilename = tempfile.mkstemp()
    os.close(tmpfd)
    return client.downloadPage(url, tempfilename).addCallback(returnFilename, tempfilename)

def returnFilename(result, filename):
    return filename

if __name__ == "__main__":
    import sys, os
    from twisted.internet import reactor

    def printFile(filename):
        for line in file(filename, 'r+b'):
            sys.stdout.write(line)
        os.unlink(filename) #delete file once we're done with it.
        reactor.stop()

    def printError(failure):
        print >> sys.stderr, "Error:", failure.getErrorMessage()
        reactor.stop()

    if len(sys.argv) == 2:
        url = sys.argv[1]
        downloadToTempFile(url).addCallback(printFile).addErrback(printError)
        reactor.run()
    else:
        print "Usage: %s <URL>" % sys.argv[0]
