"use client"

import Head from 'next/head';
import styles from '../../styles/table.module.css';


// pages/table/index.js  
import { useEffect, useState } from "react";


interface Player {
    name: string;
    hand: string[];
    texas_position: string;
    cash: string;
    current_bet: string;
};

interface GameResult {
    players: Player[];
    communityCards: string[];
    roundInfo: {
        pot: number;
        current_state: "pre-flop" | "flop" | "turn" | "river" | "end";
        current_turn: number;
        winners: Player[];
    };
}

interface WinnersModalProps {
    gameResult: GameResult;
    onClose: () => void;
}



export default function Deal() {

    const [tableId, setTableId] = useState(-1);
    // const [dealResult, setDealResult] = useState({
    //     players: Array.from({ length: 2 }, () => ({ name: "", cards: ["back", "back"] })),
    //     communityCards: Array(5).fill("back"),
    // });

    const [dealResult, setDealResult] = useState<GameResult>({
        players: Array.from({ length: 2 }, () => ({
            name: "",
            hand: ["back", "back"],
            texas_position: "",
            cash: "",
            current_bet: "",

        })),
        communityCards: Array(5).fill("back"),
        roundInfo: {
            pot: 0,
            current_state: "pre-flop",
            current_turn: 0,
            winners: [],
        },
    });

    const [showWinnersModal, setShowWinnersModal] = useState(false);
    const [FinalState, SetFinalState] = useState(true);


    // 用于重新发牌  
    const handleStart = async () => {
        SetFinalState(false);
        let currentTableId = tableId;

        if (currentTableId < 0) {
            currentTableId = await CreateTableId();
        }

        console.error("current table_id:", currentTableId);

        const startGameReq = {
          table_id: currentTableId,
        }

        const response = await fetch('/api/poker/start_game', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify(startGameReq),
        });

        const { data } = await response.json();
        console.error("data:", data)


        // 填充手牌
        // data.players.forEach((player: { cards: string[]; }, index: number) => {

        //     // 只展示自己的牌， 其他人的牌展示为back
        //     // if (index !== 0) {
        //     //     player.cards = ["back", "back"];
        //     // }

        // });

        // 填充公共牌，以及游戏状态；
        const game_state = await fetchGameState(currentTableId);
        console.error("game_state", game_state)
        const community_cards = game_state.community_cards


        if (community_cards) {

            data.communityCards = Array(5)
                .fill("back")
                .map((index) => (index < community_cards.length ? community_cards[index].value + community_cards[index].suit : "back"));
        } else {
            data.communityCards = Array(5).fill("back");
        }

        data.players.forEach((player: any) => {
            player.hand = player.hand.map((card: { value: any; suit: any; }) => card.value + card.suit);
            player.player_info = {
                texas_position: player.texas_position,
                cash: player.cash,
                current_bet: player.current_bet,
            };
        });

        setDealResult(data);

        console.error("dataResult", dealResult)

    };

    async function CreateTableId() {
        try {
            const response = await fetch("/api/poker/table", {
                method: "POST",
            });

            const res = await response.json();
            console.error("table_res:", res)
            setTableId(res.data);
            return res.data;

        } catch (error) {
            console.error("Error fetching table ID:", error);
        }
    }

    //获取公共牌
    const fetchGameState = async (tableId: number) => {
        // setIsLoading(true);  
        try {
            const response = await fetch(
                `/api/poker/game_state?table_id=${tableId}`,
            );
            const responseData = await response.json();
            console.error("responseData", responseData)

            // if (responseData == 200) {
            const game_state = responseData.data
            console.error("game_state", game_state)
            return game_state

        } catch (error) {
            console.error("Error fetching community cards:", error);
            return null;
        }
    };

    const updatePokerGame = async (tableId: number) => {
        try {

            const game_state = await fetchGameState(tableId);
            console.error("game_state", game_state)
            const community_cards = game_state.community_cards
            console.error("community_cards", community_cards)

            const pot = game_state.pot
            const players = game_state.players
            const winners = game_state.winners


            console.error("winnners", winners)

            players.forEach((player: any) => {
                player.hand = player.hand.map((card: { value: any; suit: any; }) => card.value + card.suit);
                player.texas_position = player.texas_position;
                player.cash = player.cash;
                player.current_bet = player.current_bet;
            })

            if (community_cards) {
                const newCommunityCards = Array(5)
                    .fill("back")
                    .map((_, index) => (index < community_cards.length ? community_cards[index].value + community_cards[index].suit : "back"));
                setDealResult((prevDealResult) => ({
                    ...prevDealResult,
                    communityCards: newCommunityCards,
                    roundInfo: {
                        ...prevDealResult.roundInfo,
                        pot: pot,
                        winners: winners,
                    },
                    players: players,
                }));
            }

            const current_state = game_state.current_state


            if (current_state === "end") {
                setShowWinnersModal(true);
                SetFinalState(true)
            }

        }
        catch (error) {
            console.error("Error update PokerGame:", error);
            return null;
        }
    };

    const handleAction = async (tableId: number, action: string, player_id: number, amount: number) => {
        try {
            const playActionReq = {
                table_id: tableId,
                player_id: player_id,
                action: action,
                amount: amount,
            }

            const response = await fetch('/api/poker/play_action', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(playActionReq),
            });

            if (!response.ok) {
                throw new Error(`Request failed with status code ${response.status}`);
            }

            await updatePokerGame(tableId)

        } catch (error) {
            console.error('Error handle Bet action', error);
            return null;
        }
    };


    function WinnersModal({ gameResult, onClose }: WinnersModalProps) {
        return (
            <div className={styles.modal}>
                <div className={styles.modalOverlay}>
                    <div className={styles.modalContent}>
                        <ul>
                            {gameResult.roundInfo.winners.map((winner, index) => (
                                <li key={index}>
                                    {winner.name} win the game with ${gameResult.roundInfo.pot}
                                </li>
                            ))}
                        </ul>
                        <button className={styles.closeButton} onClick={onClose}>
                            Close
                        </button>
                    </div>
                </div>
            </div>
        );
    }


    useEffect(() => {

    }, []);

    return (
        <div className={styles.container}>
            <Head>
                <title>Texas Hold'em Pokers</title>
            </Head>


            <main className={styles.main}>
                <h1 className={styles.title}>Texas Hold'em Pokers</h1>
                <div className={styles.table}>
                    <section className={styles.players}>
                        {dealResult.players.map((player, i) => (
                            <div key={i} className={`${styles.player} ${styles["player" + (i + 1)]}`}>
                                <div className={styles.playerCards}>
                                    {player.hand.map((card, j) => (
                                        <div key={j} className={styles.card}>
                                            <img
                                                src={card ? `/cards/${card}.png` : "/cards/back.png"}
                                                alt={`${card || "Card back"}`}
                                            />
                                        </div>
                                    ))}
                                </div>
                                <div className={styles.playerInfo}>
                                    <span className={styles.playerInfoText}>
                                        {player.name || `Player ${i + 1}`}
                                        <br />
                                        {player.texas_position}
                                        <br />
                                        {player.cash}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </section>
                    <section className={styles.cards}>
                        <div className={styles.potWrapper}>
                            <span className={styles.potText}>Pot: {dealResult.roundInfo.pot}</span>
                        </div>

                        <div className={styles.cardWrapper}>
                            {dealResult.communityCards.map((card, i) => (
                                <div key={i} className={styles.card}>
                                    <img
                                        src={card ? `/cards/${card}.png` : "/cards/back.png"}
                                        alt={`${card || "Card back"}`}
                                    />
                                </div>
                            ))}
                        </div>
                    </section>
                </div>

                {/* Start button always shown */}

                <div className={styles.buttonGroup}>
                    <button className={styles.startButton} onClick={handleStart}>Start</button>
                    {/* Other buttons only shown if it's not the final state */}
                    {!FinalState && (
                        <>
                            <button
                                className={styles.foldButton}
                                onClick={() => handleAction(tableId, "FOLD", 0, 0)}
                                disabled={tableId === null}
                            >
                                FOLD
                            </button>
                            {/* <button
                                className={styles.checkButton}
                                onClick={() => handleAction(tableId, "CALL", 0, 0)}
                                disabled={tableId === null}
                            >
                                CALL
                            </button> */}
                            <button
                                className={styles.checkButton}
                                onClick={() => handleAction(tableId, "CHECK", 0, 0)}
                                disabled={tableId === null}
                            >
                                CHECK
                            </button>
                            <button
                                className={styles.betButton}
                                onClick={() => handleAction(tableId, "BET", 0, 50)}
                                disabled={tableId === null}
                            >
                                BET
                            </button>
                            <button
                                className={styles.allinButton}
                                onClick={() => handleAction(tableId, "ALL_IN", 0, 0)}
                                disabled={tableId === null}
                            >
                                ALL IN
                            </button>
                        </>
                    )}

                </div>

                {showWinnersModal && (
                    <WinnersModal
                        gameResult={dealResult}
                        onClose={() => setShowWinnersModal(false)}
                    />
                )}
            </main>

        </div>
    );
}  