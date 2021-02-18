import random
import sys

# List of stringed numbers
nums = ["1", "2", "3", "4", "5"]

# Game function
def guessnumbers():
    print("I am think of a number between 1 and 100")
    lucknum = random.randint(1,100)
    # print(lucknum)
    while True:
        try:
            usernum = int(input("What number are you think of: "))
        except:
            print("Please input a number")
            continue
        # only choose between 1 and 100
        if usernum > 100:
            print("Please choose between 1 and 100")
            continue
        elif lucknum == usernum:
            print("You sly devil you, " + str(lucknum))
            useranswer = input("Would you like to play again? yes/no: ")
            if useranswer == 'yes':
                print("Let's play again")
                guessnumbers()
            else:
                sys.exit()
        # Close and ascending to lucknum
        elif lucknum > usernum:
                greater = lucknum - int(nums[0])
                greater1 = lucknum - int(nums[1])
                greater2 = lucknum - int(nums[2])
                greater3 = lucknum - int(nums[3])
                greater4 = lucknum - int(nums[4])
                if usernum == greater:
                    print("Great balls of fire!")
                elif usernum == greater1:
                    print("So close!")
                elif usernum == greater2:
                    print("Getting hotter!")
                elif usernum == greater3:
                    print("Almost getting hot!")
                elif usernum == greater4:
                    print("Getting warmer!")
                else:
                    print("Choose another number!!")
        # close but decending from lucknum
        elif lucknum < usernum:
            less = lucknum + int(nums[0])
            less1 = lucknum + int(nums[1])
            less2 = lucknum + int(nums[2])
            less3 = lucknum + int(nums[3])
            less4 = lucknum + int(nums[4])
            if usernum == less:
                print("Summertime!!")
            elif usernum == less1:
                print("70 degrees!")
            elif usernum == less2:
                print("luke warm!")
            elif usernum == less3:
                print("Almost getting cold!")
            elif usernum == less4:
                print("Getting colder!")
            else:
                print("Choose another number!!")
        # only chose a number between 1 and 100
        else:
            print("Please choose between 1 and 100")

if __name__ == "__main__":
    guessnumbers()
