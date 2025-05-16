from texasgpt._private.pydantic import BaseModel, Field
from typing import List, Dict, Optional
from texasgpt.core.poker.models import PokerTableModel, PokerRoundModel, PokerCardModel



class PokerDealResponse(BaseModel):
    """"""
    table_info: Optional[PokerTableModel]  
    round_info: Optional[PokerRoundModel]


class PokerGameStateResponse(BaseModel):
    round_info: Optional[PokerRoundModel]