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

from pythonosc.udp_client import SimpleUDPClient

from controlVariables import HOST, PORT

CLIENT = SimpleUDPClient(HOST, PORT)

import asyncio
import random

import cv2
import mss
import pydirectinput
import win32api
import win32con
from pythonosc.udp_client import SimpleUDPClient
from controlVariables import HOST, PORT

CLIENT = SimpleUDPClient(HOST, PORT)


async def move_cursor_smoothly(destination_x, destination_y, duration=2, steps_multiplier=10, sensitivity=1.0):
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

        await asyncio.sleep(duration / steps)


async def click():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    await asyncio.sleep(0.01)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)


async def respawn():
    pydirectinput.press('esc')
    pydirectinput.moveTo(900, 815)
    await click()


async def the_great_pug_position_normalization():
    sct = mss.mss()
    while True:
        await respawn()
        await asyncio.sleep(0.1)
        await move_cursor_smoothly(960, 9999, 1, 1)
        await move_cursor_smoothly(960, -380, 1, 1)
        sct.shot(output='normalization_temp.png')
        frame = cv2.imread('normalization_temp.png')

        pixel_color = frame[438, 384]
        r, g, b = pixel_color[2], pixel_color[1], pixel_color[0]
        if (61 < r < 73) and (43 < g < 55) and (21 < b < 33):
            break


async def the_great_pug_position_1():
    CLIENT.send_message("/input/TurnLeft", 1)
    await asyncio.sleep(1.5)
    CLIENT.send_message("/input/TurnLeft", 0)


async def start_world_movement_random(world, current_position_number=0):
    possible_positions = {1, 2, 3}
    if current_position_number != 0:
        possible_positions.remove(current_position_number)
    next_position_number = random.choice(list(possible_positions))

    world_position_normalization = globals()[f"{world}_position_normalization"]
    world_position = globals()[f"{world}_position_{next_position_number}"]
    await world_position_normalization()
    await world_position()

    return next_position_number


async def start_world_movement(world, next_position_number):
    world_position_normalization = globals()[f"{world}_position_normalization"]
    world_position = globals()[f"{world}_position_{next_position_number}"]
    await world_position_normalization()
    await world_position()

    return next_position_number


async def main():
    while True:
        await the_great_pug_position_normalization()
        break


if __name__ == "__main__":
    asyncio.run(main())
