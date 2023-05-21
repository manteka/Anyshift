"""Anyshift with memory address write feature. Stil WIP"""
"""THIS CODE IS A MESS. NEED TO BE CLEANED A LOT"""

import os  # Hide pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame  # Joystick input
import keyboard  # Key presses
import configparser  # Read ini files
import time  # Delays
import ctypes  # Kernel level key presses
import pyMeow as pm  # Read and write memmory addresses
from ReadWriteMemory import ReadWriteMemory


# Define console windows size (rows, lines)
#os.system("mode con cols=70 lines=13")

# Bunch of stuff so that the script can send keystrokes to game #
SendInput = ctypes.windll.user32.SendInput

# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)


class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

# Global variables
up_key = 's'
down_key = 'z'
rev_key = 'c'
presskey_timer = 0
releasekey_timer = 0
rev_button = 'False' 
neutral = 'False'
first_time = True 
nascar_mode = 'False'

def main():

    # Create a config objet and read config values
    config = configparser.ConfigParser()
    config.read('Anyshift.ini')
    global nascar_mode
    nascar_mode = config['OPTIONS']['nascar racing mode']
    seven_gears = config['OPTIONS']['seven gears']
    global rev_button
    rev_button = config['OPTIONS']['reverse is button']
    global neutral
    neutral = config['OPTIONS']['neutral detection']
    mem_mode = config['OPTIONS']['memory write mode']
    db_base_addr = config['OPTIONS']['dosbox version base address']
    offset = config['OPTIONS']['memory value offset']
    joy_id = config['SHIFTER']['joystick id']
    first = int(config['SHIFTER']['first gear'])
    second = int(config['SHIFTER']['second gear'])
    third = int(config['SHIFTER']['third gear'])
    fourth = int(config['SHIFTER']['fourth gear'])
    fifth = int(config['SHIFTER']['fifth gear'])
    sixth = int(config['SHIFTER']['sixth gear'])
    seventh = int(config['SHIFTER']['seventh gear'])
    reverse = int(config['SHIFTER']['reverse'])
    neut_key = config['KEYS']['neutral key']
    global up_key
    up_key = config['KEYS']['upshift']
    global down_key
    down_key = config['KEYS']['downshift']
    global rev_key
    rev_key = config['KEYS']['reverse']
    global presskey_timer
    presskey_timer = float(config['OPTIONS']['presskey timer'])
    global releasekey_timer
    releasekey_timer = float(config['OPTIONS']['releasekey timer'])

    # Initialize joystick module
    pygame.joystick.init()
    
    # Create a joystick object and initialize it
    shifter = pygame.joystick.Joystick(int(joy_id))
    shifter.init()    
    
    # Cool window design ;)
    print()
    print("    ___                _____ __    _ ______              ___  ____  ")
    print("   /   |  ____  __  __/ ___// /_  (_) __/ /_   _   __   <  / / __ \ ")
    print("  / /| | / __ \/ / / /\__ \/ __ \/ / /_/ __/  | | / /   / / / / / / ")
    print(" / ___ |/ / / / /_/ /___/ / / / / / __/ /_    | |/ /   / /_/ /_/ /  ")
    print("/_/  |_/_/ /_/\__, //____/_/ /_/_/_/  \__/    |___/   /_/(_)____/   ")
    print("             /____/                           ©2023 Menkaura Soft   ")
    print()
    print("Buy me a coffe if you like this app: https://bmc.link/Menkaura")
    print()
    print("Active shifter: ", shifter.get_name())
    
    gear_selected = 0 
    actual_gear = 0
    # Open DosBox process
    rwm = ReadWriteMemory()
    process = rwm.get_process_by_name('DOSBox.exe')
    process.open()
    # DosBox base address. Get from the pointer we have
    x_pointer = process.get_pointer(int(db_base_addr, 16)) 
    # Gear address is the base address plus the offset. This is the value we found in Cheat Engine
    gear_address = process.read(x_pointer) + int(offset, 16)
    
    if mem_mode == 'False':
        # Joystick read loop  
        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True  # Flag that we are done so we exit this loop.

                if event.type == pygame.JOYBUTTONDOWN:
                    if shifter.get_button(first) == True:
                        gear_selected = 1
                        actual_gear = update_gear(gear_selected, actual_gear)
                    if shifter.get_button(second) == True:
                        gear_selected = 2
                        actual_gear = update_gear(gear_selected, actual_gear) 
                    if shifter.get_button(third) == True:
                        gear_selected = 3
                        actual_gear = update_gear(gear_selected, actual_gear)
                    if shifter.get_button(fourth) == True:
                        gear_selected = 4
                        actual_gear = update_gear(gear_selected, actual_gear)
                    if shifter.get_button(fifth) == True:
                        gear_selected = 5
                        actual_gear = update_gear(gear_selected, actual_gear)
                    if shifter.get_button(sixth) == True:
                        gear_selected = 6
                        actual_gear = update_gear(gear_selected, actual_gear)  
                    if seven_gears == 'True':  # To avoid invalid button error
                        if shifter.get_button(seventh) == True:
                            gear_selected = 7
                            actual_gear = update_gear(gear_selected, actual_gear)
                    if shifter.get_button(reverse) == True:
                        gear_selected = -1
                        actual_gear = update_gear(gear_selected, actual_gear)
                    print(f"Gear in joystick: {gear_selected} -- Actual gear: {actual_gear}   ",  end="\r")

                # Change to neutral if the option is enabled. The program sleeps, and then check if the next event is a joybuttondown, if true skips neutral
                if event.type == pygame.JOYBUTTONUP and neutral == 'True':
                    time.sleep(0.3)
                    if not pygame.event.peek(pygame.JOYBUTTONDOWN):
                        gear_selected = 0
                        actual_gear = update_gear(gear_selected, actual_gear)
                        print(f"Gear in joystick: {gear_selected} -- Actual gear: {actual_gear}   ",  end="\r")

            # Select neutral if this key is pressed
            if keyboard.is_pressed(neut_key):
                gear_selected = 0
                actual_gear = update_gear(gear_selected, actual_gear)
                print(f"Gear in joystick: {gear_selected} -- Actual gear: {actual_gear}   ",  end="\r")    
    else:
        if nascar_mode == 'False':
            # Open process
            process = pm.open_process("DOSBox.exe")
            address = gear_address       
            # Loop
            done = False
            while not done:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        done = True  # Flag that we are done so we exit this loop.

                    if event.type == pygame.JOYBUTTONDOWN:
                        if shifter.get_button(first) == True:
                            pm.w_byte(process, address, 1)
                            gear_selected = 1
                        if shifter.get_button(second) == True:
                            pm.w_byte(process, address, 2)
                            gear_selected = 2
                        if shifter.get_button(third) == True:
                            pm.w_byte(process, address, 3)
                            gear_selected = 3
                        if shifter.get_button(fourth) == True:
                            pm.w_byte(process, address, 4)
                            gear_selected = 4
                        if shifter.get_button(fifth) == True:
                            pm.w_byte(process, address, 5)
                            gear_selected = 5
                        if shifter.get_button(sixth) == True:
                            pm.w_byte(process, address, 6)
                            gear_selected = 6  
                        if seven_gears == 'True':  # To avoid invalid button error
                            if shifter.get_button(seventh) == True:
                                pm.w_byte(process, address, 7)
                                gear_selected = 7
                        if shifter.get_button(reverse) == True:
                            pm.w_byte(process, address, -1)
                            gear_selected = -1                
                        print(f"Gear in joystick: {gear_selected}   ",  end="\r")

                    # Change to neutral if the option is enabled. The program sleeps, and then check if the next event is a joybuttondown, if true skips neutral
                    if event.type == pygame.JOYBUTTONUP and neutral == 'True':
                        time.sleep(0.3)
                        if not pygame.event.peek(pygame.JOYBUTTONDOWN):
                            pm.w_byte(process, address, 0)
                            gear_selected = 0
                            print(f"Gear in joystick: {gear_selected}   ",  end="\r")

                # Select neutral if this key is pressed
                if keyboard.is_pressed(neut_key):
                    gear_selected = 0
                    print(f"Gear in joystick: {gear_selected}   ",  end="\r")
        else:
            # Open process
            process = pm.open_process("DOSBox.exe")
            address = gear_address       
            # Loop
            done = False
            while not done:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        done = True  # Flag that we are done so we exit this loop.

                    if event.type == pygame.JOYBUTTONDOWN:
                        if shifter.get_button(first) == True:
                            pm.w_byte(process, address, 0)
                            gear_selected = 1
                        if shifter.get_button(second) == True:
                            pm.w_byte(process, address, 1)
                            gear_selected = 2
                        if shifter.get_button(third) == True:
                            pm.w_byte(process, address, 2)
                            gear_selected = 3
                        if shifter.get_button(fourth) == True:
                            pm.w_byte(process, address, 3)
                            gear_selected = 4
                        if shifter.get_button(reverse) == True:
                            KeyPress_rev()
                            gear_selected = -1                
                        print(f"Gear in joystick: {gear_selected}   ",  end="\r")            
                
