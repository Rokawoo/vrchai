import threading
import time
from collections import deque

from pythonosc import dispatcher, osc_server
from pythonosc.udp_client import SimpleUDPClient

from controlVariables import HOST, PORT

CLIENT = SimpleUDPClient(HOST, PORT)

TARGET_ADDRESS = "/avatar/parameters/Pat"
COUNT_FILE_PATH = "count.txt"

MAX_QUEUE_SIZE = 1

is_pat_enabled = None


def handle_message(address, *args):
    global TARGET_ADDRESS, is_pat_enabled
    if address == TARGET_ADDRESS:
        if args and args[0] == 0:  # Check if the pat is disabled 0 | 1
            if is_pat_enabled:
                increment_count()
                is_pat_enabled = False
        else:
            is_pat_enabled = True


def increment_count():
    global count
    count += 1
    save_count()
    formatted_count = "{:,}".format(count)  # Format count with commas
    print(f"Count incremented: {formatted_count}")
    with queue_lock:
        message_queue.append([f"Headpat Number: {formatted_count} >w< Awoo~!", True])
    new_message_event.set()  # Signal that a new message is available


def save_count():
    global COUNT_FILE_PATH
    with open(COUNT_FILE_PATH, "w") as file:
        file.write(str(count))


def load_count():
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
server = osc_server.ThreadingOSCUDPServer(("localhost", 9001), dispatcher)

server_thread = None

message_thread = None

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


# Function to process and send messages from the queue
def process_messages():
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


def cleanup():
    global server
    server.shutdown()
    server_thread.join()
    message_thread.join()


# Start the headpat listener in a separate thread
def start_headpat_listener():
    global server_thread, message_thread
    # Start the UDP server and the message processing thread in separate threads
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()

    message_thread = threading.Thread(target=process_messages)
    message_thread.start()

    # Start the headpat listener in a separate thread
    headpat_thread = threading.Thread(target=headpat_listener)
    headpat_thread.start()


if __name__ == "__main__":
    try:
        start_headpat_listener()
    finally:
        cleanup()
