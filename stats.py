import sqlite3

DB_PATH = "poker_stats.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS hands (
        hand_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        winner    TEXT,
        pot       INTEGER,
        showdown  INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS actions (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        hand_id   INTEGER,
        stage     TEXT,
        player    TEXT,
        action    TEXT,
        FOREIGN KEY(hand_id) REFERENCES hands(hand_id)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS player_results (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        hand_id          INTEGER,
        player           TEXT,
        chips_won        INTEGER,
        went_to_showdown INTEGER,
        won_showdown     INTEGER,
        FOREIGN KEY(hand_id) REFERENCES hands(hand_id)
    )
    """)

    conn.commit()
    conn.close()

class StatsManager:
    def __init__(self, players):
        self.players = players
        init_db()
        self.reset_session_stats()
        self._current_hand_id = None
        self._pending_actions = []
        self._hand_winner = None
        self._hand_pot = 0
        self._hand_showdown = False

    def reset_session_stats(self):
        self.session = {
            player: {
                "hands_played":     0,
                "vpip":             0,
                "pfr":              0,
                "bets":             0,
                "raises":           0,
                "calls":            0,
                "folds":            0,
                "wins":             0,
                "chips_won":        0,
                "went_to_showdown": 0,
                "won_showdown":     0,
            }
            for player in self.players
        }

    def record_new_hand(self):
        for player in self.players:
            self.session[player]["hands_played"] += 1
        self._pending_actions = []
        self._hand_winner = None
        self._hand_pot = 0
        self._hand_showdown = False
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO hands (winner, pot, showdown) VALUES (NULL, 0, 0)")
        self._current_hand_id = c.lastrowid
        conn.commit()
        conn.close()

    def record_action(self, player, action, stage):
        stats = self.session[player]
        if action == "call":
            stats["calls"] += 1
        elif action == "bet":
            stats["bets"] += 1
            if stage == "preflop":
                stats["pfr"] += 1
        elif action == "raise":
            stats["raises"] += 1
            if stage == "preflop":
                stats["pfr"] += 1
        elif action == "fold":
            stats["folds"] += 1
        if stage == "preflop" and action in ["call", "bet", "raise"]:
            stats["vpip"] += 1
        self._pending_actions.append((self._current_hand_id, stage, player, action))

    def record_win(self, player, amount):
        self.session[player]["wins"]      += 1
        self.session[player]["chips_won"] += amount
        self._hand_winner = player
        self._hand_pot    = amount

    def record_showdown(self, player, won):
        self.session[player]["went_to_showdown"] += 1
        if won:
            self.session[player]["won_showdown"] += 1
        self._hand_showdown = True

    def flush_hand(self):
        if self._current_hand_id is None:
            return
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            UPDATE hands SET winner=?, pot=?, showdown=? WHERE hand_id=?
        """, (self._hand_winner, self._hand_pot,
              1 if self._hand_showdown else 0,
              self._current_hand_id))
        c.executemany("""
            INSERT INTO actions (hand_id, stage, player, action)
            VALUES (?, ?, ?, ?)
        """, self._pending_actions)
        for player in self.players:
            s = self.session[player]
            c.execute("""
                INSERT INTO player_results
                (hand_id, player, chips_won, went_to_showdown, won_showdown)
                VALUES (?, ?, ?, ?, ?)
            """, (self._current_hand_id, player,
                  s["chips_won"], s["went_to_showdown"], s["won_showdown"]))
        conn.commit()
        conn.close()
        self._pending_actions = []

    def print_stats(self):
        print("\n" + "=" * 50)
        print("SESSION STATS")
        print("=" * 50)
        for player, stats in self.session.items():
            hands = stats["hands_played"] or 1
            vpip_pct = stats["vpip"] / hands * 100
            pfr_pct  = stats["pfr"]  / hands * 100
            agg      = (stats["bets"] + stats["raises"]) / max(stats["calls"], 1)
            print(f"\n  {player}")
            print(f"    Hands Played   : {stats['hands_played']}")
            print(f"    Wins           : {stats['wins']}")
            print(f"    Chips Won (net): {stats['chips_won']}")
            print(f"    VPIP           : {vpip_pct:.1f}%")
            print(f"    PFR            : {pfr_pct:.1f}%")
            print(f"    Aggression     : {agg:.2f}")
            print(f"    Folds          : {stats['folds']}")
            if stats["went_to_showdown"]:
                wtsd = stats["won_showdown"] / stats["went_to_showdown"] * 100
                print(f"    Showdown Win % : {wtsd:.1f}%")

