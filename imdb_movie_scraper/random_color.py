from random import choice

class RandomColor:
    def __init__(self):
        self.color = [
            "red darken-1","pink darken-1","purple darken-1","deep-purple darken-1",
            "indigo darken-1","blue darken-1","light-blue darken-1","cyan darken-1",
            "teal darken-1","green darken-1","light-green darken-1","lime darken-1",
            "yellow darken-1","amber darken-1","orange darken-1","deep-orange darken-1",
            "brown darken-1","grey darken-1", "blue-grey darken-1"
        ]
        self.color_selected = self.random_color()

    def random_color(self):
        color_choice = choice(self.color)
        return color_choice