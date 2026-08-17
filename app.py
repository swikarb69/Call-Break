"""
app.py
Main Streamlit Application for Cozy Call Break Scorekeeper.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any

from game_logic import (
    calculate_score,
    format_score,
    get_available_tricks,
    validate_player_names,
    validate_calls,
    validate_tricks,
    calculate_round_scores,
    calculate_totals,
    get_leaderboard,
    format_share_summary
)
import storage
from styles import inject_cozy_css

# Page Configuration
st.set_page_config(
    page_title="Call Break Scorekeeper",
    page_icon="🃏",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Inject Cozy Visual Theme CSS
inject_cozy_css()


def init_session_state():
    """Initializes session state and loads saved game if present."""
    if "game" not in st.session_state:
        saved_game = storage.load_game()
        st.session_state.game = saved_game
        
    if "confirm_new_game" not in st.session_state:
        st.session_state.confirm_new_game = False
        
    if "editing_round_idx" not in st.session_state:
        st.session_state.editing_round_idx = None


def save_game_state():
    """Helper to save active game state to JSON storage."""
    if st.session_state.game:
        storage.save_game(st.session_state.game)


# ==========================================
# 1. LANDING & PLAYER SETUP SCREEN
# ==========================================
def render_setup_screen():
    st.markdown("""
        <div class="hero-box">
            <div class="suit-symbols">♠ ♥ ♦ ♣</div>
            <h1 class="cozy-title">CALL BREAK</h1>
            <p class="cozy-subtitle">No more paper. Just play.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Check for saved game
    if storage.has_saved_game():
        saved = storage.load_game()
        if saved and saved.get("status") == "active":
            st.info(f" Saved game in progress ({len(saved.get('players', []))} players, Round {saved.get('current_round', 1)}).")
            col_cont, col_discard = st.columns(2)
            with col_cont:
                if st.button("Continue Saved Game ⏯️", use_container_width=True):
                    st.session_state.game = saved
                    st.rerun()
            with col_discard:
                if st.button("Discard & Start New 🗑️", type="secondary", use_container_width=True):
                    storage.clear_game()
                    st.session_state.game = None
                    st.rerun()
            st.divider()

    with st.container():
        st.markdown('<div class="cozy-card">', unsafe_allow_html=True)
        st.subheader("Who's playing?")
        
        num_players = st.radio(
            "Select Number of Players",
            options=[2, 3, 4, 5],
            index=2, # Default 4 players
            format_func=lambda x: f"{x} Players",
            horizontal=True
        )
        
        # 5 Player Mode Banner
        if num_players == 5:
            st.markdown("""
                <div class="five-player-banner">
                    <span style="font-size: 1.6rem;">🃏</span>
                    <div>
                        <strong>5 Player Mode Active</strong><br/>
                        <span style="font-size: 0.9rem;">2♥ and 2♦ are automatically removed from the deck (48 cards total, 9 tricks per round).</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        default_names = ["Swikar", "Anwar", "Dipesh", "Mukund", "Rohan"]
        player_names = []
        
        cols = st.columns(2 if num_players > 2 else num_players)
        for i in range(num_players):
            col = cols[i % len(cols)]
            with col:
                name = st.text_input(
                    f"Player {i + 1}",
                    value=default_names[i] if i < len(default_names) else f"Player {i + 1}",
                    key=f"setup_player_{i}"
                )
                player_names.append(name)
                
        st.markdown("<br/>", unsafe_allow_html=True)
        
        if st.button("Start Game 🃏", use_container_width=True):
            valid, err_msg = validate_player_names(player_names)
            if not valid:
                st.error(err_msg)
            else:
                players = [{"id": f"p_{i+1}", "name": name.strip()} for i, name in enumerate(player_names)]
                new_game = {
                    "num_players": num_players,
                    "players": players,
                    "rounds": [],
                    "current_round": 1,
                    "round_stage": "bidding",
                    "current_calls": {},
                    "current_tricks": {},
                    "status": "active"
                }
                st.session_state.game = new_game
                save_game_state()
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# 2. MAIN GAME INTERFACE
# ==========================================
def render_game_interface():
    game = st.session_state.game
    players = game["players"]
    num_players = game["num_players"]
    rounds = game["rounds"]
    totals = calculate_totals(players, rounds)
    leaderboard = get_leaderboard(players, totals)
    
    # Top Header Bar
    top_col1, top_col2 = st.columns([3, 1])
    with top_col1:
        st.markdown(f"<h2 style='margin:0;'>Round {game['current_round']}</h2>", unsafe_allow_html=True)
        st.caption(f"{num_players} Players • Call Break")
    with top_col2:
        if st.button("New Game", type="secondary", key="top_new_game"):
            st.session_state.confirm_new_game = True

    # New Game Confirmation Prompt
    if st.session_state.confirm_new_game:
        st.warning("⚠️ You already have a game in progress. Starting a new game will replace it.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Cancel", type="secondary", use_container_width=True):
                st.session_state.confirm_new_game = False
                st.rerun()
        with c2:
            if st.button("Confirm & Start New", use_container_width=True):
                storage.clear_game()
                st.session_state.game = None
                st.session_state.confirm_new_game = False
                st.rerun()
        st.divider()

    # Leaderboard Quick Strip Cards
    st.markdown("<div style='margin-bottom: 12px;'>", unsafe_allow_html=True)
    p_cols = st.columns(len(players))
    for idx, p in enumerate(players):
        pid = p["id"]
        p_name = p["name"]
        score = totals.get(pid, 0.0)
        score_str = format_score(score)
        
        # Check if leader
        is_leader = (leaderboard[0]["id"] == pid and len(rounds) > 0 and leaderboard[0]["total_score"] > 0)
        crown = "👑 " if is_leader else ""
        card_class = "player-score-card is-leader" if is_leader else "player-score-card"
        
        with p_cols[idx]:
            st.markdown(f"""
                <div class="{card_class}">
                    <div class="player-name">{crown}{p_name}</div>
                    <div class="player-points">{score_str}</div>
                </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Main App Navigation Tabs
    tab_play, tab_score, tab_history, tab_rules, tab_settings = st.tabs([
        "🎴 Play Round", "📊 Scoreboard", "📜 History & Edit", "ℹ️ Rules", "⚙️ Settings"
    ])
    
    with tab_play:
        render_play_round_tab()
        
    with tab_score:
        render_scoreboard_tab(players, rounds, totals, leaderboard)
        
    with tab_history:
        render_history_tab(players, rounds)
        
    with tab_rules:
        render_rules_tab(num_players)
        
    with tab_settings:
        render_settings_tab(players, totals, rounds)


# ==========================================
# PLAY ROUND TAB
# ==========================================
def render_play_round_tab():
    game = st.session_state.game
    players = game["players"]
    num_players = game["num_players"]
    max_tricks = get_available_tricks(num_players)
    stage = game.get("round_stage", "bidding")
    
    st.markdown('<div class="cozy-card">', unsafe_allow_html=True)
    
    # ------------------------------------------
    # STAGE 1: BIDDING (Enter Calls)
    # ------------------------------------------
    if stage == "bidding":
        st.subheader(f"Round {game['current_round']} — Enter Calls")
        st.caption("Enter everyone's call before playing.")
        
        calls = {}
        cols = st.columns(2 if num_players > 2 else num_players)
        for i, p in enumerate(players):
            col = cols[i % len(cols)]
            with col:
                st.markdown(f"**{p['name'].upper()}**")
                call_val = st.number_input(
                    f"Call for {p['name']}",
                    min_value=1,
                    max_value=max_tricks,
                    value=game.get("current_calls", {}).get(p["id"], 3),
                    step=1,
                    key=f"call_input_{p['id']}_{game['current_round']}",
                    label_visibility="collapsed"
                )
                calls[p["id"]] = int(call_val)
                
        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("Start Round ♠️", use_container_width=True):
            valid, err = validate_calls(calls, num_players)
            if not valid:
                st.error(err)
            else:
                game["current_calls"] = calls
                game["round_stage"] = "playing"
                save_game_state()
                st.rerun()

    # ------------------------------------------
    # STAGE 2: PLAYING ROUND
    # ------------------------------------------
    elif stage == "playing":
        st.subheader(f"Round {game['current_round']} — In Progress")
        st.caption("Good luck. Play your cards!")
        
        st.markdown("<div style='margin: 15px 0;'>", unsafe_allow_html=True)
        call_cols = st.columns(len(players))
        for idx, p in enumerate(players):
            pid = p["id"]
            call_val = game.get("current_calls", {}).get(pid, "-")
            with call_cols[idx]:
                st.markdown(f"""
                    <div style="background: #10241b; border: 1px solid #d4af37; border-radius: 12px; padding: 12px; text-align: center;">
                        <div style="color: #bfa882; font-weight: 600; font-size: 0.9rem;">{p['name']}</div>
                        <div style="color: #e5c158; font-size: 1.5rem; font-weight: 800; margin-top: 4px;">Call: {call_val}</div>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("Finish Round / Enter Tricks 🏆", use_container_width=True):
            game["round_stage"] = "scoring"
            save_game_state()
            st.rerun()

    # ------------------------------------------
    # STAGE 3: SCORING (Enter Tricks Won)
    # ------------------------------------------
    elif stage == "scoring":
        st.subheader(f"Round {game['current_round']} — Enter Tricks Won")
        st.caption("How many tricks did everyone win?")
        
        tricks = {}
        preview_scores = {}
        calls = game.get("current_calls", {})
        
        cols = st.columns(2 if num_players > 2 else num_players)
        for i, p in enumerate(players):
            pid = p["id"]
            player_call = calls.get(pid, 3)
            col = cols[i % len(cols)]
            with col:
                st.markdown(f"**{p['name'].upper()}**")
                st.caption(f"Called: {player_call}")
                
                tricks_won = st.number_input(
                    f"Tricks won by {p['name']}",
                    min_value=0,
                    max_value=max_tricks,
                    value=game.get("current_tricks", {}).get(pid, player_call),
                    step=1,
                    key=f"trick_input_{pid}_{game['current_round']}",
                    label_visibility="collapsed"
                )
                tricks[pid] = int(tricks_won)
                
                # Real-time live score preview card
                score_preview = calculate_score(player_call, int(tricks_won))
                preview_scores[pid] = score_preview
                score_formatted = format_score(score_preview)
                color = "#5cdb95" if score_preview > 0 else ("#ff6b6b" if score_preview < 0 else "#f4ebd0")
                
                st.markdown(f"""
                    <div style="background: #11261c; border-radius: 8px; padding: 6px 10px; text-align: center; margin-top: 6px;">
                        <span style="font-size: 0.85rem; color: #bfa882;">Score: </span>
                        <strong style="font-size: 1.1rem; color: {color};">{score_formatted}</strong>
                    </div>
                """, unsafe_allow_html=True)
                
        # Total Tricks Live Summary Check
        sum_tricks = sum(tricks.values())
        diff = max_tricks - sum_tricks
        if diff == 0:
            st.success(f"✓ Total tricks sum: {sum_tricks}/{max_tricks}")
        else:
            st.warning(f"⚠️ Total tricks sum is {sum_tricks}/{max_tricks} ({'+' if diff < 0 else ''}{-diff} off)")

        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("Finish Round ✓", use_container_width=True):
            valid, err = validate_tricks(tricks, num_players)
            if not valid:
                st.error(err)
            else:
                round_scores = calculate_round_scores(calls, tricks)
                new_round_entry = {
                    "round_number": game["current_round"],
                    "scores": round_scores
                }
                game["rounds"].append(new_round_entry)
                game["current_round"] += 1
                game["round_stage"] = "bidding"
                game["current_calls"] = {}
                game["current_tricks"] = {}
                save_game_state()
                st.rerun()
                
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# SCOREBOARD TAB
# ==========================================
def render_scoreboard_tab(players, rounds, totals, leaderboard):
    st.subheader("Main Scoreboard")
    
    if not rounds:
        st.info("No rounds played yet. Complete Round 1 to see the scoreboard matrix!")
        return

    # Build HTML Matrix Table
    headers_html = "".join([f"<th>{p['name'].upper()}</th>" for p in players])
    
    rows_html = ""
    for r in rounds:
        r_num = r["round_number"]
        scores_by_pid = {s["player_id"]: s for s in r.get("scores", [])}
        
        cells = [f"<td><strong>R{r_num}</strong></td>"]
        for p in players:
            s_entry = scores_by_pid.get(p["id"], {})
            score_val = s_entry.get("score", 0.0)
            formatted = format_score(score_val)
            css_class = "score-positive" if score_val > 0 else ("score-negative" if score_val < 0 else "")
            
            # Subtext showing (call / won)
            call_won = f"<div style='font-size:0.75rem; opacity:0.7;'>({s_entry.get('call', '-')}/{s_entry.get('tricks_won', '-')})</div>"
            cells.append(f"<td><span class='{css_class}'>{formatted}</span>{call_won}</td>")
            
        rows_html += f"<tr>{''.join(cells)}</tr>"
        
    # Totals Row
    total_cells = ["<td><strong>TOTAL</strong></td>"]
    for p in players:
        t_val = totals.get(p["id"], 0.0)
        formatted_t = format_score(t_val)
        total_cells.append(f"<td>{formatted_t}</td>")
        
    totals_html = f"<tr>{''.join(total_cells)}</tr>"
    
    table_html = f"""
        <table class="cozy-table">
            <thead>
                <tr>
                    <th>ROUND</th>
                    {headers_html}
                </tr>
            </thead>
            <tbody>
                {rows_html}
                {totals_html}
            </tbody>
        </table>
    """
    
    st.markdown(table_html, unsafe_allow_html=True)
    
    # Leader Summary Card
    leader = leaderboard[0]
    st.markdown(f"""
        <div class="leader-card">
            <h3 style="margin:0; color:#e5c158;">Current Leader</h3>
            <div style="font-size: 2.2rem; margin: 6px 0;">👑 {leader['name']}</div>
            <div style="font-size: 1.4rem; font-weight: 800; color: #f4ebd0;">{format_score(leader['total_score'])} Points</div>
        </div>
    """, unsafe_allow_html=True)


# ==========================================
# HISTORY & EDIT TAB
# ==========================================
def render_history_tab(players, rounds):
    st.subheader("Round History & Editing")
    
    if not rounds:
        st.info("No round history recorded yet.")
        return

    game = st.session_state.game
    num_players = game["num_players"]
    max_tricks = get_available_tricks(num_players)
    
    # Undo Last Round Button
    col_undo, _ = st.columns([1, 1])
    with col_undo:
        if st.button("Undo Last Round ↩️", type="secondary", use_container_width=True):
            st.session_state.confirm_undo = True
            
    if st.session_state.get("confirm_undo", False):
        last_r_num = rounds[-1]["round_number"]
        st.warning(f"Are you sure you want to remove Round {last_r_num}?")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Cancel Undo", type="secondary", use_container_width=True):
                st.session_state.confirm_undo = False
                st.rerun()
        with c2:
            if st.button("Confirm Undo", use_container_width=True):
                rounds.pop()
                game["current_round"] = len(rounds) + 1
                game["round_stage"] = "bidding"
                game["current_calls"] = {}
                game["current_tricks"] = {}
                st.session_state.confirm_undo = False
                save_game_state()
                st.success(f"Round {last_r_num} removed.")
                st.rerun()
        st.divider()

    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Render expandable round cards in reverse order (newest first)
    for r_idx in range(len(rounds) - 1, -1, -1):
        r = rounds[r_idx]
        r_num = r["round_number"]
        
        with st.expander(f"Round {r_num}", expanded=(r_idx == len(rounds) - 1)):
            scores_by_pid = {s["player_id"]: s for s in r.get("scores", [])}
            
            # Display current round details
            grid_cols = st.columns(len(players))
            for idx, p in enumerate(players):
                pid = p["id"]
                s_entry = scores_by_pid.get(pid, {})
                s_val = s_entry.get("score", 0.0)
                formatted = format_score(s_val)
                color = "#5cdb95" if s_val > 0 else ("#ff6b6b" if s_val < 0 else "#f4ebd0")
                
                with grid_cols[idx]:
                    st.markdown(f"""
                        <div style="background:#11261c; border-radius:10px; padding:10px; text-align:center;">
                            <strong style="color:#e5c158;">{p['name']}</strong><br/>
                            <span style="font-size:0.85rem; color:#bfa882;">Call: {s_entry.get('call', '-')} | Won: {s_entry.get('tricks_won', '-')}</span><br/>
                            <strong style="font-size:1.2rem; color:{color};">{formatted}</strong>
                        </div>
                    """, unsafe_allow_html=True)
                    
            st.markdown("<br/>", unsafe_allow_html=True)
            
            # Edit Round Form
            with st.form(key=f"edit_round_form_{r_num}"):
                st.markdown(f"**Edit Round {r_num} Inputs**")
                
                new_calls = {}
                new_tricks = {}
                
                form_cols = st.columns(2 if num_players > 2 else num_players)
                for i, p in enumerate(players):
                    pid = p["id"]
                    s_entry = scores_by_pid.get(pid, {})
                    fc = form_cols[i % len(form_cols)]
                    with fc:
                        st.markdown(f"*{p['name']}*")
                        c_val = st.number_input(
                            f"Call {p['name']}",
                            min_value=1,
                            max_value=max_tricks,
                            value=s_entry.get("call", 3),
                            key=f"edit_c_{r_num}_{pid}"
                        )
                        t_val = st.number_input(
                            f"Tricks {p['name']}",
                            min_value=0,
                            max_value=max_tricks,
                            value=s_entry.get("tricks_won", s_entry.get("call", 3)),
                            key=f"edit_t_{r_num}_{pid}"
                        )
                        new_calls[pid] = int(c_val)
                        new_tricks[pid] = int(t_val)
                        
                submit_edit = st.form_submit_button(f"Save Changes to Round {r_num}")
                if submit_edit:
                    valid_c, err_c = validate_calls(new_calls, num_players)
                    valid_t, err_t = validate_tricks(new_tricks, num_players)
                    
                    if not valid_c:
                        st.error(err_c)
                    elif not valid_t:
                        st.error(err_t)
                    else:
                        updated_scores = calculate_round_scores(new_calls, new_tricks)
                        rounds[r_idx]["scores"] = updated_scores
                        save_game_state()
                        st.success(f"Round {r_num} updated successfully!")
                        st.rerun()


# ==========================================
# RULES TAB
# ==========================================
def render_rules_tab(num_players: int):
    st.subheader("Call Break Rules & Scoring")
    
    st.markdown("""
    ### 🎴 Overview
    Call Break is a trick-taking card game played with a standard 52-card deck. Spades are always the trump suit.

    ---

    ### 🗣️ 1. Calling
    Before playing a round, each player bids (calls) the number of tricks they predict they will win.
    - Minimum call: **1 trick**.
    
    ---

    ### 🎯 2. Scoring Rules

    #### ✅ Successful Call (Tricks Won ≥ Call)
    If you win at least as many tricks as your call, you get points equal to your call **plus 0.1 for every extra trick**.

    $$\\text{Score} = \\text{Call} + (\\text{Tricks Won} - \\text{Call}) \\times 0.1$$

    *Examples:*
    - Call 2, Won 2 → **+2.0 points**
    - Call 3, Won 4 → **+3.1 points**
    - Call 4, Won 6 → **+4.2 points**

    #### ❌ Failed Call (Tricks Won < Call)
    If you fail to win your called number of tricks, you lose points equal to your call.

    $$\\text{Score} = -\\text{Call}$$

    *Examples:*
    - Call 3, Won 2 → **-3.0 points**
    - Call 5, Won 3 → **-5.0 points**

    ---
    """, unsafe_allow_html=True)
    
    if num_players == 5:
        st.markdown("""
        ### 🃏 5 Player Deck Rule
        When playing with 5 players:
        - **2♥ (Two of Hearts)** and **2♦ (Two of Diamonds)** are automatically removed from the deck.
        - Total cards in deck: **48 cards**.
        - Each player receives **9 cards** per hand (45 cards total dealt).
        - Maximum tricks per round: **9 tricks**.
        """)
    else:
        st.markdown("""
        ### 🃏 4 Player Deck Rule
        Standard 52-card deck. Each player receives 13 cards per hand. Maximum tricks per round: 13 tricks.
        """)


# ==========================================
# SETTINGS & EXPORT TAB
# ==========================================
def render_settings_tab(players, totals, rounds):
    st.subheader("Game Management & Settings")
    
    # Rename Players Section
    st.markdown("### ✏️ Edit Player Names")
    with st.expander("Rename active players", expanded=False):
        with st.form(key="rename_players_form"):
            new_names = []
            cols = st.columns(2 if len(players) > 2 else len(players))
            for i, p in enumerate(players):
                col = cols[i % len(cols)]
                with col:
                    n_val = st.text_input(f"Player {i+1} Name", value=p["name"], key=f"rename_p_{p['id']}")
                    new_names.append(n_val)
                    
            if st.form_submit_button("Update Player Names ✏️"):
                valid, err = validate_player_names(new_names)
                if not valid:
                    st.error(err)
                else:
                    for i, p in enumerate(players):
                        p["name"] = new_names[i].strip()
                    save_game_state()
                    st.success("Player names updated!")
                    st.rerun()

    st.divider()

    # Share Results Section
    st.markdown("### 📤 Share Game Standings")
    summary_text = format_share_summary(players, totals, rounds)
    
    st.text_area("Shareable Score Text", value=summary_text, height=180)
    st.caption("Copy the text above to paste into WhatsApp, Telegram, or SMS.")
    
    st.divider()
    
    # End Game / Reset Options
    st.markdown("### ⚙️ Game Controls")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Finish Game 🎉", use_container_width=True):
            st.session_state.game["status"] = "finished"
            save_game_state()
            st.rerun()
            
    with c2:
        if st.button("Reset Game Data 🗑️", type="secondary", use_container_width=True):
            storage.clear_game()
            st.session_state.game = None
            st.rerun()


# ==========================================
# 3. FINAL GAME OVER SCREEN
# ==========================================
def render_final_game_screen():
    game = st.session_state.game
    players = game["players"]
    rounds = game["rounds"]
    totals = calculate_totals(players, rounds)
    leaderboard = get_leaderboard(players, totals)
    
    # Celebrate!
    st.balloons()
    
    st.markdown("""
        <div class="hero-box">
            <h1 class="cozy-title" style="font-size: 3rem;">GAME OVER 🎉</h1>
            <p class="cozy-subtitle">Congratulations to the winner!</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Leaderboard Standings
    st.markdown('<div class="cozy-card">', unsafe_allow_html=True)
    st.subheader("Final Standings")
    
    for entry in leaderboard:
        medal = entry["medal"]
        name = entry["name"]
        score_str = format_score(entry["total_score"])
        is_winner = entry["rank"] == 1
        
        bg_style = "background: linear-gradient(135deg, #3d2a10 0%, #261a0a 100%); border: 2px solid #e5c158;" if is_winner else "background: #11261c;"
        
        st.markdown(f"""
            <div style="{bg_style} border-radius: 14px; padding: 16px 20px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
                <div style="font-size: 1.3rem; font-weight: 700; color: #f4ebd0;">
                    <span style="font-size: 1.6rem; margin-right: 10px;">{medal}</span> {name}
                </div>
                <div style="font-size: 1.5rem; font-weight: 800; color: #e5c158;">
                    {score_str} PTS
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Share box
    st.markdown("### 📤 Share Final Results")
    summary = format_share_summary(players, totals, rounds)
    st.code(summary, language="text")
    
    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("Start New Game 🃏", use_container_width=True):
        storage.clear_game()
        st.session_state.game = None
        st.rerun()


# ==========================================
# MAIN APPLICATION ROUTER
# ==========================================
def main():
    init_session_state()
    game = st.session_state.game
    
    if game is None:
        render_setup_screen()
    elif game.get("status") == "finished":
        render_final_game_screen()
    else:
        render_game_interface()


if __name__ == "__main__":
    main()
