"""
game_logic.py
Pure game logic functions for Call Break scorekeeping.
Includes Call Break scoring calculations, deck/trick limits, input validation,
total calculations using Decimal for precision, and leaderboard sorting.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Tuple


def calculate_score(call: int, tricks_won: int) -> float:
    """
    Calculates the score for a single player in a round.
    
    Rules:
    - If tricks_won >= call: score = call + (tricks_won - call) * 0.1
    - If tricks_won < call: score = -call
    
    Returns float rounded to exactly 1 decimal place.
    """
    call_dec = Decimal(str(call))
    tricks_dec = Decimal(str(tricks_won))
    
    if tricks_won >= call:
        extra_tricks = tricks_dec - call_dec
        score = call_dec + (extra_tricks * Decimal('0.1'))
    else:
        score = -call_dec
        
    # Round to 1 decimal place precisely
    score_rounded = score.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
    return float(score_rounded)


def format_score(score: float) -> str:
    """
    Formats score float to 1 decimal place with explicit + / - sign.
    Examples: +3.1, -4.0, 0.0
    """
    val = Decimal(str(round(score, 1))).quantize(Decimal('0.1'))
    if val > 0:
        return f"+{val}"
    elif val == 0:
        return "0.0"
    else:
        return f"{val}"


def get_available_tricks(num_players: int) -> int:
    """
    Returns total available tricks per hand based on player count.
    - 4 players: 52 cards / 4 = 13 tricks
    - 5 players: 48 cards (2♥ & 2♦ removed) / 5 = 9 tricks (45 cards dealt)
    - 2 players: 13 tricks
    - 3 players: 13 tricks
    """
    if num_players == 5:
        return 9
    return 13


def validate_player_names(names: List[str]) -> Tuple[bool, str]:
    """
    Validates player names list.
    - Names cannot be empty after trimming.
    - Names must be unique (case-insensitive check).
    """
    trimmed = [name.strip() for name in names]
    
    for idx, name in enumerate(trimmed):
        if not name:
            return False, f"Player {idx + 1} name cannot be empty."
            
    seen = set()
    for name in trimmed:
        name_lower = name.lower()
        if name_lower in seen:
            return False, f"Duplicate player name found: '{name}'. Player names must be unique."
        seen.add(name_lower)
        
    return True, ""


def validate_calls(calls: Dict[str, int], num_players: int) -> Tuple[bool, str]:
    """
    Validates player calls.
    - Minimum call: 1
    - Maximum call: total available tricks for player count.
    """
    max_tricks = get_available_tricks(num_players)
    
    for player_id, call in calls.items():
        if call is None or not isinstance(call, int):
            return False, "All players must enter a valid call number."
        if call < 1:
            return False, "Minimum call is 1 trick."
        if call > max_tricks:
            return False, f"Maximum call cannot exceed {max_tricks} tricks."
            
    return True, ""


def validate_tricks(tricks: Dict[str, int], num_players: int) -> Tuple[bool, str]:
    """
    Validates tricks won per player.
    - Tricks won must be between 0 and total available tricks.
    - Sum of tricks won across all players should equal available_tricks.
    """
    max_tricks = get_available_tricks(num_players)
    total_won = 0
    
    for player_id, won in tricks.items():
        if won is None or not isinstance(won, int):
            return False, "All players must enter valid tricks won."
        if won < 0:
            return False, "Tricks won cannot be negative."
        if won > max_tricks:
            return False, f"Tricks won for a single player cannot exceed {max_tricks}."
        total_won += won
        
    if total_won != max_tricks:
        return False, f"Total tricks won across all players ({total_won}) must equal {max_tricks} for a round."
        
    return True, ""


def calculate_round_scores(calls: Dict[str, int], tricks: Dict[str, int]) -> List[Dict[str, Any]]:
    """
    Calculates scores for all players in a round given their calls and tricks won.
    Returns list of score entries.
    """
    results = []
    for player_id, call in calls.items():
        tricks_won = tricks.get(player_id, 0)
        score = calculate_score(call, tricks_won)
        results.append({
            "player_id": player_id,
            "call": call,
            "tricks_won": tricks_won,
            "score": score
        })
    return results


def calculate_totals(players: List[Dict[str, Any]], rounds: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculates total cumulative scores for all players from the list of rounds.
    Guarantees floating point precision using Decimal.
    """
    totals_dec: Dict[str, Decimal] = {p["id"]: Decimal('0.0') for p in players}
    
    for r in rounds:
        for entry in r.get("scores", []):
            pid = entry["player_id"]
            if pid in totals_dec:
                score_val = Decimal(str(entry.get("score", 0.0)))
                totals_dec[pid] += score_val
                
    return {
        pid: float(val.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
        for pid, val in totals_dec.items()
    }


def get_leaderboard(players: List[Dict[str, Any]], totals: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Sorts players by total score in descending order and assigns badges.
    """
    leaderboard = []
    for p in players:
        pid = p["id"]
        score = totals.get(pid, 0.0)
        leaderboard.append({
            "id": pid,
            "name": p["name"],
            "total_score": score
        })
        
    # Sort descending by score
    leaderboard.sort(key=lambda x: x["total_score"], reverse=True)
    
    # Assign ranks and badges
    badges = ["🥇", "🥈", "🥉"]
    for idx, p in enumerate(leaderboard):
        p["rank"] = idx + 1
        if idx == 0:
            p["badge"] = "👑"
            p["medal"] = "🥇"
        elif idx < len(badges):
            p["badge"] = badges[idx]
            p["medal"] = badges[idx]
        else:
            p["badge"] = f"#{idx + 1}"
            p["medal"] = f"#{idx + 1}"
            
    return leaderboard


def format_share_summary(players: List[Dict[str, Any]], totals: Dict[str, float], rounds: List[Dict[str, Any]]) -> str:
    """
    Formats game results into a copyable text block for messaging/sharing.
    """
    leaderboard = get_leaderboard(players, totals)
    num_rounds = len(rounds)
    
    lines = [
        "🃏 CALL BREAK — SCOREBOARD",
        f"Played {num_rounds} Round{'s' if num_rounds != 1 else ''}",
        "----------------------------"
    ]
    
    for entry in leaderboard:
        medal = entry["medal"]
        name = entry["name"]
        score = entry["total_score"]
        score_str = format_score(score)
        lines.append(f"{medal} {name}: {score_str} pts")
        
    lines.append("----------------------------")
    lines.append("Great game! ♠️♥️♦️♣️")
    return "\n".join(lines)
