from twisted.internet import reactor, protocol
from twisted.protocols import basic
import sys
from user.startup import *

sys.path.append('/home/blake/projects/python/twisted/mud')

class EchoProtocol(basic.LineReceiver):
    def lineReceived(self, line):
        if line == 'quit':
            self.sendLine("Goodbye.")
            self.transport.loseConnection()
        else:
            cmd = "%s.%s" % ('command', line)
            try:
                importer = __import__(cmd, globals(), locals(), line)
                class_pointer = getattr(importer, line.capitalize())
                sendcmd = class_pointer()
                self.sendLine(sendcmd.success_msg())
            except:
                self.sendLine("Please try again!")

    def connectionMade(self):
        self.sendLine(startup())

class EchoServerFactory(protocol.ServerFactory):
    protocol = EchoProtocol

if __name__ == "__main__":
    port = 5001
    reactor.listenTCP(port, EchoServerFactory())
    reactor.run()
