class Command(object):
    def __init__(self):
        self.success = "The command worked! But you didn't specify a success action."
        self.failure = "Please try again!"

    def success_msg(self):
        return self.success

    def failure_msg(self):
        return self.failure
