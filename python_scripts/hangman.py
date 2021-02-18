import random
import time
import sys

# function to start the game
def beginning():
    player = input("Hangman, would you like to play? Yes or No: ")
    if player == 'yes':
        beginning.name = input("What is your name? ")
        print("Good Luck! ", beginning.name)
    elif player == 'no':
        sys.exit()
    else:
        beginning()

beginning()
# Here the user is asked to enter the name first


# Secret words
words = ['rainmaker', 'computers', 'romans', 'skyline',
         'thanksgiving', 'rottweiler', 'networking', 'japan',
         'sandwich', 'paper', 'blackboard', 'salad']

# Function will choose one random
# word from this list of words
word = random.choice(words)

# any number of turns can be used here
turns = 12

# Game Instructions
print("Guess the word by choosing a letter or word")
print(beginning.name + ", you have", + turns, 'guesses to reveal the word')

# variable 
guesses = ''

# time to read Game Instructions
time.sleep(5)

# Hangman Game Code
while turns > 0:

    # counts the number of times a user fails
    failed = 0

    # all characters from the input
    # word taking one at a time.
    for char in word:

        # comparing that character with
        # the character in guesses
        if char in guesses:
            print(char)

        else:
            print("_")

            # for every failure 1 will be
            # incremented in failure
            failed += 1

    if failed == 0:
        # user will win the game if failure is 0
        # and 'You Win' will be given as output
        print("You Win")

        # this print the correct word
        print("The word is: ", word)
        break


    # The choice of guessing the word or choosing letters
    # user input between word or letter
    letterorword = input(beginning.name + ", guess the word or choose a letter: "
                                          "word or letter: ")
    # using the word option to guess the word
    if letterorword == 'word':
        print("If you guess incorrect, you will lose the game!")
        playerword = input("Please guess the word: ")
        if playerword == word:
            print("You guess the word correctly " + beginning.name)
            print("You Win!")
            # Asking to play again
            again = input("Would you like to play again " + beginning.name + "?: ")
            if again == 'yes':
                # start at the beginning function
                beginning()
            else:
                # Exit the game
                print("Enjoy your day!")
                sys.exit()
        else:
            # start at the beginning function
            print("You Lose!")
            beginning()
    elif letterorword == 'letter':
        # if user has input the wrong alphabet then
        # it will ask user to enter another alphabet
        guess = input("choose a letter: ")

        # every input character will be stored in guesses
        guesses += guess

        # check input with the character in word
        if guess not in word:

            turns -= 1

            # if the character doesn’t match the word
            # then “Wrong” will be given as output
            print("Wrong")

            # this will print the number of
            # turns left for the user
            print("You have", + turns, 'more guesses')

            if turns == 0:
                print("You Loose")
