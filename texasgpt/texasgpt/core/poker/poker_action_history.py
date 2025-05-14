from texasgpt.core.poker.models import PlayerActionModel, PlayerActionHistoryStageModel


class PlayerActionHistory():
    def __init__(self):
        self.player_action_history = {}  

    def to_dict(self):  
        return {  
            player_name: PlayerActionHistoryStageModel(  
                pre_flop=history.get("pre-flop", []),  
                flop=history.get("flop", []),  
                turn=history.get("turn", []),  
                river=history.get("river", [])  
            ).dict()  
            for player_name, history in self.player_action_history.items()  
        }  
    
    def update_action(self, player, action, amount, stage):  
        if player.texas_position not in self.player_action_history:  
            self.player_action_history[player.texas_position] = {  
                "pre-flop": [],  
                "flop": [],  
                "turn": [],  
                "river": []  
            }  

        action_model = PlayerActionModel(action=action, amount=amount)  
        self.player_action_history[player.texas_position][stage].append(action_model)