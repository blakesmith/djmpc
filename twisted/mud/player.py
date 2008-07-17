class Player(object):

    def __init__(self):
        """Initializes all the attributes of a new player instance"""
        self.body = self.body()
        self.inventory = self.inventory()

    class body:
        def __init__(self):
            self.max_health, self.health = {"hp": 75, "sp": 75, "ep": 75}

        def get_health(self):
            return self.health

    class inventory:
        def __init__(self):
            self.max_spaces = 10
            self.spaces = 0

