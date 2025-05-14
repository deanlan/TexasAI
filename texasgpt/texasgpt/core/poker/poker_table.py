import uuid
from texasgpt.core.poker.poker_deck import PokerDeck
from texasgpt.core.poker.poker_player import PokerPlayer, PokerBot
from texasgpt.core.poker.models import PokerRoundModel, PokerCardModel, PokerPlayerModel, PokerDeckModel, PokerPlayerAction, PlayerActionHistoryModel
from texasgpt.core.poker.poker_action_history import PlayerActionHistory
from phevaluator import evaluate_cards

from typing import Optional, Tuple, List, Dict, Union



class PokerTable():  
    def __init__(self, player_names):  
        if len(player_names) < 1 or len(player_names) > 10:  
            raise ValueError("Invalid number of players")  
        initial_cash = 1000  
        self.players = [PokerPlayer(name, initial_cash) for name in player_names]  
        # self.positions = {i: player for i, player in enumerate(self.players)}
        self.table_id = uuid.uuid4()
        self.current_round = None

    def to_dict(self):  
        return {  
            "players": [PokerPlayerModel(**player.to_dict()) for player in self.players],   
            "table_id": str(self.table_id),  
            # "positions": {pos: PokerPlayerModel(**player.to_dict()) for pos, player in self.positions.items()},   
            "current_round": PokerRoundModel(**self.current_round.to_dict()) if self.current_round else None,  
        }  
    
    def add_player(self, player_name: str, is_bot: bool = False) -> Tuple[bool, str]:  
        if len(self.players) >= 10:  
            return False, "Table is full"  

        if any(player.name == player_name for player in self.players):  
            return False, "Player with this name already exists in the table"  
        
        if is_bot:
            new_player = PokerBot(player_name, initial_cash=1000)
        else:
            new_player = PokerPlayer(player_name, initial_cash=1000)  

        self.players.append(new_player)  

        return True, "Success"


