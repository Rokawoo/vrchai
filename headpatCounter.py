"""
File: headpatCounter.py

Description:
    This Python script implements a headpat listener using OSC (Open Sound Control). It listens for headpat events,
    increments a headpat count, and sends messages to a chatbox. The script utilizes the 'pythonosc' library for OSC
    communication and 'threading' for multithreading.

Dependencies:
    - threading
    - time
    - collections.deque
    - pythonosc.dispatcher.Dispatcher
    - pythonosc.osc_server.ThreadingOSCUDPServer
    - pythonosc.udp_client.SimpleUDPClient
    - controlVariables.HOST
    - controlVariables.PORT
    - controlVariables.LISTENING_PORT

Global Variables:
    - CLIENT: The SimpleUDPClient for sending OSC messages.
    - TARGET_ADDRESS: The OSC address for headpat events.
    - COUNT_FILE_PATH: The file path for storing the headpat count.
    - MAX_QUEUE_SIZE: The maximum size of the message queue.
    - is_pat_enabled: Flag to track headpat status.
    - dispatcher: An instance of the dispatcher for handling OSC messages.
    - server: The OSC server for receiving messages.
    - server_thread: The thread for running the OSC server.
    - message_thread: The thread for processing and sending messages to the chatbox.
    - headpat_thread: The thread for listening for headpats.
    - queue_lock: The lock for protecting the message queue access.
    - new_message_event: The event to signal when a new message is added to the queue.
    - message_queue: The deque with a maximum size for the message queue.
    - count: The headpat count variable.
    - pat_enabled: The condition variable for synchronization.

Functions:
    - handle_message(address: str, *args) -> None: Handle messages received from the OSC server.
    - increment_count() -> None: Increment the headpat count, save it, and add a new message to the queue.
    - save_count() -> None: Save the current headpat count to a file.
    - load_count() -> int: Load the headpat count from a file.
    - process_messages() -> None: Process and send messages from the queue to the chatbox.
    - headpat_listener() -> None: Listen for headpats and toggle the is_pat_enabled flag accordingly.
    - cleanup() -> None: Shut down the OSC server and join the server and message threads.
    - start_headpat_listener() -> None: Start the headpat listener and related threads.

Author:
    Augustus Sroka

Last Updated:
    11/20/2023
"""

import threading
import time
from collections import deque

from pythonosc import dispatcher, osc_server
from pythonosc.udp_client import SimpleUDPClient

from controlVariables import HOST, PORT, LISTENING_PORT

CLIENT = SimpleUDPClient(HOST, PORT)

TARGET_ADDRESS = "/avatar/parameters/Pat"
COUNT_FILE_PATH = "count.txt"

MAX_QUEUE_SIZE = 1

is_pat_enabled = None


def handle_message(address, *args):
    """
    Handle messages received from the OSC server.

    Parameters:
    - address (str): The OSC address of the received message.
    - *args: Variable number of arguments received in the message.

    Returns:
    - None
    """
    global TARGET_ADDRESS, is_pat_enabled
    if address == TARGET_ADDRESS:
        if args and args[0] == 0:  # Check if the pat is disabled 0 | 1
            if is_pat_enabled:
                increment_count()
                is_pat_enabled = False
        else:
            is_pat_enabled = True


def increment_count():
    """
    Increment the pat count, save it, and add a new message to the queue.

    Returns:
    - None
    """
    global count
    count += 1
    save_count()
    formatted_count = "{:,}".format(count)  # Format count with commas
    print(f"Count incremented: {formatted_count}")
    with queue_lock:
        message_queue.append([f"Headpat Number: {formatted_count} >w< Awoo~!", True])
    new_message_event.set()  # Signal that a new message is available


def save_count():
    """
    Save the current count to a file.

    Returns:
    - None
    """
    global COUNT_FILE_PATH
    with open(COUNT_FILE_PATH, "w") as file:
        file.write(str(count))


def load_count():
    """
    Load the count from a file.

    Returns:
    - int: The loaded count or 0 if the file is not found.
    """
    global COUNT_FILE_PATH
    try:
        with open(COUNT_FILE_PATH, "r") as file:
            return int(file.read() or "0")
    except FileNotFoundError:
        return 0


# Create an instance of the dispatcher and register the message handler
dispatcher = dispatcher.Dispatcher()
dispatcher.set_default_handler(handle_message)

# Create a UDP server to receive messages
server = osc_server.ThreadingOSCUDPServer((HOST, LISTENING_PORT), dispatcher)

# Thread Buckets
server_thread = None
message_thread = None
headpat_thread = None

# Create a lock for protecting the message queue access
queue_lock = threading.Lock()

# Create an Event to signal when a new message is added to the queue
new_message_event = threading.Event()

# Create a deque with a maximum size for the message queue
message_queue = deque(maxlen=MAX_QUEUE_SIZE)

# Count variable
count = load_count()

# Create a condition variable for synchronization
pat_enabled = threading.Condition()


def process_messages():
    """
    Process and send messages from the queue to the chatbox.

    Returns:
    - None
    """
    global CLIENT, server, queue_lock, new_message_event, message_queue, count

    while True:
        # Wait for a new message to become available in the queue
        new_message_event.wait(1)

        # Lock the queue before accessing it
        with queue_lock:
            while message_queue:
                message = message_queue.popleft()  # Use popleft() to get the first element
                CLIENT.send_message("/chatbox/input", message)

                # Wait 2.5 seconds per request
                time.sleep(2.5)

        # Clear the event flag to avoid processing the same message again
        new_message_event.clear()


def headpat_listener():
    """
    Listen for headpats and toggle the is_pat_enabled flag accordingly.

    Returns:
    - None
    """
    global pat_enabled, is_pat_enabled
    print("Listening For Headpats...")
    is_pat_enabled = True  # Flag to track pat status
    try:
        while True:
            # Wait until pat is disabled
            with pat_enabled:
                pat_enabled.wait_for(lambda: not is_pat_enabled)

            # Wait until pat is re-enabled
            with pat_enabled:
                pat_enabled.wait_for(lambda: is_pat_enabled)

            # Additional delay to avoid immediate re-triggering
            pat_enabled.wait(1)

    except KeyboardInterrupt:
        pass


def hCcleanup():
    """
    Shut down the OSC server and join the server and message threads.

    Returns:
    - None
    """
    global server, server_thread, message_thread, headpat_thread
    try:
        server.shutdown()
    except Exception as e:
        print(f"Error during server shutdown: {e}")

    try:
        server_thread.join(timeout=5)
        message_thread.join(timeout=1.5)
        headpat_thread.join(timeout=1.5)
    except Exception as e:
        print(f"Error during thread join: {e}")


def start_headpat_listener():
    """
    Start the headpat listener and related threads.

    Returns:
    - None
    """
    global server_thread, message_thread, headpat_thread
    # Start the UDP server and the message processing thread in separate threads
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    message_thread = threading.Thread(target=process_messages, daemon=True)
    message_thread.start()

    headpat_thread = threading.Thread(target=headpat_listener, daemon=True)
    headpat_thread.start()


if __name__ == "__main__":
    try:
        start_headpat_listener()
    finally:
        hCcleanup()
