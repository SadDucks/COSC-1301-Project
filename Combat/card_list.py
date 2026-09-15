import cards as cards
import json

with open("items/attack.json", "r") as attack:
    attackCards = json.load(attack)

with open("items/support.json", "r") as support:
    supportCards = json.load(support)

attackCardList = []
supportCardList = []

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

for card in supportCards:
    newCard = cards.supportCard(
        card["id"],
        card["name"],
        card["image"],
        card["healing"],
        card["energy"]
    )
    supportCardList.append(newCard)

