# CommandLinePokerSoftware

A command-line **Texas Hold'em** simulator written in Python.

This project supports human and bot play, multiple game modes, hand evaluation, side-pot handling, and persistent stats in SQLite.

## Features

- **Texas Hold'em game loop** with blinds, dealer rotation, betting streets, and showdown resolution.
- **Multiple game modes**:
  - Player vs Player (PvP)
  - Player vs Computer (PvC)
  - Computer vs Computer (CvC)
- **Bot difficulties**:
  - Easy
  - Medium
  - Hard (Monte Carlo equity-based decisions)
  - Chaos (random actions)
- **Poker engine support** for:
  - legal action generation (check/call/bet/raise/fold/all-in)
  - hand ranking and winner selection
  - all-in runouts and side-pot distribution
- **Persistent statistics** (SQLite):
  - hand history
  - per-action logs
  - player summary metrics (VPIP, PFR, aggression, showdown rates)

## Requirements

- Python **3.9+**
- No third-party packages required (uses only Python standard library)

## Quick Start

From the repository root:

```bash
python3 main.py
```

Then use the in-game menu to:

1. Start a game
2. View database stats
3. Clear stats
4. View rules
5. Quit

## Game Configuration

When starting a game you can choose:

- **Mode**: PvP, PvC, or CvC
- **Player count**: 2 to 8
- **Bot difficulty** (for modes with bots): easy, medium, hard, chaos

Default settings include:

- Starting chips: `1000`
- Starting small blind: `10`

## Stats & Database

Stats are persisted in:

- `poker_stats.db`

The app records:

- Hands (`hands` table)
- Player actions by stage (`actions` table)
- Player results (`player_results` table)

You can inspect stats through the app menu (**View Stats**), including:

- overall player summary
- action breakdown by player/street
- recent hand history

## Project Structure

- `main.py` — entrypoint and overall game loop
- `menu.py` — interactive menu and setup prompts
- `gameplay.py` — dealing, betting rounds, hand evaluation, pots/showdown
- `strategies.py` — human input + bot strategies (including Monte Carlo bot)
- `game_state.py` — initial game-state construction
- `stats.py` — session stats + SQLite persistence/reporting
- `constants.py` — ranks, suits, blinds, and rank values
- `game_texts.py` — menu/rules UI text

## Notes

- This is a terminal game; no GUI is required.
- CvC mode is useful for quickly simulating many hands and generating stats.
- Existing `poker_stats.db` data may reflect previous runs in this directory.
