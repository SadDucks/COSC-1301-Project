import cards as cards
import json

with open("items/attack.json", "r") as file:
    attackCards = json.load(file)

attackCardList = []

for card in attackCards:
    newCard = cards.attackCard(
        card["id"],
        card["name"],
        card["image"],
        card["attack"],
        card["energy"],
        card["health"]
    )
    attackCardList.append(newCard)




#Link = attackCard("Link", "IMAGE", 15, 5, 50)
#Gannondorf = attackCard("Gannondorf", "IMAGE", 15, 5, 50)
#Zelda = attackCard("Zelda", "IMAGE", 20, 5, 25)
#Calamo = attackCard("Calamo", "IMAGE", 5, 2, 10)

#healing_potion = supportCard("Healing Potion", "IMAGE", 0, 25, 3)
#energy_potion = supportCard("Energy Potion", "IMAGE", 0, 0, -5)