class PokerRound():  
    def __init__(self, players):  
        if len(players) < 2 or len(players) > 10:  
            raise ValueError("Invalid number of players")   
        self.players = players
        self.deck = PokerDeck()  
        self.community_cards = []  
        self.current_state = "pre-flop"
        self.current_turn = 0
        self.round_id = uuid.uuid4()
        self.pot = 0
        self.texas_positions = {}
        self.winners = []
        self.player_action_history = PlayerActionHistory()
        self._init_game_round()
        

    def to_dict(self):  
        return {   
            "players": [PokerPlayerModel(**player.to_dict()) for player in self.players],  
            "deck": PokerDeckModel(**self.deck.to_dict()),  
            "current_state": self.current_state,
            "current_turn": self.current_turn,
            "community_cards": [PokerCardModel(**card.to_dict()) for card in self.community_cards],  
            "round_id": str(self.round_id),  
            "winners":  [PokerPlayerModel(**player.to_dict()) for player in self.winners],
            "texas_positions": {pos: PokerPlayerModel(**player.to_dict()) for pos, player in self.texas_positions.items()},  
            "pot": self.pot,  
             "player_action_history": PlayerActionHistoryModel(player_action_history = self.player_action_history.to_dict())
        }
    

    def _init_game_round(self):
        self._init_game_positions()
        self.community_cards = []  
        self.deck = PokerDeck()
        for player in self.players:
            player.reset_for_new_round()
        
    
    def _init_game_positions(self):
        if len(self.players) == 2:  
            texas_positions = ["BTN", "BB"]  
        elif len(self.players) == 3:  
            texas_positions = ["BTN", "SB", "BB"] 
        else:
            texas_positions = ["BTN", "SB", "BB", "UTG"] + [f"MP{i}" for i in range(1, len(self.players) - 3)]  

        for index, player in enumerate(self.players):  
            position_name = texas_positions[index % len(texas_positions)]  
            player.texas_position = position_name  
            self.texas_positions[position_name] = player  
  

    def deal_hole_cards(self):  
        for player in self.players:  
            print("player:", player.__dict__)
            player.receive_cards(self.deck.draw(2))  
            print(f"{player.name} 's hand is {player.hand}")

    def deal_community_cards(self, num_of_cards):  
        self.community_cards.extend(self.deck.draw(num_of_cards))  
        print(f"community cards: {self.community_cards}")  

    def flop(self):  
        self.current_state = "flop"
        self.deal_community_cards(3)  

    def turn(self):  
        self.current_state = "turn"
        self.deal_community_cards(1)  

    def river(self):
        self.current_state = "river"   
        self.deal_community_cards(1)  

  
    def get_players_hands(self):  
        return {player.name: player.to_dict() for player in self.players}  
    
    def update_game_state(self, player: PokerPlayer, action: PokerPlayerAction, amount: Optional[int] = None):
        print(f"update_game_state, play_action,", player.name, action, amount) 


        # 根据当前状态（pre-flop, flop, turn, river）添加到 player_action_history 中
        self.player_action_history.update_action(player, action, amount, self.current_state)


        # 更新当前玩家的状态  
        player_index = self.players.index(player)  
        next_position = (player_index + 1) % len(self.players)  
        print(f"next player is ", self.players[next_position] )

        remaining_players = [p for p in self.players if not p.folded] 
        all_in_players = [p for p in remaining_players if p.all_in] 

        if len(all_in_players)  == len(remaining_players):
            self.advance_to_next_stage()  
            return
        
        if len(remaining_players) == 1:
            self.current_state = "river"
            self.advance_to_next_stage()    
            return
          
        print(f"current_state", self.current_state)
        if self.all_players_played():  
            self.advance_to_next_stage()  
            return

        next_player = self.players[next_position]  
        # 判断下一个玩家是否需要跳过  
        while next_player.folded or next_player.all_in:  
            print(f"Skipping {next_player.name} due to fold or all_in.")  
            next_position = (next_position + 1) % len(self.players)  
            next_player = self.players[next_position]

        
        self.current_turn = next_position  
        print(f"Now it's {next_player.name}'s turn, id: {next_position}")  
        if isinstance(next_player, PokerBot):
            bot_action, bot_amount = next_player.decide_action(amount)
            print(f"bot_action", bot_action, bot_amount)
            if bot_action == "CALL":
                if bot_amount < player.current_bet:
                    print(f"error call amount")
                    return
                next_player.call(bot_amount)
                self.pot += bot_amount
                # elif bot_action == "FOLD":
                #     next_player.fold()
                # elif bot_action == "ALL_IN":
                #     next_player.all_in()
                
            self.update_game_state(next_player, bot_action, bot_amount)

    def all_players_played(self) -> bool:  

        active_players = [player for player in self.players if not player.folded]  
        bet_amounts = [player.current_bet for player in active_players]  
        all_played = all(player.has_played for player in self.players) 

        print(f"active_players", active_players)
        print(f"bet_amounts", bet_amounts)
        print(f"all_played", all_played)

        # all check 的情况
        if all_played and len(set(bet_amounts)) == 1 and bet_amounts[0] == 0:  
            return True  
        elif len(set(bet_amounts)) == 1 and bet_amounts[0] != 0:  
            return True  
        else:  
            return False  


    def advance_to_next_stage(self):  
        print(f"Now it's time to move to next stage, current_stage:", self.current_state)  
        self.reset_players_played_status()  
        self.current_turn = 0
    
        if self.current_state == "pre-flop":  
            self.flop()  
             
        elif self.current_state == "flop":  
            self.turn()  
              
        elif self.current_state == "turn":  
            self.river()  
            
        elif self.current_state == "river":  
            self.current_state = "end" 
            self.conclude_round()      
             

    def reset_players_played_status(self):  
        for player in self.players:  
            player.has_played = False  
            player.current_bet = 0
    
    def evaluate_hands(self):  
        print(f"Now it's time to evaluate_hands") 
    # Dictionary to store each player's hand ranking  
        player_rankings = {}  

        for player in self.players:  
            if not player.folded:  
            # Get evaluator friendly cards.  
                player_full_hand = player.hand + self.community_cards   
                print("player_full_hand", player_full_hand)
                cards_str_list = [str(card) for card in player_full_hand]
            # Rank of the best hand - lower is better.  
                rank = evaluate_cards(*cards_str_list)  
            # Store the player's hand ranking  
                player_rankings[player] = rank  

        print("players_ranking", player_rankings)

        return player_rankings  

    def conclude_round(self):  
        print("Conclue_round!")  
        active_players = [player for player in self.players if not player.folded] 
        if len(active_players) > 1:
            player_rankings = self.evaluate_hands()  
            # Find the highest hand rank and find all the players with the highest hand rank  
            min_rank = float('inf')  
            for player, rank in player_rankings.items():  
                if rank < min_rank:  
                    self.winners = [player]  
                    min_rank = rank  
                elif rank == min_rank:  
                    self.winners.append(player)

        else:
            # all fold
            self.winners = active_players

    # Split the pot among the winners  
        winnings = self.pot / len(self.winners)  
        for winner in self.winners:  
            winner.cash += winnings  
            print(f"{winner.name} has won ${winnings}!")  
 
        return