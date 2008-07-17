from twisted.protocols import basic
from twisted.internet import protocol, reactor

class HttpEchoProtocol(basic.LineReceiver):
    def __init__(self):
        self.lines = []
        self.gotRequest = False

    def lineReceived(self, line):
        self.lines.append(line)
        if not line and not self.gotRequest:
            self.sendResponse()
            self.gotRequest = True

    def sendResponse(self):
        responseBody = "You said:\r\n\r\n" + "\r\n".join(self.lines)
        self.sendLine("HTTP/1.0 200 OK")
        self.sendLine("Content-Type: text/plain")
        self.sendLine("Content-Length: %i" % len(responseBody))
        self.sendLine("")
        self.transport.write(responseBody)
        self.transport.loseConnection()

f = protocol.ServerFactory()
f.protocol = HttpEchoProtocol
reactor.listenTCP(8000, f)
reactor.run()
