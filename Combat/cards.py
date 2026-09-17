class card:
    # Creates the basic information for every card
    def __init__(self, id, name, image):
        self.id = id
        self.name = name
        self.image = image

    def __str__(self):
        return self.name

class attackCard(card):
    def __init__(self, id, name, image, attack, energyCost, health):
        super().__init__(id, name, image)
        self.attack = attack
        self.energy = energyCost
        self.health = health
        self.currentHealth = health


class supportCard(card):
    def __init__(self, id, name, image, healing, energy):
        super().__init__(id, name, image)
        self.healing = healing
        self.energy = energy


class prizeCard(card):
    def __init__(self, id, name, image):
        super().__init__(id, name, image)