import subprocess
import random
import csv
import sys
import os
import datetime
import hashlib
import getpass
import readline
from pynput import keyboard as KB


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
CGREY    = '\33[90m'
CRED2    = '\33[91m'
CGREEN2  = '\33[92m'
CYELLOW2 = '\33[93m'
CBLUE2   = '\33[94m'
CVIOLET2 = '\33[95m'
CBEIGE2  = '\33[96m'
CWHITE2  = '\33[97m'
CUR_UP_BEGIN = '\033[F'
SAVE_CUR_POS = '\033[s'
LOAD_CUR_POS = '\033[u'


def saveCurPos():
    print(SAVE_CUR_POS, end="")
    sys.stdout.flush()


def loadCurPos():
    print(LOAD_CUR_POS, end="")
    sys.stdout.flush()


def quit():
    exit()


class Log:
    errorOn = True
    warningOn = True
    def e(msg):
        if Log.errorOn:
            print(CRED + "[ERR]: " + msg + CEND)
    def w(msg):
        if Log.warningOn:
            print(CBEIGE + "[WAR]: " + msg + CEND)
    def fileExists(filename):
        if not os.path.exists(filename):
            Log.e("The '" + filename + "' file does not exist!")
            return False
        return True


class KeyPress:
    _hotkeys = []
    def __init__(self):
        self._listener = KB.Listener(on_press=self._on_press, on_release=self._on_release)
        self._listener.start()

    def __del__(self):
        self._listener.stop()

    def _on_press(self, key):
        for hotkey in self._hotkeys:
            if any([key in hkey for hkey in hotkey["keys"]]):
                hotkey["set"].add(key)
                if any(all(k in hotkey["set"] for k in hkey) for hkey in hotkey["keys"]):
                    hotkey["func"]()

    def _on_release(self, key):
        for hotkey in self._hotkeys:
            try:
                hotkey["set"].remove(key)
            except KeyError:
                pass

    def hotkey(self, keys: list, func):
        self._hotkeys.append({ "keys": keys, "func": func, "set" : set() })


class CSVManager:
    _csvfile=""

    def __init__(self, csvfile):
        self._csvfile = csvfile

    def decomment(csv):
        for row in csv:
            raw = row.split('#')[0].strip()
            if raw:
                yield raw

    def csvfile():
        return self._csvfile

    def makeIfNotExist(self):
        if not os.path.exists(self._csvfile):
            open(self._csvfile, 'w').close()
        return self

    def parse(self):
        rows = []
        if Log.fileExists(self._csvfile):
            with open(self._csvfile, newline='') as csvfile:
                csvReader = csv.reader(CSVManager.decomment(csvfile), delimiter=';')
                for row in csvReader:
                    rows.append(row)
                csvfile.close()
        if len(rows) < 1:
            Log.w("The output list is empty on '" + self._csvfile + "' file.")
        return rows

    def append(self, row: list):
        if Log.fileExists(self._csvfile):
            with open(self._csvfile, 'a') as csvfile:
                csvWriter = csv.writer(csvfile, delimiter=';')
                csvWriter.writerow(row)
                csvfile.close()

    # TODO: def remove(csvfile, item, column: int, all = False):

    #def change(csvfile, key, column: int, value):


