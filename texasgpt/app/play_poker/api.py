from fastapi import APIRouter, HTTPException # type: ignore

from texasgpt._private.config import Config
from texasgpt.app.play_poker.request.request import CreateTableRequest, JoinTableRequest, StartPokerGameRequest, PlayActionRequest
from texasgpt.app.play_poker.request.response import PokerDealResponse, PokerTableModel, PokerRoundModel, PokerGameStateResponse
from texasgpt.app.openapi.api_view_model import Result
from texasgpt.component import ComponentType
from texasgpt.core.poker.poker_table import PokerTable, PokerRound


import logging

CFG = Config()
router = APIRouter()

tables = []  

@router.post("/v1/play_poker/create_table")
def create_table(request: CreateTableRequest):  
    poker_table = PokerTable(request.player_names)  
    tables.append(poker_table)  
    
    return {"success": True, "table_id": len(tables) - 1} 

@router.post("/v1/play_poker/join_table")
def join_table(request: JoinTableRequest):  
    if request.table_id >= len(tables) or request.table_id < 0:  
        raise HTTPException(status_code=404, detail="Table not found")  

    poker_table = tables[request.table_id]  
    success, message = poker_table.add_player(request.player_name, request.is_bot)  

    return {"success": success, "message": message}  


@router.post("/v1/play_poker/start_poker_game")
def start_poker_game(request: StartPokerGameRequest):
    table_id = request.table_id  
    if table_id >= len(tables) or table_id < 0:  
        raise HTTPException(status_code=404, detail="Table not found")  

    poker_table = tables[table_id]  
    round_instance = PokerRound(poker_table.players)  
    round_instance.deal_hole_cards()   
    players_hands = round_instance.get_players_hands()   
    print("players_hands", players_hands)
    poker_table.current_round = round_instance  # 保存当前轮到桌子实例中  

    # 示范将游戏的信息封装为返回数据  
    table_model = PokerTableModel(**poker_table.to_dict())  
    round_model = PokerRoundModel(**round_instance.to_dict())    
    deal_response = PokerDealResponse(
        table_info=table_model,
        round_info=round_model,
    )
    
    return Result.succ(deal_response)


@router.get("/v1/play_poker/get_game_state")
def get_game_state(table_id: int):  
    if table_id >= len(tables) or table_id < 0:  
        raise HTTPException(status_code=404, detail="Table not found")  

    poker_table = tables[table_id]  
    current_game = poker_table.current_round
    if not current_game:
        return Result.failed(msg="Poker game is not started")

    round_model = PokerRoundModel(**current_game.to_dict())
    game_state_response = PokerGameStateResponse(
        round_info=round_model
    )

    return Result.succ(game_state_response)


@router.post("/v1/play_poker/player_action")
def playerAction(request: PlayActionRequest):
    print(f"play_action,", request)
    try:
        action = request.player_action.action
        amount = request.player_action.amount

        if request.table_id >= len(tables) or request.table_id < 0:  
            raise HTTPException(status_code=404, detail="Table not found")  

        poker_table = tables[request.table_id] 
        current_game = poker_table.current_round

        player = current_game.players[request.player_id]
        print(f"player,", player)

        if action == action.BET:   
            player.bet(amount)  
            current_game.pot += amount

        elif action == action.CALL:  
            player.call(amount)  
            current_game.pot += amount

        elif action == action.RAISE:  
            min_raise = max(p.current_bet for p in current_game.players) - player.current_bet
            player.raise_bet(min_raise, amount)
            current_game.pot += amount

        elif action == action.CHECK:  
            to_call = max(p.current_bet for p in current_game.players) - player.current_bet  
            if to_call > 0:  
                raise HTTPException(status_code=406, detail="Invalid check")  
            player.check()  

        elif action == action.FOLD:  
            player.fold()  

        elif action == action.ALL_IN:  
            print("ALL IN action")
            amount = player.cash
            player.all_in_bet()  
            current_game.pot += amount
        else:
            print("Invalid action")

        # 更新游戏状态  
        print(f"play_action,", player.name, action, amount)
        current_game.update_game_state(player, action, amount)  

        return Result.succ("action successful")
      
    except Exception as e:
        return Result.failed(code="E0002", msg=f"poker action failed {e}")



# @router.post("/v1/play_poker/action")
# async def poker_action(request: PokerActionRequest):
#     print(f"/v1/poker_action")
#     # logging.error(f"pocket_image:{request.pocket_image}")
#     try:
        
#         pocket_image = request.pocket_image 
#         public_image = request.public_image  
#         position = request.position 
#         starting_pot = request.starting_pot
#         effective_stacks = request.effective_stacks 

#         from texasgpt.core.ai_assist.img_assist import AIPoker
#         res = AIPoker(public_image, position, starting_pot, effective_stacks)  
#         print(res)

#         return Result.succ(res)
      
#     except Exception as e:
#         return Result.failed(code="E000X", msg=f"analysis failed {e}")