class CommandParser(object):

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