def view_stats_menu():
    init_db()  
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM hands WHERE winner IS NOT NULL")
    total_hands = c.fetchone()[0]
    conn.close()

    if total_hands == 0:
        print("\nNo game data found. Play some hands first!")
        return

    while True:
        print("\n" + "=" * 50)
        print("DATABASE STATS")
        print("=" * 50)
        print(f"  Total hands recorded: {total_hands}")
        print("\n  1. Overall player summary")
        print("  2. Action breakdown by player")
        print("  3. Recent hand history")
        print("  4. Back to main menu")

        choice = input("\nSelect option (1-4): ").strip()

        if choice == "1":
            _show_player_summary()
        elif choice == "2":
            _show_action_breakdown()
        elif choice == "3":
            _show_recent_hands()
        elif choice == "4":
            break
        else:
            print("Invalid input.")


def _show_player_summary():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    print("\n" + "-" * 50)
    print("OVERALL PLAYER SUMMARY (all recorded games)")
    print("-" * 50)
    c.execute("SELECT DISTINCT player FROM actions")
    players = [row[0] for row in c.fetchall()]
    for player in players:
        c.execute("SELECT COUNT(DISTINCT hand_id) FROM actions WHERE player=?", (player,))
        hands = c.fetchone()[0] or 1
        c.execute("SELECT COUNT(*) FROM hands WHERE winner=?", (player,))
        wins = c.fetchone()[0]
        c.execute("""
            SELECT COUNT(DISTINCT hand_id) FROM actions
            WHERE player=? AND stage='preflop' AND action IN ('call','bet','raise')
        """, (player,))
        vpip_hands = c.fetchone()[0]
        c.execute("""
            SELECT COUNT(DISTINCT hand_id) FROM actions
            WHERE player=? AND stage='preflop' AND action IN ('raise','bet')
        """, (player,))
        pfr_hands = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM actions WHERE player=? AND action IN ('bet','raise')", (player,))
        agg_actions = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM actions WHERE player=? AND action='call'", (player,))
        calls = c.fetchone()[0]
        c.execute("SELECT SUM(went_to_showdown), SUM(won_showdown) FROM player_results WHERE player=?", (player,))
        row = c.fetchone()
        wtsd_total = row[0] or 0
        wtsd_wins  = row[1] or 0
        print(f"\n  {player}")
        print(f"    Hands Played  : {hands}")
        print(f"    Wins          : {wins}  ({wins/hands*100:.1f}%)")
        print(f"    VPIP          : {vpip_hands/hands*100:.1f}%")
        print(f"    PFR           : {pfr_hands/hands*100:.1f}%")
        print(f"    Aggression    : {agg_actions/max(calls,1):.2f}")
        if wtsd_total:
            print(f"    Showdown W%   : {wtsd_wins/wtsd_total*100:.1f}%  ({wtsd_wins}/{wtsd_total})")
    conn.close()


def _show_action_breakdown():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    print("\n" + "-" * 50)
    print("ACTION BREAKDOWN BY PLAYER & STREET")
    print("-" * 50)
    c.execute("SELECT DISTINCT player FROM actions")
    players = [row[0] for row in c.fetchall()]
    for player in players:
        print(f"\n  {player}")
        for stage in ["preflop", "flop", "turn", "river"]:
            c.execute("""
                SELECT action, COUNT(*) FROM actions
                WHERE player=? AND stage=?
                GROUP BY action ORDER BY COUNT(*) DESC
            """, (player, stage))
            rows = c.fetchall()
            if rows:
                parts = ", ".join(f"{action}: {cnt}" for action, cnt in rows)
                print(f"    {stage.capitalize():8s}: {parts}")
    conn.close()


def _show_recent_hands():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    print("\n" + "-" * 50)
    print("LAST 10 HANDS")
    print("-" * 50)
    c.execute("""
        SELECT hand_id, winner, pot, showdown, timestamp
        FROM hands WHERE winner IS NOT NULL
        ORDER BY hand_id DESC LIMIT 10
    """)
    rows = c.fetchall()
    if not rows:
        print("  No completed hands found.")
        conn.close()
        return
    print(f"  {'Hand':>5}  {'Winner':<12}  {'Pot':>6}  {'Showdown':>8}  Timestamp")
    print("  " + "-" * 55)
    for hand_id, winner, pot, showdown, ts in rows:
        sd = "Yes" if showdown else "No"
        ts_short = ts[:16] if ts else "-"
        print(f"  {hand_id:>5}  {winner:<12}  {pot:>6}  {sd:>8}  {ts_short}")
    conn.close()

def clear_stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM hands")
    c.execute("DELETE FROM actions")
    c.execute("DELETE FROM player_results")
    conn.commit()
    conn.close()