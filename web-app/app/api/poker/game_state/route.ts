import { NextRequest, NextResponse } from "next/server";

import fetch from "node-fetch";


interface ApiResponse {
    success: boolean;
    err_code: string | null;
    err_msg: string | null;
    data: {
        round_info: {
            players: any[];
            winners: any[];
            community_cards: string[];
            texas_positions: Record<string, any>;
            round_id: string;
            current_state: string;
            pot: number;
            player_action_history: Record<string, any>;
        };
    };
}


export async function GET(req: NextRequest) {
    try {
        const searchParams = req.nextUrl.searchParams
        const table_id = searchParams.get('table_id')
        // const current_state = searchParams.get('current_state')

        console.error("tableid", table_id)

        const response = await fetch(
            `http://localhost:5670/api/v1/play_poker/get_game_state?table_id=${table_id}`,
        );

        if (!response.ok) {
            throw new Error("Failed to fetch data");
        }

        const apiData = (await response.json()) as ApiResponse;
        console.error("APIDATA", apiData)
        const game_state = apiData.data.round_info
        console.error("game_state", game_state)
        return NextResponse.json({ message: "Success", data: game_state }, { status: 200 });

    } catch (error) {
        return NextResponse.json(
            { message: "Error fetching data", error: (error as Error).message },
            { status: 500 }
        );
    }
}  

