import sys

def madlib():
    adjective = input("Add an adjective: ")
    noun = input("add a noun: ")
    pronoun = input("add a pronoun: ")



    a = "I like to skateboard to my {0} friend named Josh.".format(adjective)
    b = "We always go the skateboard {0},".format(noun)
    c = "Josh and {0} are best of friends!".format(pronoun)

    print(a + " " + b + " " + c)
    user = input("Would you like to try again? [yes or no] ")
    if user == 'yes':
        madlib()
    else:
        sys.exit()


if __name__ == "__main__":
    madlib()
