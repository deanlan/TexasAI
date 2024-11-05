from texasgpt.core.poker.poker_deck import PokerCard
from texasgpt.core.poker.models import PokerPlayerModel, PokerCardModel
import random  



class PokerPlayer():  
    def __init__(self, name, initial_cash):  
        self.name = name  
        self.hand = []  
        self.cash = initial_cash  
        self.current_bet = 0  
        self.folded = False  
        self.all_in = False  
        self.has_played = False  
        self.texas_position = "" # 德州的位置 BTN/SB/BB/UTG//

    def to_dict(self):  
      return {  
            "name": self.name,  
            "hand": [PokerCardModel(**card.to_dict()) for card in self.hand],  
            "cash": self.cash,  
            "current_bet": self.current_bet,  
            "folded": self.folded,  
            "all_in": self.all_in,  
            "has_played": self.has_played,  
            "texas_position": self.texas_position,
        }  
    def receive_cards(self, cards):  
        self.hand.clear()
        self.hand.extend(cards)  
          
    def check(self):  
        self.current_bet = 0
        self.has_played = True  
        print(f"{self.name} checks") 

    def bet(self, amount):  
        if self.current_bet > amount or amount > self.cash:  
            raise ValueError("Invalid bet amount {amount}")  
        self.current_bet = amount  
        self.cash -= amount  
        self.has_played = True

    def call(self, amount):  
        if amount < self.current_bet or amount > self.cash:  
            raise ValueError("Invalid call amount {amount}")  
        self.current_bet = amount  
        self.cash -= amount  
        self.has_played = True

    def check_hand(self):  
        return sorted(self.hand, key=lambda card: (PokerCard.values.index(card.value), PokerCard.suits.index(card.suit)))  

    def fold(self):  
        print("fold in action")
        self.folded = True  
        self.has_played = True
    
    def all_in_bet(self):  
        print("all in action")
        self.current_bet += self.cash  
        self.cash = 0  
        self.all_in = True  
        self.has_played = True

    def raise_bet(self, min_raise, amount):  
        if amount <= min_raise or amount > self.cash:  
            raise ValueError(f"Invalid raise amount {amount}")  
        self.current_bet += amount  
        self.cash -= amount  
        self.has_played = True  

    def reset_for_new_round(self):  
        self.hand = []  
        self.current_bet = 0  
        self.folded = False  
        self.all_in = False
        self.has_played = False  

class PokerBot(PokerPlayer):  

    def __init__(self, name, initial_cash):  
        super().__init__(name, initial_cash)  

    def decide_action(self, amount):  
        actions = ['CALL']  
        bot_action = random.choice(actions)
        bot_amount = amount 
        if bot_action == "ALL_IN":
            bot_amount = self.cash 
        elif bot_action == "CALL":
            pass

        return bot_action, bot_amount
            
      
    def raise_amount(self, min_raise):  
        return random.randint(min_raise, self.cash)  