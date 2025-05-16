import { NextRequest, NextResponse } from "next/server";

import fetch from "node-fetch";


export interface PlayAction {
    table_id: number;
    player_id: number;
    player_action: PlayerActionModel;
}

export interface PlayerActionModel {
    action: string;
    amount: number;
}

export async function POST(req: NextRequest) {
    try {
        const body = await req.json();

        const { table_id, player_id, action, amount } = body

        const playActionReq = {
            table_id: table_id,
            player_id: player_id,
            player_action: {
                action: action,
                amount: amount,
            },
        };

        const response = await playerAction(playActionReq);
        if (response.message === "Success") {
            console.log("Player action success!");

        } else {
            throw new Error(response.message)
        }

        return NextResponse.json({ message: "Success", data: response }, { status: 200 });
    } catch (error) {
        return NextResponse.json(
            { message: "Error fetching data", error: (error as Error).message },
            { status: 500 }
        );
    }
}


export const playerAction = async (play_action: PlayAction): Promise<{ message: string; data?: any }> => {
    try {
        const response = await fetch(
            `http://localhost:5670/api/v1/play_poker/player_action`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(play_action),
            }
        );

        if (!response.ok) {
            throw new Error("Failed to fetch data");
        }

        const apiData = await response.json();
        console.log("Player action response:", apiData);
        return { message: "Success", data: apiData };

    } catch (error) {
        throw new Error((error as Error).message);
    }
};
