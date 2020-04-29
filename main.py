from guizero import App, PushButton, Text, TextBox, Combo


def get_bit(value, n):
    return ((value >> n & 1) != 0)

def set_bit(value, n):
    return value | (1 << n)

def clear_bit(value, n):
    return value & ~(1 << n)


colOff = (255, 255, 255)
colOn  = (100, 100, 100)

offset = 0x2800
current = 0x00
char = "N"
text = ""

dispModes = ["numbers", "numbers starting at 0", "braille", "none", "position", "position short", "on or off", "dot or none"]
dispMode = 0

positionText = ["Top Left", "Middle Left", "Bottom Left", "Top Right", "Middle Right", "Bottom Right"]
positionShortText = ["TL", "ML", "BL", "TR", "MR", "BR"]
positionText8 = ["Top Left", "Top Middle Left", "Bottom Middle Left", "Top Right", "Top Middle Right", "Bottom Middle Right", "Bottom Left", "Bottom Right"]
positionShortText8 = ["TL", "TML", "BML", "TR", "TMR", "BMR", "BL", "BR"]

brailleType = "English Braille"
brailleTypes = {
    "English Braille": {
        " ": "⠀", #There is a different charector for space
        "1": "⠁",
        "a": "⠁",
        "2": "⠃",
        "b": "⠃",
        "3": "⠉",
        "c": "⠉",
        "4": "⠙",
        "d": "⠙",
        "5": "⠑",
        "e": "⠑",
        "6": "⠋",
        "f": "⠋",
        "7": "⠛",
        "g": "⠛",
        "8": "⠓",
        "h": "⠓",
        "9": "⠊",
        "i": "⠊",
        "0": "⠚",
        "j": "⠚",
        "k": "⠅",
        "l": "⠇",
        "m": "⠍",
        "n": "⠝",
        "o": "⠕",
        "p": "⠏",
        "q": "⠟",
        "r": "⠗",
        "s": "⠎",
        "t": "⠞",
        "u": "⠥",
        "v": "⠧",
        "x": "⠭",
        "y": "⠽",
        "z": "⠵",
        "and": "",
        "for": "",
        "of": "",
        "the": "",
        "with": "",
        "ch": "",
        "gh": "",
        "sh": "",
        "th": "",
        "wh": "",
        "ed": "",
        "er": "",
        "ou": "",
        "ow": "",
        "w": "⠺",
        ",": "⠂",
        "-ea-": "⠂",
        ";": "⠆",
        "-bb-": "⠆",
        ":": "⠒",
        "-cc-": "⠒",
        ".": "⠲",
        "-dd-": "⠲",
        "en": "⠢",
        "!": "⠖",
        "-ff-": "⠖",
        "to": "⠖",
        "(": "⠶",
        ")": "⠶",
        "-gg-": "⠶",
        "?": "⠦",
        '"': "⠦", #66 quotes
        "in": "⠔",
        '"': "⠴", #99 quotes
        "by": "⠴",
        "'": "⠄",
        "-": "⠤",
        "com-": "⠤"
    }
}

def updateChar():
    global char
    char = chr(offset+current)
    currentText.value = char

def flipDot(n):
    global current
    if get_bit(current, n):
        current = clear_bit(current, n)
        buttons[n].bg = colOff
    else:
        current = set_bit(current, n)
        buttons[n].bg = colOn
    updateChar()
    updateDispMode()

def setDot(n, v):
    global current
    if bool(v):
        current = set_bit(current, n)
        buttons[n].bg = colOn
    else:
        current = clear_bit(current, n)
        buttons[n].bg = colOff
    updateChar()


def toggle68(to=None):
    if to == None:
        to = not buttons[6].visible
    buttons[6].visible = to
    buttons[7].visible = to
    setDot(6, False)
    setDot(7, False)
    updateDispMode()

def typeIt(c=None):
    global text
    if c == None:
        c = char
    text += c
    outputText.value = text

def backspace():
    global text
    text = text[:-1]
    outputText.value = text

def textChanged():
    global text
    if text != outputText.value:
        text = ""
        for i in range(len(outputText.value)):
            c = outputText.value[i]
            if ord(c) & 0xFF00 == 0x2800:
                text += chr(ord(c) & 0xFFFF)
            elif c.lower() in brailleTypes[brailleType]:
                text += brailleTypes[brailleType][c.lower()]
            elif c in ["\n"]:
                text += c
        outputText.value = text

