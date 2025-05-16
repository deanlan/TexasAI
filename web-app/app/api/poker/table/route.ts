import { NextRequest, NextResponse } from "next/server";

import fetch from "node-fetch";


interface ApiResponse {
    success: boolean;
    err_code: string | null;
    err_msg: string | null;
    table_id: number;
}


interface JoinTableRequestBody {
    table_id: number;
    player_info: {
        player_name: string;
    },
    is_bot: boolean;
}

interface JoinTableResponse {
    success: boolean;
    message: string;
}

export async function joinTable(data: JoinTableRequestBody): Promise<JoinTableResponse> {
    try {
        console.error("join_table_data:", data)
        const response = await fetch(
            `http://localhost:5670/api/v1/play_poker/join_table`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            throw new Error("Failed to fetch data");
        }

        const responseData = (await response.json()) as JoinTableResponse;
        console.error("join_table_data:", responseData)
        return responseData;
    } catch (error) {
        throw new Error((error as Error).message);
    }
}

export async function POST(req: NextRequest) {
    try {
        const player_names = ["You"];

        const response = await fetch(
            `http://localhost:5670/api/v1/play_poker/create_table`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ player_names }),
        });

        if (!response.ok) {
            throw new Error("Failed to fetch data");
        }

        const apiData = (await response.json()) as ApiResponse;
        console.error("table_data:", apiData)

        const joinTableData = {
            table_id: apiData.table_id,
            player_name: "Bot",
            is_bot: true,
        };

        const joinTableResponse = await joinTable(joinTableData);
        if (!joinTableResponse.success) {
            throw new Error(joinTableResponse.message);
        }

        return NextResponse.json({ message: "Success", data: apiData.table_id }, { status: 200 });
    } catch (error) {
        return NextResponse.json(
            { message: "Error fetching data", error: (error as Error).message },
            { status: 500 }
        );
    }
}