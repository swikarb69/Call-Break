"""
test_game_logic.py
Unit tests for Call Break scorekeeper game logic.
"""

import unittest
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


class TestCallBreakGameLogic(unittest.TestCase):

    def test_calculate_score_exact_calls(self):
        self.assertEqual(calculate_score(2, 2), 2.0)
        self.assertEqual(calculate_score(3, 3), 3.0)
        self.assertEqual(calculate_score(4, 4), 4.0)

    def test_calculate_score_extra_tricks(self):
        self.assertEqual(calculate_score(3, 4), 3.1)
        self.assertEqual(calculate_score(4, 6), 4.2)
        self.assertEqual(calculate_score(1, 5), 1.4)
        self.assertEqual(calculate_score(8, 11), 8.3)

    def test_calculate_score_failed_calls(self):
        self.assertEqual(calculate_score(3, 2), -3.0)
        self.assertEqual(calculate_score(5, 3), -5.0)
        self.assertEqual(calculate_score(4, 0), -4.0)

    def test_format_score(self):
        self.assertEqual(format_score(3.1), "+3.1")
        self.assertEqual(format_score(-3.0), "-3.0")
        self.assertEqual(format_score(0.0), "0.0")

    def test_available_tricks(self):
        self.assertEqual(get_available_tricks(2), 13)
        self.assertEqual(get_available_tricks(3), 13)
        self.assertEqual(get_available_tricks(4), 13)
        self.assertEqual(get_available_tricks(5), 9)

    def test_validate_player_names(self):
        # Valid names
        valid, msg = validate_player_names(["Swikar", "Rahul", "Aman", "Aryan"])
        self.assertTrue(valid)

        # Empty name
        valid, msg = validate_player_names(["Swikar", "  ", "Aman"])
        self.assertFalse(valid)
        self.assertIn("empty", msg.lower())

        # Duplicate names (case insensitive)
        valid, msg = validate_player_names(["Swikar", "Rahul", "swikar"])
        self.assertFalse(valid)
        self.assertIn("duplicate", msg.lower())

    def test_validate_calls(self):
        calls_valid = {"p1": 3, "p2": 4, "p3": 2, "p4": 4}
        valid, _ = validate_calls(calls_valid, 4)
        self.assertTrue(valid)

        calls_invalid_low = {"p1": 0, "p2": 4}
        valid, msg = validate_calls(calls_invalid_low, 4)
        self.assertFalse(valid)

        calls_invalid_high = {"p1": 14, "p2": 4}
        valid, msg = validate_calls(calls_invalid_high, 4)
        self.assertFalse(valid)

    def test_validate_tricks_4_players(self):
        # Sum of tricks in 4-player game must equal 13
        tricks_valid = {"p1": 4, "p2": 3, "p3": 2, "p4": 4}
        valid, _ = validate_tricks(tricks_valid, 4)
        self.assertTrue(valid)

        # Sum = 12 (invalid)
        tricks_invalid_sum = {"p1": 3, "p2": 3, "p3": 2, "p4": 4}
        valid, msg = validate_tricks(tricks_invalid_sum, 4)
        self.assertFalse(valid)

    def test_validate_tricks_5_players(self):
        # Sum of tricks in 5-player game must equal 9
        tricks_valid = {"p1": 2, "p2": 2, "p3": 2, "p4": 2, "p5": 1}
        valid, _ = validate_tricks(tricks_valid, 5)
        self.assertTrue(valid)

        # Sum = 10 (invalid for 5 players)
        tricks_invalid = {"p1": 2, "p2": 2, "p3": 2, "p4": 2, "p5": 2}
        valid, msg = validate_tricks(tricks_invalid, 5)
        self.assertFalse(valid)

    def test_calculate_totals_decimal_precision(self):
        players = [{"id": "p1", "name": "Swikar"}, {"id": "p2", "name": "Rahul"}]
        rounds = [
            {
                "round_number": 1,
                "scores": [
                    {"player_id": "p1", "score": 3.1},
                    {"player_id": "p2", "score": 2.0}
                ]
            },
            {
                "round_number": 2,
                "scores": [
                    {"player_id": "p1", "score": 2.0},
                    {"player_id": "p2", "score": -3.0}
                ]
            },
            {
                "round_number": 3,
                "scores": [
                    {"player_id": "p1", "score": 4.2},
                    {"player_id": "p2", "score": 3.1}
                ]
            }
        ]
        totals = calculate_totals(players, rounds)
        # p1: 3.1 + 2.0 + 4.2 = 9.3
        # p2: 2.0 - 3.0 + 3.1 = 2.1
        self.assertEqual(totals["p1"], 9.3)
        self.assertEqual(totals["p2"], 2.1)

    def test_leaderboard_sorting(self):
        players = [
            {"id": "p1", "name": "Swikar"},
            {"id": "p2", "name": "Rahul"},
            {"id": "p3", "name": "Aman"}
        ]
        totals = {"p1": 9.3, "p2": 12.1, "p3": 5.4}
        leaderboard = get_leaderboard(players, totals)
        
        self.assertEqual(leaderboard[0]["name"], "Rahul")
        self.assertEqual(leaderboard[0]["badge"], "👑")
        self.assertEqual(leaderboard[1]["name"], "Swikar")
        self.assertEqual(leaderboard[1]["badge"], "🥈")
        self.assertEqual(leaderboard[2]["name"], "Aman")
        self.assertEqual(leaderboard[2]["badge"], "🥉")

    def test_format_share_summary(self):
        players = [{"id": "p1", "name": "Swikar"}, {"id": "p2", "name": "Rahul"}]
        totals = {"p1": 9.3, "p2": 2.1}
        rounds = [{"round_number": 1}]
        
        summary = format_share_summary(players, totals, rounds)
        self.assertIn("CALL BREAK — SCOREBOARD", summary)
        self.assertIn("Swikar: +9.3 pts", summary)
        self.assertIn("Rahul: +2.1 pts", summary)


if __name__ == "__main__":
    unittest.main()
