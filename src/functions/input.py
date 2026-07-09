import mouse
import pyperclip

def mouse_x():
    return mouse.get_position()[0]

def mouse_y():
    return mouse.get_position()[1]

def get_clipboard():
    return pyperclip.paste()