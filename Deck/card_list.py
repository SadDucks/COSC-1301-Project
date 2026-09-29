from Deck import cards;
import json;

# Creates Lists for each Card Type

attackCardList = [];
supportCardList = [];
prizeCardList = [];

# Pulls data from Json Database

with open("items/attack.json", "r") as attack:
    attackCards = json.load(attack);

with open("items/support.json", "r") as support:
    supportCards = json.load(support);

with open("items/prize.json", "r") as prize:
    prizeCards = json.load(prize);


# Adds cards from database to each list respectfully

for card in attackCards:
    newCard = cards.attackCard(
        card["id"],
        card["name"],
        card["image"],
        card["attack"],
        card["energy"],
        card["health"]
    );
    attackCardList.append(newCard);

for card in supportCards:
    newCard = cards.supportCard(
        card["id"],
        card["name"],
        card["image"],
        card["healing"],
        card["energy"]
    );
    supportCardList.append(newCard);

for card in prizeCards:
    newCard = cards.prizeCard(
        card["id"],
        card["name"],
        card["image"]
    );
    prizeCardList.append(newCard);