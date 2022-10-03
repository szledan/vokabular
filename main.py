import subprocess
import random


CEND      = '\33[0m'
CBOLD     = '\33[1m'
CITALIC   = '\33[3m'
CURL      = '\33[4m'
CBLINK    = '\33[5m'
CBLINK2   = '\33[6m'
CSELECTED = '\33[7m'

CBLACK  = '\33[30m'
CRED    = '\33[31m'
CGREEN  = '\33[32m'
CYELLOW = '\33[33m'
CBLUE   = '\33[34m'
CVIOLET = '\33[35m'
CBEIGE  = '\33[36m'
CWHITE  = '\33[37m'

CUR_UP_BEGIN = '\033[F'


class Vocabular:
    def __init__(self):
        print("LOG")

    def menuHelp(self):
        print("q – quit")
        print("h – show this help")
        print("? – help in the quest")

    def menuExit(self):
        subprocess.call(['setxkbmap', 'hu'])
        exit()

    def menu(self, inpt):
        for c in inpt[1:].lower():
            if c == "h":
                self.menuHelp()
            if c == "q":
                self.menuExit()
            if c == "?":
                print("TODO")


words = [
    ["da", "igen"],
    ["nu", "nem"],
    ["bine", "jó"]
]

tasks = []

for i in range(4):
    p = random.randrange(i % len(words) + 1)
    pair = words[p]
    d = random.randrange(2)
    tasks.append([d, pair[d], pair[(d + 1) % 2]])

voc = Vocabular()

MP = 3
P = 0
G = 0
for taskNr, task in enumerate(tasks):
    mp = 3
    p = P
    tlang = "hu" if task[0] > 0 else "ro"
    rlang = "ro" if task[0] > 0 else "hu"
    langs = tlang + ">" + rlang
    PS = " > "

    subprocess.call(["setxkbmap", rlang])
    term = task[1]
    res = task[2]
    print("--- " + str(taskNr) + " / " + str(len(tasks)) + " - " + langs + " ---")
    # print(CBEIGE + term + CEND)

    while True:
        itext = CBEIGE + term + CEND + PS
        inpt = input(itext)
        if len(inpt) < 1:
            continue
        if inpt[0] == ":":
            voc.menu(inpt)
        else:
            b = 0
            P = P + 1
            msg = CUR_UP_BEGIN + itext
            if inpt == res:
                G = G + 1
                b = 1
                msg = msg + CGREEN + inpt + CEND
            else:
                msg = msg + CRED + inpt + CEND
                if not P - p < MP:
                    msg = msg + " >> " + CGREEN + term + " <> " + res + CEND
            msg = msg + "\t[" + str(G) + "/" + str(P) + "]"
            print(msg)
            if b > 0:
                break

print()
print("  Great work! ")
print("    " + str(G) + "/" + str(P) )
print()

voc.menuExit()

# Import the required module for text
# to speech conversion
from gtts import gTTS

# This module is imported so that we can
# play the converted audio
import os

# The text that you want to convert to audio
mytext = 'broască țestoasă'

# Language in which you want to convert
language = 'ro'

# Passing the text and language to the engine,
# here we have marked slow=False. Which tells
# the module that the converted audio should
# have a high speed
myobj = gTTS(text=mytext, lang=language, slow=False)

# Saving the converted audio in a mp3 file named
# welcome
myobj.save("welcome.mp3")

# Playing the converted file
os.system("mplayer welcome.mp3")

