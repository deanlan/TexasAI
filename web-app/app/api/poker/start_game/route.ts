import { NextRequest, NextResponse } from "next/server";
import fetch from "node-fetch";

interface Card {
    suit: string;
    value: string;
}

interface PlayerData {
    name: string;
    hand: Card[];
    cash: number;
    current_bet: number;
    folded: boolean;
    all_in: boolean;
    has_played: boolean;
    texas_position: string;
}

interface ApiResponse {
    success: boolean;
    err_code: string | null;
    err_msg: string | null;
    data: {
        table_info: {
            players: PlayerData[];
            table_id: string;
            current_round: Record<string, unknown>;
        };
        round_info: {
            players: PlayerData[];
            // deck: Record<string, unknown>;
            community_cards: string[];
            round_id: string;
            pot: number;
            current_state: string;
            current_turn: number;
        };
    };
}

interface FormattedPlayer {
    name: string;
    hand: Card[];
    cash: number;
    current_bet: number;
    folded: boolean;
    all_in: boolean;
    has_played: boolean;
    texas_position: string;
}


function formatData(apiData: ApiResponse) {
    const formattedPlayers: FormattedPlayer[] = apiData.data.round_info.players.map(
        (player) => {
            const cards = player.hand.map((card) => card.value + card.suit);
            console.error("cards:", cards);
            return {
                name: player.name,
                hand: player.hand,
                cash: player.cash,
                current_bet: player.current_bet,
                folded: player.folded,
                all_in: player.all_in,
                has_played: player.has_played, // set 'checked' property initial value to 'false'  
                texas_position: player.texas_position
            };
        }
    );

    return {
        players: formattedPlayers,
        communityCards: apiData.data.round_info.community_cards,
        roundInfo: apiData.data.round_info
    };
}



export async function POST(req: NextRequest) {
    try {

        const body = await req.json();
        const { table_id} = body
        console.error("tableid", table_id)

        const startGameReq = {
            table_id: table_id,
        };

        const response = await fetch(
            `http://localhost:5670/api/v1/play_poker/start_poker_game`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(startGameReq),
            }
        );

        if (!response.ok) {
            throw new Error("Failed to fetch data");
        }

        const apiData = (await response.json()) as ApiResponse;
        console.error("table_data", apiData)
        const formattedData = formatData(apiData);
        console.error("formattedData", formattedData)

        return NextResponse.json({ message: "Success", data: formattedData }, { status: 200 });
    } catch (error) {
        return NextResponse.json(
            { message: "Error fetching data", error: (error as Error).message },
            { status: 500 }
        );
    }
}


