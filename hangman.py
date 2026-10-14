"""Hangman in the terminal.

Guess the secret word one letter at a time. Six wrong guesses and you lose.
You can also guess the whole word, or use one hint per game.
"""

import random

MAX_LIVES = 6
COMMANDS = ("hint", "quit")

WORDS = {
    "Programming": [
        "python", "variable", "function", "keyboard", "compiler", "algorithm", "database",
        "internet", "browser", "network", "software", "terminal", "package", "library",
        "debugging", "framework", "server", "website", "program", "developer",
    ],
    "Animals": [
        "elephant", "giraffe", "dolphin", "penguin", "kangaroo", "leopard", "crocodile",
        "butterfly", "squirrel", "hedgehog", "buffalo", "cheetah", "peacock", "sparrow",
        "octopus", "rabbit", "falcon", "monkey", "turtle", "camel",
    ],
    "Countries": [
        "pakistan", "malaysia", "argentina", "australia", "germany", "indonesia", "morocco",
        "norway", "portugal", "singapore", "thailand", "turkey", "uganda", "vietnam",
        "kenya", "brazil", "canada", "denmark", "ireland", "jordan",
    ],
    "Fruits and Food": [
        "mango", "pineapple", "strawberry", "watermelon", "pomegranate", "apricot", "banana",
        "cherry", "coconut", "guava", "lemon", "orange", "papaya", "peach", "biryani",
        "chocolate", "sandwich", "pancake", "noodles", "pizza",
    ],
}

GALLOWS = [
    """
  +---+
  |   |
      |
      |
      |
      |
=========""",
    """
  +---+
  |   |
  O   |
      |
      |
      |
=========""",
    """
  +---+
  |   |
  O   |
  |   |
      |
      |
=========""",
    """
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========""",
    """
  +---+
  |   |
  O   |
 /|\\  |
      |
      |
=========""",
    """
  +---+
  |   |
  O   |
 /|\\  |
 /    |
      |
=========""",
    """
  +---+
  |   |
  O   |
 /|\\  |
 / \\  |
      |
=========""",
]


class InputError(Exception):
    """Input that is not usable (it does not cost a life)."""


# ---------- Game rules (pure functions, easy to test) ----------

def pick_word(category, used=None, rng=random):
    """Pick a random word, avoiding words already used this session."""
    words = WORDS[category]
    used = used if used is not None else set()
    fresh = [word for word in words if word not in used]
    if not fresh:           # everything has been played: start the list again
        used.difference_update(words)
        fresh = words
    word = rng.choice(fresh)
    used.add(word)
    return word


def masked(word, guessed):
    """Show the word with unguessed letters as underscores: p _ t h _ n."""
    return " ".join(letter if letter in guessed else "_" for letter in word)


def is_solved(word, guessed):
    return all(letter in guessed for letter in word)


def parse_input(text, word, guessed, wrong_words):
    """Work out what the player typed.

    Returns ('letter', 'a'), ('word', 'python'), ('hint',) or ('quit',).
    Raises InputError for anything unusable.
    """
    text = text.strip().lower()
    if text == "":
        raise InputError("Please type a letter, a whole word, 'hint' or 'quit'.")
    if text == "hint":
        return ("hint",)
    if text == "quit":
        return ("quit",)
    if not text.isalpha() or not text.isascii():
        raise InputError("Use English letters only.")
    if len(text) == 1:
        if text in guessed:
            raise InputError(f"You already guessed '{text}'.")
        return ("letter", text)
    if len(text) != len(word):
        raise InputError(f"The secret word has {len(word)} letters, so '{text}' cannot be it.")
    if text in wrong_words:
        raise InputError(f"You already tried the word '{text}'.")
    return ("word", text)


def choose_hint_letter(word, guessed, rng=random):
    """Pick a letter of the word that has not been guessed yet."""
    hidden = sorted({letter for letter in word if letter not in guessed})
    return rng.choice(hidden)


# ---------- Playing one game ----------

def draw_status(word, guessed, wrong_letters, lives, show):
    show(GALLOWS[MAX_LIVES - lives])
    show(f"\nWord: {masked(word, guessed)}")
    show(f"Wrong letters: {', '.join(wrong_letters) if wrong_letters else 'none'}")
    show(f"Lives left: {lives}")