def changeDispMode(n=None):
    global dispMode
    if n == None:
        dispMode = (dispMode + 1) % len(dispModes)
    else:
        dispMode = n
    updateDispMode()

def updateDispMode():
    m = dispModes[dispMode]
    buttonDispMode.text = "Button display:\n{}".format(m)
    if   m == "numbers":
        for i in range(8):
            buttons[i].text = str(i+1)
    elif m == "numbers starting at 0":
        for i in range(8):
            buttons[i].text = str(i)
    elif m == "braille":
        for i in range(8):
            buttons[i].text = chr(0x2800 + (2^i))
    elif m == "none":
        for i in range(8):
            buttons[i].text = ""
    elif m == "position":
        if buttons[6].visible:
            for i in range(8):
                buttons[i].text = positionText8[i]
        else:
            for i in range(6):
                buttons[i].text = positionText[i]
    elif m == "position short":
        if buttons[6].visible:
            for i in range(8):
                buttons[i].text = positionShortText8[i]
        else:
            for i in range(6):
                buttons[i].text = positionShortText[i]
    elif m == "on or off":
        for i in range(8):
            if get_bit(current, i):
                buttons[i].text = "On"
            else:
                buttons[i].text = "Off"
    elif m == "dot or none":
        for i in range(8):
            if get_bit(current, i):
                buttons[i].text = "Dot"
            else:
                buttons[i].text = ""
    else:
        for i in range(len(buttons)):
            buttons[i].text = "Invalid button disp"

def changeBrailleType(to):
    global brailleType
    brailleType = to
    


app = App(title="Braille Writer", layout="grid")  


currentText = Text(app, text=char, size=64, grid=[0,0])
outputText = TextBox(app, command=textChanged, text="", grid=[1,0])
outputText.text_size = 24
brailleTypeCombo = Combo(app, command=changeBrailleType, options=list(brailleTypes), selected=brailleType, grid=[2,0])

dotButtonWidth = 13
dotButtonHeight = 4
otherButtonWidth = 13
otherButtonHeight = 2
buttons = []
buttons.append( PushButton(app, command=flipDot, args=[0], text="1", grid=[0,1], width=dotButtonWidth, height=dotButtonHeight) )
buttons.append( PushButton(app, command=flipDot, args=[1], text="2", grid=[0,2], width=dotButtonWidth, height=dotButtonHeight) )
buttons.append( PushButton(app, command=flipDot, args=[2], text="3", grid=[0,3], width=dotButtonWidth, height=dotButtonHeight) )
buttons.append( PushButton(app, command=flipDot, args=[3], text="4", grid=[1,1], width=dotButtonWidth, height=dotButtonHeight) )
buttons.append( PushButton(app, command=flipDot, args=[4], text="5", grid=[1,2], width=dotButtonWidth, height=dotButtonHeight) )
buttons.append( PushButton(app, command=flipDot, args=[5], text="6", grid=[1,3], width=dotButtonWidth, height=dotButtonHeight) )
buttons.append( PushButton(app, command=flipDot, args=[6], text="7", grid=[0,4], width=dotButtonWidth, height=dotButtonHeight, visible=False) )
buttons.append( PushButton(app, command=flipDot, args=[7], text="8", grid=[1,4], width=dotButtonWidth, height=dotButtonHeight, visible=False) )
for b in buttons:
    b.bg = colOff

buttonTypeIt = PushButton(app, command=typeIt, text="Type it", grid=[2,1], width=otherButtonWidth, height=otherButtonHeight)
buttonBackspace = PushButton(app, command=backspace, text="Backspace", grid=[2,2], width=otherButtonWidth, height=otherButtonHeight)
buttonDispMode = PushButton(app, command=changeDispMode, text="Button display:\n{}".format(dispModes[dispMode]), grid=[2,3], width=otherButtonWidth, height=otherButtonHeight)
buttonToggle68 = PushButton(app, command=toggle68, text="Toggle between\n6 and 8 dots", grid=[2,4], width=otherButtonWidth, height=otherButtonHeight)


updateChar()
app.display()
