# 🃏 Cozy Call Break Scorekeeper

A beautiful, cozy, fast, mobile-friendly digital scorekeeper for the **Call Break** card game built with **Python & Streamlit**.

Designed to replace paper scorekeeping during game night — with a warm card-table aesthetic (forest green felt, dark mahogany wood, cream cards, and muted gold accents).

---

## 🌟 Features

- 👥 **2 to 5 Player Support**: Dynamic player setup with name validation and default presets.
- 🃏 **Automatic 5-Player Deck Handling**: Automatically notes the removal of **2♥** and **2♦** (48 cards total, 9 tricks per round).
- 🎯 **Exact Call Break Scoring**:
  - **Tricks Won ≥ Call**: $\text{Score} = \text{Call} + (\text{Tricks Won} - \text{Call}) \times 0.1$
  - **Tricks Won < Call**: $\text{Score} = -\text{Call}$
  - `Decimal` floating point precision guarantees exact scores rounded to 1 decimal place (`+3.1`, `-3.0`, `0.0`).
- ⚡ **Fast 3-Step Round Workflow**:
  1. **Enter Calls**: Quick input fields for each player.
  2. **Play Round**: View active calls at a glance while playing cards.
  3. **Enter Tricks Won**: Touch-friendly input with **real-time live score previews** and trick validation.
- 📊 **Main Scoreboard & Live Leaderboard**:
  - Player Score Cards with Leader Crown 👑.
  - Matrix Scoreboard Table (Rounds x Players + Totals row). Dynamic column layout.
- 📜 **Round History, Editing & Undo**:
  - Inspect any finished round.
  - Edit calls or tricks won with automatic total score recalculations.
  - One-click **Undo Last Round** with safety confirmation.
- 💾 **Local Storage Persistence**:
  - Game state automatically persists to local `callbreak_game.json`.
  - Survives browser refreshes with **"Continue Saved Game"** option.
  - Protection against accidental overwrite when starting a new game.
- 📤 **Share Results**: Format final scores into a clean text block to copy and share on WhatsApp or SMS.
- 🎨 **Cozy Card-Table Aesthetic**: Custom CSS injected via `styles.py`.

---

## 📁 Project Structure

```text
callbreak1/
│
├── app.py               # Main Streamlit web application interface & navigation
├── game_logic.py        # Pure scoring engine, validation, and calculations
├── storage.py           # JSON file persistence (save, load, clear)
├── styles.py            # Custom CSS for cozy dark-green felt visual theme
├── test_game_logic.py   # Unit test suite verifying scoring and logic
├── requirements.txt     # Dependency specifications (streamlit, pandas)
└── README.md            # Documentation & user guide
```

---

## 🚀 Quick Start & Installation

### 1. Clone the repository
```bash
git clone <repository_url>
cd callbreak1
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## 🧪 Running Unit Tests

Run the test suite to verify scoring accuracy and validation rules:

```bash
python -m unittest test_game_logic.py
```

---

## 📜 Call Break Scoring Rules

### 1. Successful Call ($\text{Tricks Won} \ge \text{Call}$)
Points equal your call **plus 0.1 for every extra trick won**.
- Call 2, Won 2 → **+2.0 points**
- Call 3, Won 4 → **+3.1 points**
- Call 4, Won 6 → **+4.2 points**

### 2. Failed Call ($\text{Tricks Won} < \text{Call}$)
Points equal your negative call.
- Call 3, Won 2 → **-3.0 points**
- Call 5, Won 3 → **-5.0 points**

### 3. 5-Player Deck Adjustment
When playing with 5 players:
- **2♥** and **2♦** are removed from the deck (48 cards total).
- Each player receives **9 cards** per hand (45 cards dealt).
- Available tricks per round: **9 tricks**.

---

## 🎨 Design Philosophy

Sitting around a warm table playing cards with friends should feel cozy, minimal, and playful — not like using a cold Excel spreadsheet.

- **Dark Forest Green Felt Background** (`#0d2117` / `#1b3d2c`)
- **Cream Cardstock Containers** (`#fcf9f2` / `#142e22`)
- **Muted Gold Accents** (`#d4af37` / `#e5c158`)
- **Serif Typography** (`Cinzel`)