def play_game(word, rng=random, ask=input, show=print):
    """Play one game. Returns {'won': bool, 'quit': bool, 'word': str, 'wrong': int}."""
    guessed = set()
    wrong_letters = []
    wrong_words = []
    lives = MAX_LIVES
    hint_used = False

    show(f"\nThe secret word has {len(word)} letters.")
    show("Type a letter, a whole word, 'hint' (once, costs 1 life) or 'quit'.")

    while True:
        draw_status(word, guessed, wrong_letters, lives, show)
        if lives == 0:
            show(f"\nYou lost! The word was '{word}'.")
            return {"won": False, "quit": False, "word": word, "wrong": MAX_LIVES}
        if is_solved(word, guessed):
            show(f"\nYou won! The word was '{word}'. You made {MAX_LIVES - lives} wrong guess(es).")
            return {"won": True, "quit": False, "word": word, "wrong": MAX_LIVES - lives}

        try:
            action = parse_input(ask("\nYour guess: "), word, guessed, wrong_words)
        except InputError as error:
            show(f"{error} (This did not cost a life.)")
            continue

        if action[0] == "quit":
            show(f"You gave up. The word was '{word}'.")
            return {"won": False, "quit": True, "word": word, "wrong": MAX_LIVES - lives}

        if action[0] == "hint":
            if hint_used:
                show("You already used your hint for this game. (This did not cost a life.)")
            elif lives <= 1:
                show("A hint would cost your last life, so it is not allowed. (This did not cost a life.)")
            else:
                hint_used = True
                letter = choose_hint_letter(word, guessed, rng)
                guessed.add(letter)
                lives -= 1
                show(f"Hint: the word contains the letter '{letter}'. (It cost you 1 life.)")
            continue

        if action[0] == "letter":
            letter = action[1]
            guessed.add(letter)
            if letter in word:
                show(f"Good guess! '{letter}' is in the word {word.count(letter)} time(s).")
            else:
                wrong_letters.append(letter)
                lives -= 1
                show(f"Sorry, there is no '{letter}'.")
            continue

        # whole-word guess
        guess = action[1]
        if guess == word:
            guessed.update(word)
        else:
            wrong_words.append(guess)
            lives -= 1
            show(f"'{guess}' is not the word.")


# ---------- Statistics and menus ----------

def new_stats():
    return {"played": 0, "won": 0, "streak": 0, "best_streak": 0}


def update_stats(stats, result):
    if result["quit"]:
        return
    stats["played"] += 1
    if result["won"]:
        stats["won"] += 1
        stats["streak"] += 1
        stats["best_streak"] = max(stats["best_streak"], stats["streak"])
    else:
        stats["streak"] = 0


def format_stats(stats):
    if stats["played"] == 0:
        return "No finished games yet."
    return (f"Games: {stats['played']}   Won: {stats['won']}   Lost: {stats['played'] - stats['won']}\n"
            f"Current win streak: {stats['streak']}   Best win streak: {stats['best_streak']}")


def choose_category(ask=input, show=print, rng=random):
    names = list(WORDS)
    show("\nChoose a category:")
    for number, name in enumerate(names, start=1):
        show(f"  {number}. {name}")
    show(f"  {len(names) + 1}. Surprise me (any category)")
    while True:
        choice = ask("Your choice: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(names):
            return names[int(choice) - 1]
        if choice == str(len(names) + 1):
            return rng.choice(names)
        show("Please type one of the numbers shown.")


def main():
    stats = new_stats()
    used = set()
    while True:
        print()
        print("Hangman")
        print("  1. Play")
        print("  2. Statistics")
        print("  q. Quit")
        choice = input("Your choice: ").strip().lower()

        if choice == "1":
            while True:
                category = choose_category()
                print(f"\nCategory: {category}")
                word = pick_word(category, used)
                result = play_game(word)
                update_stats(stats, result)
                if result["quit"]:
                    break
                if input("\nPlay another word? (y/n): ").strip().lower() != "y":
                    break
        elif choice == "2":
            print()
            print(format_stats(stats))
            input("\nPress Enter to go back to the menu...")
        elif choice in ("q", "quit", "exit"):
            print()
            print(format_stats(stats))
            print("Thanks for playing. Goodbye!")
            break
        else:
            print("Please choose 1, 2 or q.")


if __name__ == "__main__":
    main()
