from dataclasses import dataclass
from typing import Optional  


from texasgpt._private.pydantic import BaseModel, ConfigDict
from texasgpt.core.poker.models import PlayerActionModel

class PokerActionRequest(BaseModel):
    """ModelRequest"""

    pocket_image: str = None
    public_image: str = None
    position: str = None
    starting_pot: str = None
    effective_stacks: str = None



class CreateTableRequest(BaseModel):  
    player_names: list  

class JoinTableRequest(BaseModel):  
    table_id: int
    is_bot: bool
    player_name: str  
    initial_cash : int = 1000

class StartPokerGameRequest(BaseModel):
    table_id: int


class Operation(BaseModel):  
    player_name: str  
    operation: str  

class TablePosition(BaseModel):  
    player_name: str  
    position: int  

class PlayActionRequest(BaseModel):
    table_id: int
    player_id: int
    player_action: PlayerActionModel
