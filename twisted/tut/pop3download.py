from twisted.mail import pop3client
from twisted.internet import reactor, protocol, defer
from cStringIO import StringIO
import email

class POP3DownloadProtocol(pop3client.POP3Client):
    allowInsecureLogin = True

    def serverGreeting(self, greeting):
        pop3client.POP3Client.serverGreeting(self, greeting)
        login = self.login(self.factory.username, self.factory.password)
        login.addCallback(self._loggedIn)
        login.chainDeferred(self.factory.deferred)
