"""Automated tests. Run with:  python -m unittest -v"""

import random
import unittest

import hangman as h


def scripted(answers):
    iterator = iter(answers)
    return lambda prompt="": next(iterator)


class WordListTests(unittest.TestCase):
    def test_words_are_clean(self):
        for category, words in h.WORDS.items():
            self.assertGreaterEqual(len(words), 15, category)
            self.assertEqual(len(words), len(set(words)), f"duplicates in {category}")
            for word in words:
                self.assertTrue(word.isalpha() and word.isascii() and word.islower(), word)
                self.assertGreaterEqual(len(word), 4, word)
                self.assertNotIn(word, h.COMMANDS)

    def test_pick_word_avoids_repeats_until_list_is_used_up(self):
        rng = random.Random(1)
        used = set()
        words = [h.pick_word("Animals", used, rng) for _ in range(len(h.WORDS["Animals"]))]
        self.assertEqual(len(set(words)), len(h.WORDS["Animals"]))
        again = h.pick_word("Animals", used, rng)        # list restarts, no crash
        self.assertIn(again, h.WORDS["Animals"])


class RuleTests(unittest.TestCase):
    def test_masked(self):
        self.assertEqual(h.masked("python", set()), "_ _ _ _ _ _")
        self.assertEqual(h.masked("python", {"p", "o"}), "p _ _ _ o _")
        self.assertEqual(h.masked("apple", {"p"}), "_ p p _ _")

    def test_is_solved(self):
        self.assertFalse(h.is_solved("tea", {"t", "e"}))
        self.assertTrue(h.is_solved("tea", {"t", "e", "a"}))

    def test_gallows_stages(self):
        self.assertEqual(len(h.GALLOWS), h.MAX_LIVES + 1)
        self.assertEqual(len(set(h.GALLOWS)), h.MAX_LIVES + 1)

    def test_parse_input_valid(self):
        self.assertEqual(h.parse_input(" A ", "python", set(), []), ("letter", "a"))
        self.assertEqual(h.parse_input("PYTHON", "python", set(), []), ("word", "python"))
        self.assertEqual(h.parse_input("hint", "python", set(), []), ("hint",))
        self.assertEqual(h.parse_input("Quit", "python", set(), []), ("quit",))

    def test_parse_input_invalid(self):
        for bad in ["", "   ", "1", "a1", "!", "é", "ab", "toolongword"]:
            with self.assertRaises(h.InputError, msg=bad):
                h.parse_input(bad, "python", set(), [])
        with self.assertRaises(h.InputError):
            h.parse_input("a", "python", {"a"}, [])
        with self.assertRaises(h.InputError):
            h.parse_input("kitten", "python", set(), ["kitten"])

    def test_hint_letter_is_always_unguessed(self):
        rng = random.Random(2)
        for _ in range(100):
            letter = h.choose_hint_letter("banana", {"b", "n"}, rng)
            self.assertEqual(letter, "a")
        self.assertIn(h.choose_hint_letter("cat", set(), rng), "cat")


class GameTests(unittest.TestCase):
    def play(self, word, answers, seed=0):
        output = []
        result = h.play_game(word, random.Random(seed), scripted(answers), output.append)
        return result, "\n".join(output)

    def test_win_by_letters(self):
        result, text = self.play("tea", ["t", "e", "a"])
        self.assertTrue(result["won"])
        self.assertEqual(result["wrong"], 0)
        self.assertIn("You won!", text)

    def test_win_with_some_mistakes(self):
        result, text = self.play("tea", ["z", "t", "x", "e", "a"])
        self.assertTrue(result["won"])
        self.assertEqual(result["wrong"], 2)
        self.assertIn("Wrong letters: z, x", text)

    def test_loss_after_six_wrong_letters(self):
        result, text = self.play("tea", list("zxqwjk"))
        self.assertFalse(result["won"])
        self.assertEqual(result["wrong"], 6)
        self.assertIn("You lost! The word was 'tea'.", text)

    def test_correct_whole_word_wins(self):
        result, _ = self.play("python", ["python"])
        self.assertTrue(result["won"])
        self.assertEqual(result["wrong"], 0)

    def test_wrong_whole_word_costs_a_life_and_cannot_be_repeated(self):
        result, text = self.play("python", ["bottle", "bottle", "python"])
        self.assertTrue(result["won"])
        self.assertEqual(result["wrong"], 1)
        self.assertIn("already tried the word", text)

    def test_bad_input_costs_nothing(self):
        result, text = self.play("tea", ["", "7", "?", "t", "t", "elephant", "e", "a"])
        self.assertTrue(result["won"])
        self.assertEqual(result["wrong"], 0)
        self.assertEqual(text.count("did not cost a life"), 5)   # "", "7", "?", repeated "t", wrong-length word

    def test_quit(self):
        result, text = self.play("tea", ["quit"])
        self.assertTrue(result["quit"])
        self.assertFalse(result["won"])
        self.assertIn("'tea'", text)

    def test_hint_costs_one_life_and_works_once(self):
        result, text = self.play("tea", ["hint", "hint", "t", "e", "a"])
        self.assertTrue(result["won"])
        self.assertEqual(result["wrong"], 1)
        self.assertEqual(text.count("Hint: the word contains"), 1)
        self.assertIn("already used your hint", text)

    def test_hint_not_allowed_on_last_life(self):
        # five wrong letters leaves one life; a hint would kill the player, so it is refused
        result, text = self.play("tea", list("zxqwj") + ["hint", "t", "e", "a"])
        self.assertTrue(result["won"])
        self.assertIn("last life", text)
        self.assertEqual(result["wrong"], 5)

    def test_hint_that_reveals_last_missing_letter_wins(self):
        result, text = self.play("tea", ["t", "e", "hint"])
        self.assertTrue(result["won"])
        self.assertEqual(result["wrong"], 1)

    def test_every_word_can_be_won_by_guessing_its_letters(self):
        for words in h.WORDS.values():
            for word in words:
                result, _ = self.play(word, sorted(set(word)))
                self.assertTrue(result["won"], word)


class StatsAndMenuTests(unittest.TestCase):
    def test_stats_and_streaks(self):
        stats = h.new_stats()
        for won in [True, True, False, True, True, True]:
            h.update_stats(stats, {"won": won, "quit": False})
        h.update_stats(stats, {"won": False, "quit": True})       # quitting is ignored
        self.assertEqual(stats, {"played": 6, "won": 5, "streak": 3, "best_streak": 3})
        self.assertIn("Best win streak: 3", h.format_stats(stats))

    def test_empty_stats(self):
        self.assertEqual(h.format_stats(h.new_stats()), "No finished games yet.")

    def test_choose_category(self):
        quiet = lambda text: None
        self.assertEqual(h.choose_category(scripted(["2"]), quiet), "Animals")
        self.assertEqual(h.choose_category(scripted(["x", "0", "9", "1"]), quiet), "Programming")
        surprise = h.choose_category(scripted(["5"]), quiet, random.Random(3))
        self.assertIn(surprise, h.WORDS)


if __name__ == "__main__":
    unittest.main()