class UserManager:
    __noUser = "UNKNOW"

    _user = __noUser
    _users = []
    _userfile = ""
    _userlogfile = ""

    def __init__(self, userfile, userlogfile):
        self._userfile = userfile
        self._userlogfile = userlogfile
        self._userMgr = CSVManager(userfile).makeIfNotExist()
        self._userLogMgr = CSVManager(userlogfile).makeIfNotExist()
        self._users = self._userMgr.parse()

    def userlist(self):
        return self._users

    def userlogMgr(self):
        return self._userLogMgr

    def trylogin(self, userName, password = ""):
        return (userName, password) in [(item[0], item[1]) for item in self._users]

    def login(self, userName, password = ""):
        passwordMD5 = "" if len(password) < 1 else hashlib.md5(password.encode()).hexdigest()
        successed = (userName, passwordMD5) in [(item[0], str(item[1])) for item in self._users]
        nowStr = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        self._userLogMgr.append(["LOGIN", int(successed), userName, nowStr])
        return successed

    def lastLogin(self):
        rows = self._userLogMgr.parse()
        for row in reversed(rows):
            if row[0] == "LOGIN" and row[1] == "1":
                return row
        return []

    def add(self, username = "", password = ""):
        usedNames = [item[0] for item in self._users]
        def checkName(name):
            if name == "" or not name.replace('_', '').isalnum() or not name.isascii():
                return 1
            if userName in [item[0] for item in usedNames]:
                return 2
            return 0
        userName = username
        usable = checkName(userName)
        passWord = password
        same = False

        if username == "":
            print("Add new user.")
            i = 0
            while True:
                userName = input(" Username: ")
                readline.remove_history_item(readline.get_current_history_length() - 1)
                usable = checkName(userName)
                if usable == 1:
                    print(CRED + "Please use alphanumeric ascii or underscore characters." + CEND)
                elif usable == 2:
                    print(CRED + "Username is already used or empty!" + CEND)
                else:
                    break
                if i > 1:
                    return False
                i = i + 1

            for i in range(3):
                password1 = getpass.getpass(" Password 1.: ")
                password2 = getpass.getpass(" Password 2.: ")
                same = password1 == password2
                if same:
                    passWord = password1
                    break
                else:
                    print(CRED + "Passwords not equal!" + CEND)
        if usable > 0 or not same:
            return False

        passwordMD5 = "" if len(passWord) < 1 else hashlib.md5(passWord.encode()).hexdigest()
        row = [userName, passwordMD5]
        self._userMgr.append(row)
        self._users = self._userMgr.parse()
        # TODO: create user-spec files
        if username == "":
            print("The '" + userName + "' user added.")
        return True

    #def remove(self, userName)
    #def rename(self, oldUserName, newUserName)


class Menu:
    def __init__(self, vok):
        class Completer:
            def __init__(self, logic):
                self.logic = logic

            def traverse(self, tokens, tree):
                if tree is None:
                    return []
                elif len(tokens) == 0:
                    return []
                if len(tokens) == 1:
                    return [ x + ' ' for x in tree if x.startswith(tokens[0]) ]
                else:
                    if tokens[0] in tree.keys():
                        return self.traverse(tokens[1:],tree[tokens[0]])
                    else:
                        return []
                return []

            def complete(self, text, state):
                try:
                    tokens = readline.get_line_buffer().split()
                    if not tokens or readline.get_line_buffer()[-1] == ' ':
                        tokens.append('')
                    results = self.traverse(tokens, self.logic) + [None]
                    #print("results: ", results)
                    return results[state]
                except Exception as e:
                    print(e)

        logic = {
            'quit': None,
            'help': None,
            'user':
                    {
                    'list':None,
                    'switch':None,
                    'add':None
                    }
            }

        completer = Completer(logic)
        readline.set_completer(completer.complete)
        readline.parse_and_bind('"\C-r": reverse-search-history')
        readline.parse_and_bind("set bell-style none")
        readline.parse_and_bind('tab: complete')
        self._vok = vok

    def _adv(s):
        if len(s) < 1:
            return '', s
        return s[0], s[1:]

    def menuExit(self):
        self._vok.logout()
        quit()

    def menuHelp(self):
        def _p(k, m):
            print(k + CGREY + m + CEND)
        _p(":q", " – quit")
        _p(":h", " – show this help")
        #_p(":l", " – manage languages – ':ln [hu]' list/set native language; ':lc en' choosing the language to learn")
        _p(":u", " – manage users – ':ul' list; ':uc' change; ':un' add new; ':ud' delete; ':um' rename")

    def menuManageLanguages(self):
        c, cmd = Menu._adv(cmd)
