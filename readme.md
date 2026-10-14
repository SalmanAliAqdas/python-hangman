# Hangman

A command-line Hangman game written in Python. Guess the secret word one letter at a time before the drawing of the hangman is completed.

## Features
- 4 categories (Programming, Animals, Countries, Fruits and Food) with 20 words each, plus a "Surprise me" option
- Words do not repeat during a session until the whole list has been used
- Guess a single letter, or guess the whole word
- One hint per game (reveals a letter, costs 1 life)
- Six lives, with the gallows drawn in text as you make mistakes
- Mistakes in typing never cost a life: numbers, symbols, repeated letters and words of the wrong length are just rejected
- Statistics: games won and lost, current win streak and best win streak
- Automated tests (22), including a check that every word in every category can be won

## Requirements
- Python 3 installed
- No extra packages needed

## How to run
```
python hangman.py
```
If `python` is not recognized on Windows, use `py hangman.py`.

## How to play
Choose **1. Play**, pick a category, and the game shows one underscore for each letter of the secret word.

On each turn type one of these and press Enter:

| You type | What happens |
|---|---|
| a single letter, for example `e` | reveals every `e` in the word, or costs a life if there is none |
| a whole word, for example `elephant` | wins if correct, costs a life if wrong |
| `hint` | reveals one letter, costs 1 life, can be used once per game |
| `quit` | gives up and shows the word |

The word must have the same number of letters as the secret word to count as a word guess. You win by revealing every letter or guessing the word. You lose after 6 lives are gone.

Example:
```
  +---+
  |   |
  O   |
      |
      |
      |
=========

Word: e _ e _ _ _ _ _
Wrong letters: z
Lives left: 5

Your guess: hint
Hint: the word contains the letter 'h'. (It cost you 1 life.)
```

## Tips
- Start with common vowels such as `e`, `a` and `o`, then common consonants such as `r`, `t`, `n` and `s`.
- Save your hint for when you are stuck.
- A hint is not allowed on your last life.

## Running the tests
```
python -m unittest -v
```

## How it works
- `WORDS` stores the categories and their words
- `masked` builds the display such as `p _ t h _ n`
- `parse_input` decides whether you typed a letter, a word, a command or something invalid
- `play_game` runs one complete game
- Game logic is separate from keyboard input, so it can be tested automatically

## Project structure
- `hangman.py`: the game
- `test_hangman.py`: automated tests
- `.gitignore`: files Git should ignore
- `readme.md`: this file

## Possible future improvements
- Load words from a text file so players can add their own
- Difficulty levels based on word length
- A two-player mode where one person types the secret word
- A graphical or web version
