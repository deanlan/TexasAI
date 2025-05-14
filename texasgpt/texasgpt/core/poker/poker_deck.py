import random
from  texasgpt.core.poker.models import PokerCardModel


class PokerCard():  
    suits = ['H', 'D', 'C', 'S']  
    values = list(range(2, 10)) + ['T', 'J', 'Q', 'K', 'A']  

    def __init__(self, suit, value):  
        if suit not in self.suits or value not in self.values:  
            raise ValueError("Invalid card")  
        self.suit = suit  
        self.value = value  

    def __str__(self):  
        return f"{self.value}{self.suit}"  

    def __repr__(self):  
        return self.__str__()  
    
    def to_dict(self):  
        return {  
            "suit": self.suit, 
            "value": str(self.value)
        }  


class PokerDeck():  
    def __init__(self):  
        self.cards = [PokerCard(suit, value) for suit in PokerCard.suits for value in PokerCard.values]  
        random.shuffle(self.cards)  

    def draw(self, num_of_cards=1):  
        drawn_cards = self.cards[:num_of_cards]  
        self.cards = self.cards[num_of_cards:]  
        return drawn_cards  

    def to_dict(self):  
        return {  
            "cards": [PokerCardModel(**card.to_dict()) for card in self.cards],  
        }