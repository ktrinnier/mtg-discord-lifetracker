import { useEffect, useState } from "react";
import "./App.css";

const API_BASE_URL = "http://localhost:8000";

type Participant = {
  participant_id: string;
  player_id: string;
  display_name: string;
  life: number;
  poison_counters: number;
  is_eliminated?: boolean;
  eliminated_at?: string | null;
};

type GameSummary = {
  game_id: string;
  status: string;
  participants: Participant[];
  winner_player_id?: string | null;
  first_blood?: {
    player_id: string;
    display_name: string | null;
    delta: number;
    created_at: string;
  } | null;
};


type LobbyGame = GameSummary;

function App() {
  const [gameId, setGameId] = useState("");
  const [game, setGame] = useState<GameSummary | null>(null);
  // const [guildId, setGuildId] = useState("local-test-guild");
  const guildId = "local-test-guild";
  const [activeGames, setActiveGames] = useState<LobbyGame[]>([]);
  const [view, setView] = useState<"lobby" | "game" | "summary">("lobby");
  const [playerDropdownOpen, setPlayerDropdownOpen] = useState(false);

  const availableUsers = [
    { discord_user_id: "111111111", display_name: "Hank" },
    { discord_user_id: "222222222", display_name: "Bobby" },
    { discord_user_id: "333333333", display_name: "Peggy" },
    { discord_user_id: "444444444", display_name: "Ladybird" },
  ];

  const [selectedUserIds, setSelectedUserIds] = useState<string[]>([]);

  const [winnerPlayerId, setWinnerPlayerId] = useState("");

  async function loadGame() {
    const response = await fetch(`${API_BASE_URL}/games/${gameId}`);
    const data = await response.json();
    setGame(data);
    setView("game");
  }

  async function loadActiveGames() {
    const response = await fetch(`${API_BASE_URL}/games?status=active`);
    const data = await response.json();

    setActiveGames(data);
  }

  async function adjustLife(participantId: string, delta: number) {
    await fetch(`${API_BASE_URL}/participants/${participantId}/life`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ delta }),
    });

    await loadGame();
  }

  async function adjustPoison(participantId: string, delta: number) {
    await fetch(`${API_BASE_URL}/participants/${participantId}/poison`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ delta }),
    });

    await loadGame();
  }

  async function createGameWithPlayers() {
    const selectedUsers = availableUsers.filter((user) =>
      selectedUserIds.includes(user.discord_user_id)
    );

    if (selectedUsers.length === 0) {
      return;
    }

    const response = await fetch(
      `${API_BASE_URL}/games?guild_id=${guildId}`,
      { method: "POST" }
    );

    const data = await response.json();
    const newGameId = data.game_id;

    setGameId(newGameId);

    for (const player of selectedUsers) {
      await fetch(`${API_BASE_URL}/games/${newGameId}/players`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(player),
      });
    }

    const gameResponse = await fetch(`${API_BASE_URL}/games/${newGameId}`);
    const gameData = await gameResponse.json();

    setGame(gameData);
    setView("game");
  }

  async function startGame() {
    await fetch(
      `${API_BASE_URL}/games/${gameId}/start`,
      {
        method: "POST",
      }
    );

    await loadGame();
  }

  async function finishGame() {
    await fetch(
      `${API_BASE_URL}/games/${gameId}/finish`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          winner_player_id: winnerPlayerId,
        }),
      }
    );

    const response = await fetch(`${API_BASE_URL}/games/${gameId}`);
    const data = await response.json();

    setGame(data);
    setView("summary");
  }

  useEffect(() => {
    if (view !== "lobby") return;

    loadActiveGames();

    const interval = window.setInterval(() => {
      loadActiveGames();
    }, 5000);

    return () => window.clearInterval(interval);
  }, [view]);

  return (
    <main className="app">
      <header className="topBar">
        <div>
          <h1>MTG Life Tracker</h1>
          {game && <p>{game.status}</p>}
        </div>
        {view === "game" && (
          <button
            onClick={() => {
              setView("lobby");
            }}
          >
            ← Lobby
          </button>
        )}
      </header>

      {view === "summary" && game && (
        <section className="summaryScreen">
          <div className="summaryContent">
            <h2>Game Finished</h2>

            <div className="winnerCard">
              <div className="winnerLabel">
                Winner
              </div>
              <div className="winnerName">
                {
                  game.participants.find(
                    (p) => p.player_id === game.winner_player_id
                  )?.display_name ?? "Unknown"
                }
              </div>
            </div>

            <div className="summaryCard">
              <h3>Final Life Totals</h3>

              {game.participants.map((p) => (
                <div key={p.participant_id} className="summaryRow">
                  <span>{p.display_name}</span>
                  <span>
                    Life: {p.life} | Poison: {p.poison_counters}
                  </span>
                </div>
              ))}
            </div>

            {game.first_blood && (
              <div className="summaryCard">
                <h3>First Blood</h3>
                <p>{game.first_blood.display_name}</p>
              </div>
            )}

            <button
              onClick={() => {
                setView("lobby");
                setGame(null);
                setWinnerPlayerId("");
                loadActiveGames();
              }}
            >
              Return to Lobby
            </button>
          </div>
        </section>
      )}

      {view === "lobby" && (
        <section className="setupPanel">
          <div className="playerDropdown">
            <button
              className="playerDropdownButton"
              onClick={() => setPlayerDropdownOpen(!playerDropdownOpen)}
            >
              {selectedUserIds.length === 0
                ? "Select players"
                : `${selectedUserIds.length} players selected`}
            </button>

            {playerDropdownOpen && (
              <div className="playerDropdownMenu">
                {availableUsers.map((user) => {
                  const selected = selectedUserIds.includes(user.discord_user_id);

                  return (
                    <button
                      key={user.discord_user_id}
                      className={`playerDropdownItem ${selected ? "selected" : ""}`}
                      onClick={() => {
                        if (selected) {
                          setSelectedUserIds(
                            selectedUserIds.filter(
                              (id) => id !== user.discord_user_id
                            )
                          );
                        } else {
                          setSelectedUserIds([
                            ...selectedUserIds,
                            user.discord_user_id,
                          ]);
                        }
                      }}
                    >
                      <span>{user.display_name}</span>
                      <span>{selected ? "✓" : ""}</span>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
          <button
            onClick={createGameWithPlayers}
            disabled={selectedUserIds.length === 0}
          >
            Create Game
          </button>
        </section>
      )}

      {view === "lobby" && (
        <section className="lobby">
          <h2>Active Games</h2>

          {activeGames.length === 0 && (
            <p className="muted">No active games found.</p>
          )}

          <div className="lobbyGrid">
            {activeGames.map((activeGame) => (
              <button
                key={activeGame.game_id}
                className="lobbyCard"
                onClick={() => {
                  setGameId(activeGame.game_id);
                  setGame(activeGame);
                  setView("game");
                }}
              >
                <div className="lobbyCardHeader">
                  <strong>{activeGame.status}</strong>
                  <span>{activeGame.participants.length} players</span>
                </div>

                <div className="lobbyPlayers">
                  {activeGame.participants.map((p) => (
                    <span key={p.participant_id}>
                      {p.display_name} ({p.life})
                    </span>
                  ))}
                </div>
              </button>
            ))}
          </div>
        </section>
      )}
      {view === "game" && game && (
        <>
          {game.status === "created" && (
            <section className="notStartedBanner">
              <h2>Game not started</h2>
              <p>Players are added. Start the game when everyone is ready.</p>
              <button onClick={startGame}>Start Game</button>
            </section>
          )}
          <section className="gameActions">
            <select
              value={winnerPlayerId}
              onChange={(e) => setWinnerPlayerId(e.target.value)}
            >
              <option value="">Select Winner</option>

              {game.participants.map((p) => (
                <option
                  key={p.player_id}
                  value={p.player_id}
                >
                  {p.display_name}
                </option>
              ))}
            </select>

            <button
              onClick={finishGame}
              disabled={!winnerPlayerId}
            >
              Finish Game
            </button>
          </section>

          <section className="tableGrid">
            {game.participants.map((p) => (
              <article
                key={p.participant_id}
                className={`playerTile ${p.is_eliminated ? "eliminated" : ""}`}
              >
                <button
                  className="tapZone tapLeft"
                  onClick={() => adjustLife(p.participant_id, -1)}
                  aria-label={`${p.display_name} loses 1 life`}
                >
                  −
                </button>

                <button
                  className="tapZone tapRight"
                  onClick={() => adjustLife(p.participant_id, 1)}
                  aria-label={`${p.display_name} gains 1 life`}
                >
                  +
                </button>

                <div className="playerContent">
                  <div className="playerName">{p.display_name}</div>

                  <div className="lifeTotal">{p.life}</div>

                  <div className="quickControls">
                    <button onClick={() => adjustLife(p.participant_id, -5)}>
                      -5
                    </button>
                    <button onClick={() => adjustLife(p.participant_id, 5)}>
                      +5
                    </button>
                  </div>

                  <div className="counterBar">
                    <span>☠ {p.poison_counters}</span>
                    <button onClick={() => adjustPoison(p.participant_id, -1)}>
                      -
                    </button>
                    <button onClick={() => adjustPoison(p.participant_id, 1)}>
                      +
                    </button>
                  </div>

                  {p.is_eliminated && (
                    <div className="eliminatedBadge">ELIMINATED</div>
                  )}
                </div>
              </article>
            ))}
          </section>
        </>
      )}
    </main>
  );
}

export default App;