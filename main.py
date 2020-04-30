#\========================================/#
#||  Braille Typer                       ||#
#||      By Oliver Simmons (GoodClover)  ||#
#||     License: MIT                     ||#
#/========================================\#

##### Imports #####
from guizero import App, PushButton, Text, TextBox, Combo
import json
import keyboard

# I 'borrowed' this code so it's going here
def get_bit(value, n):
    return ((value >> n & 1) != 0)

def set_bit(value, n):
    return value | (1 << n)

def clear_bit(value, n):
    return value & ~(1 << n)


##### Variable declarations #####
colOff = (255, 255, 255)
colOn  = (100, 100, 100)

# Braille starts at 0x2800 for a space and you add 8 bits representing the dots.
#  1  4
#  2  5
#  3  6
#  7  8
offset = 0x2800
current = 0x00
char = "⠀" # This is a braille space.
text = ""

dispModes = [
    "numbers",
    "numbers starting at 0",
    "braille",
    "none",
    "position",
    "position short",
    "on or off",
    "dot or none"
]
dispMode = 0

positionText = {
    0:    "Top Left", 3: "Top Right",
    1: "Middle Left", 4: "Middle Right",
    2: "Bottom Left", 5: "Bottom Right"
}
positionShortText = {
    0: "TL", 3: "TR",
    1: "ML", 4: "MR",
    2: "BL", 5: "BR"
}
positionText8 = {
    0:           "Top Left", 3: "Top Right",
    1:    "Top Middle Left", 4: "Top Middle Right",
    2: "Bottom Middle Left", 5: "Bottom Middle Right",
    6:        "Bottom Left", 7: "Bottom Right"
}
positionShortText8 = {
    0:  "TL", 3: "TR",
    1: "TML", 4: "TMR",
    2: "BML", 5: "BMR",
    6:  "BL", 7: "BR"
}

with open("brailleTypes.json", "r", encoding="utf8") as file:
    brailleTypes = json.loads(file.read())
brailleType = "English Braille"

##### Start of functions #####
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
    updateDispMode()

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
        for i in range(8):
            setDot(i, False)
    text += c
    outputText.value = text

def typeExt():
    keyboard.wait("space", suppress=True)
    keyboard.write(text)

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
            elif c.lower() in brailleTypes[brailleType]["characters"]:
                text += brailleTypes[brailleType]["characters"][c.lower()]
            elif c in ["\n"]:
                text += c
        outputText.value = contractText(text)

def contractText(text):
    return text
    # I have no idea how to do this.
    # buildup = ""
    # newtext = ""
    # for char in text:
    #     buildup += char
    #     if:
    #         newtext += buildup
    # return newtext

def changeDispMode(n=None):
    global dispMode
    if n == None:
        dispMode = (dispMode + 1) % len(dispModes)
    else:
        dispMode = n
    updateDispMode()

def changeBrailleType(to):
    global brailleType
    brailleType = to


##### Display Modes #####
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



##### Application Window #####
app = App(title="Braille Writer", layout="grid")


currentText = Text(app,
    text=char,
    size=64,
    grid=[0,0]
)
outputText = TextBox(app,
    command=textChanged,
    text="",
    grid=[1,0]
)
outputText.text_size = 24
brailleTypeCombo = Combo(app,
    command=changeBrailleType,
    options=list(brailleTypes),
    selected=brailleType,
    grid=[2,0]
)

dotButtonWidth = 13
dotButtonHeight = 4
otherButtonWidth = 13
otherButtonHeight = 2
buttons = {
    0: PushButton(app,
        command=flipDot, args=[0],
        text="1",
        grid=[0,1],
        width=dotButtonWidth, height=dotButtonHeight
    ),
    1: PushButton(app,
        command=flipDot, args=[1],
        text="2",
        grid=[0,2],
        width=dotButtonWidth, height=dotButtonHeight
    ),
    2: PushButton(app,
        command=flipDot, args=[2],
        text="3",
        grid=[0,3],
        width=dotButtonWidth, height=dotButtonHeight
    ),
    3: PushButton(app,
        command=flipDot, args=[3],
        text="4",
        grid=[1,1],
        width=dotButtonWidth, height=dotButtonHeight
    ),
    4: PushButton(app,
        command=flipDot, args=[4],
        text="5",
        grid=[1,2],
        width=dotButtonWidth, height=dotButtonHeight
    ),
    5: PushButton(app,
        command=flipDot, args=[5],
        text="6",
        grid=[1,3],
        width=dotButtonWidth, height=dotButtonHeight
    ),
    6: PushButton(app,
        command=flipDot, args=[6],
        text="7",
        grid=[0,4],
        width=dotButtonWidth, height=dotButtonHeight,
        visible=False
    ),
    7: PushButton(app,
        command=flipDot, args=[7],
        text="8",
        grid=[1,4],
        width=dotButtonWidth, height=dotButtonHeight,
        visible=False
    )
}
for i in buttons:
    buttons[i].bg = colOff

buttonTypeIt = PushButton(app,
    command=typeIt,
    text="Type it",
    grid=[2,1],
    width=otherButtonWidth, height=otherButtonHeight
)
buttonTypeExt = PushButton(app,
    command=typeExt,
    text="Type Externally\n(Hit space in\n destination window)",
    grid=[3,1],
    width=otherButtonWidth, height=otherButtonHeight
)
buttonBackspace = PushButton(app,
    command=backspace,
    text="Backspace",
    grid=[2,2],
    width=otherButtonWidth, height=otherButtonHeight
)
buttonDispMode = PushButton(app,
    command=changeDispMode,
    text="Button display:\n{}".format(dispModes[dispMode]),
    grid=[2,3],
    width=otherButtonWidth, height=otherButtonHeight
)
buttonToggle68 = PushButton(app,
    command=toggle68,
    text="Toggle between\n6 and 8 dots",
    grid=[2,4],
    width=otherButtonWidth, height=otherButtonHeight
)
##### The Final Little Bit #####
updateChar()
app.display()
