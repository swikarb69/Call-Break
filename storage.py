"""
storage.py
Local JSON storage mechanism for persisting Call Break game state.
"""

import json
import os
from typing import Dict, Any, Optional

DEFAULT_FILEPATH = "callbreak_game.json"


def save_game(game_state: Dict[str, Any], filepath: str = DEFAULT_FILEPATH) -> bool:
    """
    Saves the game dictionary to a local JSON file.
    Returns True if successful, False otherwise.
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(game_state, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving game state to {filepath}: {e}")
        return False


def load_game(filepath: str = DEFAULT_FILEPATH) -> Optional[Dict[str, Any]]:
    """
    Loads and returns the game state dictionary from local JSON file.
    Returns None if file does not exist or is corrupted.
    """
    if not os.path.exists(filepath):
        return None
        
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Basic schema check
            if isinstance(data, dict) and "players" in data and "rounds" in data:
                return data
            return None
    except Exception as e:
        print(f"Error loading game state from {filepath}: {e}")
        return None


def clear_game(filepath: str = DEFAULT_FILEPATH) -> bool:
    """
    Removes the local JSON save file.
    Returns True if removed or already absent, False on error.
    """
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            return True
        except Exception as e:
            print(f"Error removing {filepath}: {e}")
            return False
    return True


def has_saved_game(filepath: str = DEFAULT_FILEPATH) -> bool:
    """
    Checks if a valid saved game file exists.
    """
    return load_game(filepath) is not None
