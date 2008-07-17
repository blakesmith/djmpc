from twisted.application import internet, service
from twisted.internet import reactor, protocol, defer, utils
from twisted.protocols import basic

class FingerProtocol(basic.LineReceiver):
    def lineReceived(self, user):
        self.factory.getUser(user).addErrback(self.errBack).addCallback(self.callBack)

    def errBack(self, _):
        self.transport.write("Internal error in server\r\n")
        self.transport.loseConnection()

    def callBack(self, m):
        self.transport.write(m+"\r\n")
        self.transport.loseConnection()

class FingerFactory(protocol.ServerFactory):
    protocol = FingerProtocol

    def __init__(self, **kwargs):
        self.users = kwargs

    def getUser(self, user):
        return defer.succeed(self.users.get(user, "No such user"))

application = service.Application('finger', uid=1, gid=1)
factory = FingerFactory(moshez='Happy and well')
internet.TCPServer(79, factory).setServiceParent(service.IServiceCollection(application))
