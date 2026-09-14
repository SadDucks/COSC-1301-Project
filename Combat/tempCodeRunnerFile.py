class card:
    # Creates the basic information for every card
    def __init__(self, name, image):
        self.name = name
        self.image = image

    def __str__(self):
        return self.name
