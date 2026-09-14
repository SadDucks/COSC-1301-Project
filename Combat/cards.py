class card:
    # Creates the basic information for every card
    def __init__(self, name, image):
        self.name = name
        self.image = image

    def __str__(self):
        return self.name

class attackCard(card):
    def __init__(self, name, image, damage, energyCost, health):
        super().__init__(name, image)
        self.damage = damage
        self.energy = energyCost
        self.health = health
        self.currentHealth = health


class supportCard(card):
    def __init__(self, name, image, damage, healing, energy):
        super().__init__(name, image)
        self.damage = damage
        self.healing = healing
        self.energy = energy