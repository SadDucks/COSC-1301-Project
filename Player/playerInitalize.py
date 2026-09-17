


class playerInitialize:
    def __init__(self, playerNumber=4):
        for i in range(1, playerNumber + 1):

            playerArray = []
            setattr(self, f"player{i}", playerArray)

        self.player1.append("test")
        print(self.player1[0]);
