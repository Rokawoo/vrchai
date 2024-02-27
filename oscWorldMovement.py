"""
File: VrChatMovement.py

Purpose:
    VrChat Movement Control Script for Cursor and Avatar.

Description:
    This Python script implements control for cursor movement and avatar actions in VrChat. It utilizes various libraries
    for screen capturing, input simulation, and asynchronous operations to enable smooth cursor movement and avatar actions.
    The script contains functions for moving the cursor smoothly, clicking, respawning the avatar, and positioning the
    avatar in specific locations within the virtual world.

Dependencies:
    - pythonosc
    - cv2
    - mss
    - pydirectinput
    - win32api
    - win32con
    - controlVariables

Usage:
    Run the script to control cursor movement and avatar actions in VrChat. Ensure all dependencies are installed and
    the controlVariables are appropriately configured.

Note:
    This script is designed for use in VrChat environments.

Author:
    Augustus Sroka

Last Updated:
    2/26/2024
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
import oscMovement
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
    """
    Simulate a mouse click by pressing and releasing the left mouse button.
    """
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    await asyncio.sleep(0.01)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)


async def respawn():
    """
    Performs a respawn action in the game environment.
    """
    pydirectinput.press('esc')
    pydirectinput.moveTo(900, 815)
    await click()

async def capture_frame_and_pixel_color(y, x):
    mss.mss().shot(output='normalization_temp.png')
    frame = cv2.imread('normalization_temp.png')
    pixel_color = frame[y, x]
    return pixel_color


async def the_great_pug_position_normalization():
    """
    Normalize the spawn position in "The Great Pug" game environment.
    """
    await respawn()
    await asyncio.sleep(0.1)
    await move_cursor_smoothly(960, -9999, 1, 1)

    while True:
        pixel_color = await capture_frame_and_pixel_color(975, 665)
        r, g, b = pixel_color[2], pixel_color[1], pixel_color[0]
        if (197 < r < 209) and (187 < g < 199) and (154 < b < 166):
            while True:
                pixel_color = await capture_frame_and_pixel_color(1079, 1)
                r, g, b = pixel_color[2], pixel_color[1], pixel_color[0]
                print(r, g, b)
                if (36 < r < 54) and (26 < g < 42) and (14 < b < 29):
                    await move_cursor_smoothly(960, 1600, 1, 1)
                    await oscMovement.forward_move(1)
                    await oscMovement.left_turn_free(0.3377)
                    await oscMovement.forward_move(1)
                    await oscMovement.left_turn_free(0.015)
                    await oscMovement.right_move(0.06)
                    return None
                await oscMovement.right_turn_free(0.0001)
        await respawn()
        await asyncio.sleep(0.15)


async def the_great_pug_position_1():
    """
    Perform a movement actions in "The Great Pug" game environment to position 1.
    """
    await oscMovement.forward_move(7.8)
    await oscMovement.half_turn(1)
    await oscMovement.right_move(0.18)
    await oscMovement.left_turn_free(0.04)


async def start_world_movement_random(world, current_position_number=0, override_position_number=None):
    """
    Start movement in the game world randomly.

    Parameters:
    - world (str): The name of the game world.
    - current_position_number (int): The current position number. (Default 0 - All positions Viable)
    - specific_position_number (int): Override for random position.

    Returns:
    int: The next position number after the movement.
    """
    if override_position_number is not None:
        next_position_number = override_position_number
    else:
        possible_positions = {1, 2, 3} - {current_position_number}
        next_position_number = random.choice(list(possible_positions))

    world_position_normalization = globals()[f"{world}_position_normalization"]
    world_position = globals()[f"{world}_position_{next_position_number}"]
    await world_position_normalization()
    await world_position()

    return next_position_number


async def main():
    await start_world_movement_random("the_great_pug", 0, 1)



if __name__ == "__main__":
    asyncio.run(main())
