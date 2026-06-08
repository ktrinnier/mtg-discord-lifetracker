import { useState } from "react";
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
};

function App() {
  const [gameId, setGameId] = useState("");
  const [game, setGame] = useState<GameSummary | null>(null);
  const [guildId, setGuildId] = useState("local-test-guild");

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

  async function createGame() {
    const response = await fetch(
      `${API_BASE_URL}/games?guild_id=${guildId}`,
      {
        method: "POST",
      }
    );

    const data = await response.json();

    setGameId(data.game_id);
  }

  async function addPlayers() {
    const selectedUsers = availableUsers.filter((user) =>
      selectedUserIds.includes(user.discord_user_id)
    );

    for (const player of selectedUsers) {
      await fetch(`${API_BASE_URL}/games/${gameId}/players`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(player),
      });
    }

    await loadGame();
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

    await loadGame();
  }

  return (
    <main className="app">
      <header className="topBar">
        <div>
          <h1>MTG Life Tracker</h1>
          {game && <p>{game.status}</p>}
        </div>

        <div className="loadGame">
          <input
            value={gameId}
            onChange={(e) => setGameId(e.target.value)}
            placeholder="Paste game ID"
          />
          <button onClick={loadGame}>Load</button>
        </div>
      </header>

      <section className="setupPanel">
      <input
        value={guildId}
        onChange={(e) => setGuildId(e.target.value)}
        placeholder="Guild ID"
      />

      <button onClick={createGame}>
        Create Game
      </button>

      <select
        className="userSelect"
        multiple
        value={selectedUserIds}
        onChange={(e) => {
          const selected = Array.from(
            e.target.selectedOptions,
            (option) => option.value
          );

          setSelectedUserIds(selected);
        }}
      >
        {availableUsers.map((user) => (
          <option
            key={user.discord_user_id}
            value={user.discord_user_id}
          >
            {user.display_name}
          </option>
        ))}
      </select>

      <button
        onClick={addPlayers}
        disabled={!gameId}
      >
        Add Players
      </button>

      <button
        onClick={startGame}
        disabled={!gameId}
      >
        Start Game
      </button>

      <select
        value={winnerPlayerId}
        onChange={(e) =>
          setWinnerPlayerId(e.target.value)
        }
      >
        <option value="">
          Select Winner
        </option>

        {game?.participants.map((p) => (
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

      {game && (
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
      )}
    </main>
  );
}

export default App;