#        if c == "n":

    def menuManageUsers(self, cmd):
        c, cmd = Menu._adv(cmd)
        if c == "l":
            lastLoggedUsers = []
            users = self._vok._um.userlist()
            userlog = self._vok._um.userlogMgr().parse()
            for user in users:
                for row in reversed(userlog):
                    if row[0] == "LOGIN" and row[1] == "1" and row[2] == user[0]:
                        lastLoggedUsers.append([user[0], row[3]])
                        break
            print("User\tLast login")
            for r in lastLoggedUsers:
                print(r[0] + "\t" + r[1])
        if c == "c":
            self._vok.logout()
            self._vok.login(trylast=False)
        if c == "n":
            self._vok._um.add()

    def menu(self, cmd):
        c, cmd = Menu._adv(cmd)
        if c == "q":
            self.menuExit()
        if c == "h":
            self.menuHelp()
        if c == "l":
            self.menuManageLanguages(cmd)
        if c == "u":
            self.menuManageUsers(cmd)


class Vokabular:
    __ps = "> "
    __dataDirName = "data"
    __mainConfigDirName = ".config"
    __usersCSVName = "users"
    __usersLogCSVName = "userslog"

    _ps = __ps

    def __init__(self, dataDir = ""):
        print(CBOLD + " --== Vocabular 1.0 ==-- " + CEND)
        print(CGREY + "(C) 2022. Szilárd LEDÁN (szledan@gmail.com)" + CEND)
        print()
        self._kp = KeyPress()
        self._kp.hotkey([{KB.Key.alt, KB.KeyCode(char='s')}], saveCurPos)
        self._kp.hotkey([{KB.Key.alt, KB.KeyCode(char='l')}], loadCurPos)
        self._menu = Menu(self)

        self._rootDir = os.path.abspath(os.getcwd())
        self._dataDir = dataDir if len(dataDir) > 0 else os.path.join(self._rootDir, self.__dataDirName)
        self._mainConfigDir = os.path.join(self._dataDir, self.__mainConfigDirName)
        self._usersCSV = os.path.join(self._mainConfigDir, self.__usersCSVName)
        self._usersLogCSV = os.path.join(self._mainConfigDir, self.__usersLogCSVName)

        if not os.path.exists(self._dataDir):
            Log.w("The '" + self.__dataDirName + "' directory does not exist.")
            os.makedirs(self._dataDir)
            Log.w("Created it.")
        if not os.path.exists(self._mainConfigDir):
            os.makedirs(self._mainConfigDir)

        self._um = UserManager(self._usersCSV, self._usersLogCSV)

    def init(self):
        #! TODO: user spec load
        print("Welcome!")
        print(CGREY + "Type ':h' for help." + CEND)
        print()

    def logout(self):
        subprocess.call(['setxkbmap', 'hu'])
        print("Goodbye!")

    def login(self, trylast=True):
        if len(self._um._users) < 1:
            if not self._um.add():
                quit()

        loggedin = False
        if trylast and len(self._um.lastLogin()) > 0:
            lastUser = self._um.lastLogin()[2]
            print("Try login '" + lastUser + "'...")
            loggedin = self._um.trylogin(lastUser)
            if not loggedin:
                print(CRED + "FAIL" + CEND)

        probe = 3
        while not loggedin:
            print("Login")
            if probe < 1:
                quit()
            probe = probe - 1
            userName = input(" Username: ")
            password = getpass.getpass(" Password: ")
            loggedin = self._um.login(userName, password)
            if not loggedin:
                print(CRED + "FAIL" + CEND)
        print(CGREEN + "SUCCESS" + CEND)
        print()

        print("Loading...")
        print()
        self.init()

    def loop(self):
        while True:
            cmd = ""
            try:
                cmd = input(self._ps)
            except EOFError:
                print()
                cmd = ":q"
            if len(cmd) < 1:
                continue
            if cmd[0] == ":":
                self._menu.menu(cmd[1:])
            else:
                print(cmd)


def main():
    vok = Vokabular()
    vok.login()
    vok.loop()


if __name__ == "__main__":
    main()


#################################################################################x

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
            vok.menu(inpt)
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

vok.menuExit()

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

