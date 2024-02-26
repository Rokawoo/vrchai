"""
File: ocsWorldMovement.py

Description:
    This Python script provides functionality for executing movement commands relative to a specific virtual
    environment. It uses the 'pythonosc' library for sending OSC messages, 'asyncio' for asynchronous
    operations.

Dependencies:
    - asyncio
    - pydirectinput
    - pythonosc.udp_client.SimpleUDPClient
    - controlVariables.HOST
    - controlVariables.PORT
    - controlVariables.MOVE_MESSAGE

Global Variables:
    - CLIENT: The SimpleUDPClient for sending OSC messages.
    - commands: A dictionary mapping regular expressions to corresponding movement commands.
    - number_words: A dictionary mapping words to their numerical values.
    - compiled_commands: A dictionary mapping compiled regular expressions to corresponding movement functions.
    - compiled_number_words: A dictionary mapping compiled regular expressions to numerical values.

Author:
    Augustus Sroka

Last Updated:
    11/20/2023
"""

import random
import time

import cv2
import mss
import pydirectinput
import win32api
import win32con
from pythonosc.udp_client import SimpleUDPClient

from controlVariables import HOST, PORT, AWAITING_MOVEMENT

CLIENT = SimpleUDPClient(HOST, PORT)


def move_cursor_smoothly(destination_x, destination_y, duration=2, steps_multiplier=10, sensitivity=1.0):
    """
    Move the cursor smoothly to a specified destination on the screen.

    Parameters:
    - destination_x (int): The x-coordinate of the destination.
    - destination_y (int): The y-coordinate of the destination.
    - duration (float): The total time duration for the cursor movement.
    - steps_multiplier (int): The number of steps to divide the movement into.
    - sensitivity (float): A sensitivity factor to adjust the step size.

    Note:
    The cursor movement is achieved by simulating steps using PyDirectInput.
    """
    current_x, current_y = pydirectinput.position()

    steps = int(duration * steps_multiplier)

    step_size_x = (destination_x - current_x) / steps * sensitivity
    step_size_y = (destination_y - current_y) / steps * sensitivity

    pydirectinput.press('esc')

    for step in range(steps + 1):
        if step == 1:
            pydirectinput.press('esc')

        new_x = int(current_x + step_size_x * step)
        new_y = int(current_y + step_size_y * step)

        pydirectinput.moveTo(new_x, new_y)

        time.sleep(duration / steps)


def click():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(0.01)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)


def respawn():
    """
    Respawn function to reset the virtual environment.
    """
    pydirectinput.press('esc')
    pydirectinput.moveTo(900, 815)
    click()


def the_great_pug_position_normalization():
    """
    """
    sct = mss.mss()
    while True:
        respawn()
        time.sleep(0.1)
        move_cursor_smoothly(960, 9999, 1, 1)
        move_cursor_smoothly(960, -380, 1, 1)
        sct.shot(output='normalization_temp.png')
        frame = cv2.imread('normalization_temp.png')

        pixel_color = frame[438, 384]
        r, g, b = pixel_color[2], pixel_color[1], pixel_color[0]
        if (61 < r < 73) and (43 < g < 55) and (21 < b < 33):
            print("Position Normalized")
            break


def the_great_pug_position_1():
    CLIENT.send_message("/input/TurnLeft", 1)
    time.sleep(1.5)
    CLIENT.send_message("/input/TurnLeft", 0)


def set_time_to_move():
    global AWAITING_MOVEMENT
    wait_time = random.randint(240, 300)
    time.sleep(wait_time)
    AWAITING_MOVEMENT = True


def start_world_movement(world):
    global AWAITING_MOVEMENT
    AWAITING_MOVEMENT = False
    pass


while True:
    the_great_pug_position_normalization()
    break
