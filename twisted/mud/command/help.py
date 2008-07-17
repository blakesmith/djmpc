from command import Command

class Help(Command):
    def __init__(self):
        self.success = "Basic help menu"
        self.failure = "The help files failed to load"
