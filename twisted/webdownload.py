from twisted.web import client

class HTTPProgressDownloader(client.HTTPDownloader):
    def gotHeaders(self, headers):
        if self.status == '200':
            if headers.has_key('content-length'):
                self.totalLength = int(headers['content-length'][0])
            else:
                self.totalLength = 0
            self.currentLength = 0.0
            print ''
        return client.HTTPDownloader.gotHeaders(self, headers)

    def pagePart(self, data):
        if self.status == '200':
            self.currentLength += len(data)
            if self.totalLength:
                percent = "%i%%" % ((self.currentLength/self.totalLength)*100)
            else:
                percent = '%dK' % (self.currentLength/1000)
                print "\033[1FProgress: " + percent
        return client.HTTPDownloader.pagePart(self, data)

def downloadWithProgress(url, file, contextFactory=None, *args, **kwargs):
    scheme, host, port, path = client._parse(url)
    factory = HTTPProgressDownloader(url, file, *args, **kwargs)
    if scheme == 'https':
        from twisted.internet import ssl
        if contextFactory is None:
            contextFactory = ssl.ClientContextFactory()
        reactor.connectSSL(host, port, factory, contextFactory)
    else:
        reactor.connectTCP(host, port, factory)
    return factory.deferred

if __name__ == "__main__":
    import sys
    from twisted.internet import reactor

    def downloadComplete(result):
        print "Download Complete."
        reactor.stop()

    def downloadError(failure):
        print "Error:", failure.getErrorMessage()
        reactor.stop()

    url, outputFile = sys.argv[1:]
    downloadWithProgress(url, outputFile).addCallback(downloadComplete).addErrback(downloadError)
    reactor.run()
