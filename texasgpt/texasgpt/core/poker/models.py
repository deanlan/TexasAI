from texasgpt._private.pydantic import BaseModel
from enum import Enum, auto
from typing import Optional, List, Dict


class PokerCardModel(BaseModel):  
    suit: str  
    value: str  

class PokerDeckModel(BaseModel):  
    cards: List[PokerCardModel]  


class PokerPlayerAction(str, Enum):  
    FOLD = "FOLD"  
    CHECK = "CHECK"  
    CALL = "CALL"  
    BET = "BET"  
    RAISE = "RAISE"  
    ALL_IN = "ALL_IN"  

class PlayerActionModel(BaseModel):  
    action: PokerPlayerAction  
    amount: int = 0  


class PlayerActionHistoryStageModel(BaseModel):
    pre_flop: List[PlayerActionModel] = []
    flop: List[PlayerActionModel] = []
    turn: List[PlayerActionModel] = []
    river: List[PlayerActionModel] = []

class PlayerActionHistoryModel(BaseModel):
    player_action_history: Dict[str, PlayerActionHistoryStageModel]

class PokerPlayerModel(BaseModel):  
    name: str  
    hand: List[PokerCardModel]  
    cash: int  
    current_bet: int  
    folded: bool  
    all_in: bool  
    has_played: bool
    texas_position: str  

class PokerRoundModel(BaseModel):  
    players: List[PokerPlayerModel]  
    deck: PokerDeckModel  
    community_cards: List[PokerCardModel]  
    texas_positions: Dict[str, PokerPlayerModel]
    current_state: str
    winners: List[PokerPlayerModel] 
    player_action_history: PlayerActionHistoryModel 
    round_id: str  
    pot: int

class PokerTableModel(BaseModel):  
    players: List[PokerPlayerModel]  
    table_id: str  
    current_round: Optional[PokerRoundModel]