# Function to apply sequential logic to h-shifter inputs, and make the necessary key presses
def update_gear(gear_selected, actual_gear):

    global first_time

    if nascar_mode == 'True':
        if rev_button == 'True' and gear_selected == -1:
            while actual_gear != 1:
                KeyPress_down()
                actual_gear -= 1
            KeyPress_rev() 
            act_gear = 1
        else:  # Reverse is a gear, not a button   
            KeyRelease_rev()  # Release de reverse key just in case we came from reverse is a button mode
            if neutral == 'True':  # Normal operation with gear 0 for neutral
                act_gear = actual_gear
                while act_gear != gear_selected:
                    if act_gear < gear_selected:
                        act_gear += 1
                        KeyPress_up()                
                    if act_gear > gear_selected:
                        act_gear -= 1
                        KeyPress_down()
            else:  # Game doesn´t detect neutral, so we skip gear 0    
                act_gear = actual_gear
                while act_gear != gear_selected:  
                    if act_gear < gear_selected:
                        if act_gear == 0:
                            act_gear += 1
                            if first_time == True:  # To prevent the bug where it doesn´t change the first time you use the shifter
                                KeyPress_up()
                                first_time = False   
                        else:
                            act_gear += 1
                            KeyPress_up()                
                    if act_gear > gear_selected:
                        if act_gear == 0:
                            act_gear -= 1                                           
                        else:
                            act_gear -= 1
                            KeyPress_down()
    else:
        # Press key selected for reverse
        if rev_button == 'True' and gear_selected == -1:
            KeyPress_rev() 
            act_gear = -1
        else:  # Reverse is a gear, not a button   
            KeyRelease_rev()  # Release de reverse key just in case we came from reverse is a button mode
            if neutral == 'True':  # Normal operation with gear 0 for neutral
                act_gear = actual_gear
                while act_gear != gear_selected:
                    if act_gear < gear_selected:
                        act_gear += 1
                        KeyPress_up()                
                    if act_gear > gear_selected:
                        act_gear -= 1
                        KeyPress_down()
            else:  # Game doesn´t detect neutral, so we skip gear 0    
                act_gear = actual_gear
                while act_gear != gear_selected:  
                    if act_gear < gear_selected:
                        if act_gear == 0:
                            act_gear += 1
                            if first_time == True:  # To prevent the bug where it doesn´t change the first time you use the shifter
                                KeyPress_up()
                                first_time = False  
                        else:
                            act_gear += 1
                            KeyPress_up()                
                    if act_gear > gear_selected:
                        if act_gear == 0:
                            act_gear -= 1                                           
                        else:
                            act_gear -= 1
                            KeyPress_down()
                            
    return act_gear


# Ctypes complicated stuff for low level key presses
def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def KeyPress_up():
    time.sleep(presskey_timer)
    PressKey(int(up_key, 16))  # press
    time.sleep(releasekey_timer)
    ReleaseKey(int(up_key, 16))  # release


def KeyPress_down():
    time.sleep(presskey_timer)
    PressKey(int(down_key, 16))  # press
    time.sleep(releasekey_timer)
    ReleaseKey(int(down_key, 16))  # release


def KeyPress_rev():
    time.sleep(presskey_timer)
    PressKey(int(rev_key, 16))  # press


def KeyRelease_rev():
    time.sleep(releasekey_timer)
    ReleaseKey(int(rev_key, 16))  # release
    

if __name__ == "__main__":
    pygame.init()
    main()
    pygame.quit()