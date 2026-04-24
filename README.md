# CommandLinePokerSoftware

A command-line **Texas Hold'em** simulator written in Python.

Supports human and bot play, multiple game modes, hand evaluation, side-pot handling, and persistent stats stored in SQLite.

## Features

- **Texas Hold'em game loop** with blinds, dealer rotation, betting streets, and showdown resolution
- **Multiple game modes**:
  - Player vs Player (PvP)
  - Player vs Computer (PvC)
  - Computer vs Computer (CvC)
- **Bot difficulties**:
  - Easy — tier-based preflop + light equity post-flop
  - Medium — tier-based preflop + Monte Carlo equity with board awareness
  - Hard — full Monte Carlo equity with position, opponent reads, bluffing, and value sizing
  - Chaos — random actions
- **Advanced bot features** (Medium / Hard):
  - Monte Carlo equity estimation with opponent range modeling based on observed VPIP/PFR
  - Board texture analysis (flush draws, straight draws, paired boards, danger scoring)
  - Opponent classification (tight-aggressive, loose-passive, etc.)
  - Position-aware decisions and bluff frequency tuning
  - LRU equity cache to reduce redundant simulations
- **Poker engine** supporting:
  - Legal action generation (check / call / bet / raise / fold / all-in)
  - Hand ranking across all 7-card combinations
  - All-in runouts and side-pot distribution
- **Persistent statistics** via SQLite:
  - Hand history with winner, pot size, and showdown flag
  - Per-action logs by player and street
  - Session and database-wide player metrics (VPIP, PFR, aggression factor, showdown win rate)

## Requirements

**To run from source:**
- Python **3.9+**
- No third-party packages required (standard library only)

**To run the executable:**
- Windows 10/11 (64-bit)
- No Python installation needed — everything is bundled via PyInstaller

## Quick Start

### Option 1 — Run the executable (no Python required)

A pre-built Windows executable is included for convenience.

1. Download `main.exe` from the repository
2. Double-click it, or run it from a terminal:

```bash
main.exe
```

> **Note:** Windows may show a SmartScreen warning for unsigned executables. Click **More info → Run anyway** to proceed.

### Option 2 — Run from source

Requires Python 3.9+.

```bash
python3 main.py
```

Use the in-game menu to:

1. Start a game
2. View database stats
3. Clear stats
4. View rules
5. Quit

## Game Configuration

When starting a game you can choose:

- **Mode**: PvP, PvC, or CvC
- **Player count**: 2–8
- **Bot difficulty** (for modes with bots): Easy, Medium, Hard, Chaos

Default settings:

- Starting chips: `1000`
- Starting small blind: `10`

## Stats & Database

Stats are persisted in `poker_stats.db` across sessions. The app records:

- `hands` — winner, pot size, showdown flag, timestamp
- `actions` — every player action logged by street
- `player_results` — per-hand chip delta and showdown outcomes

View stats through the app menu (**View Stats**), including:

- Overall player summary (VPIP, PFR, aggression, win rate, showdown %)
- Action breakdown by player and street
- Recent hand history (last 10 hands)

## Project Structure

| File | Description |
|---|---|
| `main.py` | Entrypoint, game loop, game-over detection |
| `menu.py` | Interactive menus and setup prompts |
| `gameplay.py` | Dealing, betting rounds, hand evaluation, side-pots, showdown |
| `strategies.py` | Human input + all bot strategies including Monte Carlo |
| `game_state.py` | Initial game-state construction |
| `stats.py` | Session stats tracking + SQLite persistence and reporting |
| `constants.py` | Ranks, suits, blind sizes, rank values, preflop tier table |
| `game_texts.py` | UI strings for menus and rules display |

## Notes

- Terminal only — no GUI required.
- CvC mode is useful for quickly simulating many hands and building up stat history.
- Existing `poker_stats.db` data persists between runs unless cleared from the menu.
