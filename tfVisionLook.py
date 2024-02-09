"""
File: tfVisionLook.py

Description:
    This Python file contains asynchronous functions for image processing. It includes functionality for splitting text
    and ensuring proper punctuation in a given string. Additionally, it contains functions related to object detection
    using TensorFlow and cursor movement with PyDirectInput.

Dependencies:
    - asyncio
    - tensorflow
    - pytesseract
    - cv2
    - pyautogui
    - pydirectinput

Global Variables:
    - None

Functions:
    - split_text(input_text): Split the input text into individual words.
    - ensure_punctuation(input_text): Ensure proper punctuation in the given string.
    - object_detection(image_path): Perform object detection using TensorFlow on the specified image.
    - move_cursor(x, y): Move the cursor to the specified coordinates using PyDirectInput.

Author:
    Augustus Sroka

Last Updated:
    11/25/2023
"""

import asyncio
import os
import threading

import aiofiles
import cv2
import mss
import numpy as np
import pydirectinput
import tensorflow as tf
from object_detection.builders import model_builder
from object_detection.utils import config_util, label_map_util

CUSTOM_MODEL_NAME = 'my_ssd_resnet50_v1_fpn_640x640_coco17_tpu-8_tuned'
LABEL_MAP_NAME = 'label_map.pbtxt'

paths = {
    'ANNOTATION_PATH': os.path.join('..', 'Tensorflow', 'workspace', 'annotations'),
    'CHECKPOINT_PATH': os.path.join('..', 'Tensorflow', 'workspace', 'models', CUSTOM_MODEL_NAME),
}

files = {
    'PIPELINE_CONFIG': os.path.join('..', 'Tensorflow', 'workspace', 'models', CUSTOM_MODEL_NAME, 'pipeline.config'),
    'LABELMAP': os.path.join(paths['ANNOTATION_PATH'], LABEL_MAP_NAME)
}

label_map_path = files['LABELMAP']  # Replace with the actual path to your label map
category_index = label_map_util.create_category_index_from_labelmap(label_map_path, use_display_name=True)

configs = config_util.get_configs_from_pipeline_file(files['PIPELINE_CONFIG'])
detection_model = model_builder.build(model_config=configs['model'], is_training=False)

ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
ckpt.restore(os.path.join(paths['CHECKPOINT_PATH'], 'ckpt-50')).expect_partial()

detected_objects_list = []


async def get_detected_objects():
    """
    Returns the list of detected objects based on the latest frame analysis.

    Returns:
    - List[Union[None, List[Union[str, float, Tuple[float, float]]]]]: The list of detected objects.
    """
    global detected_objects_list

    return [item['class'] if item['class'] != 'DefaultFace' else 'Person' for item in
            detected_objects_list] if detected_objects_list else ''


async def read_image_async(file_path):
    """
   Asynchronously read the contents of an image file.

   Parameters:
   - file_path (str): The path to the image file.

   Returns:
   - bytes: The content of the image file.
   """
    async with aiofiles.open(file_path, 'rb') as file:
        return await file.read()


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


async def detect_and_process(frame):
    """
    Detect objects in a given frame using a TensorFlow detection model and process the results.

    Parameters:
    - frame (numpy.ndarray): The image frame in NumPy array format.

    The function prints information about the highest-scoring detected object and moves the cursor if needed.
    """
    global detected_objects_list
    input_tensor = tf.convert_to_tensor(np.expand_dims(frame, 0), dtype=tf.float32)
    detections = detect_fn(input_tensor)

    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy()
                  for key, value in detections.items()}
    detections['num_detections'] = num_detections

    label_id_offset = 1

    sorted_indices = np.argsort(detections['detection_scores'])[::-1]

    detected_objects_list = [
        {
            'class': category_index[int(detections['detection_classes'][i]) + label_id_offset]['name'],
            'coordinates': detections['detection_boxes'][i]
        }
        for i in sorted_indices if detections['detection_scores'][i] >= 0.8
    ]

    if detected_objects_list:
        highest_score_object = detected_objects_list[0]

        ymin, xmin, ymax, xmax = highest_score_object['coordinates']
        im_height, im_width, _ = frame.shape

        (left, right, top, bottom) = (
            int(xmin * im_width), int(xmax * im_width), int(ymin * im_height), int(ymax * im_height))

        center_x = (left + right) / 2
        center_y = (top + bottom) / 2

        current_x, current_y = pydirectinput.position()
        distance = np.sqrt((center_x - current_x) ** 2 + (center_y - current_y) ** 2)
        if distance > 50:  # Adjust the threshold as needed
            await move_cursor_smoothly(center_x, center_y, 1, 10, 0.45)


@tf.function
def detect_fn(image):
    """
    Run object detection on the given image using a TensorFlow detection model.

    Parameters:
    - image (tf.Tensor): The input image tensor.

    Returns:
    - dict: A dictionary containing the detection results, including detection boxes,
            classes, scores, and the number of detections.
    """
    image, shapes = detection_model.preprocess(image)
    prediction_dict = detection_model.predict(image, shapes)
    detections = detection_model.postprocess(prediction_dict, shapes)
    return detections


async def capture_and_process():
    """
    Continuously capture screenshots, process them for object detection, and move the cursor accordingly.

    The function runs in an infinite loop until the 'q' key is pressed.
    """
    sct = mss.mss()
    while True:
        sct.shot(output='temp.png')  # Save the screenshot to a temporary file
        image_data = await read_image_async('temp.png')  # Read the screenshot from the file
        frame = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        await detect_and_process(frame)


async def main():
    try:
        await asyncio.gather(capture_and_process())
    finally:
        vision_cleanup()


vision_looker_thread = None


def vision_cleanup():
    """
    Perform cleanup tasks, such as closing the mss (Python Screen Capture) instance and destroying OpenCV windows.

    Additional cleanup steps can be added here.
    """
    global vision_looker_thread
    try:
        mss.mss().close()
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"Error during shutdown: {e}")

    try:
        vision_looker_thread.join(timeout=5)
    except Exception as e:
        print(f"Error during thread join: {e}")


def start_vision_looker():
    global vision_looker_thread
    vision_looker_thread = threading.Thread(target=lambda: asyncio.run(main()), daemon=True)
    vision_looker_thread.start()


if __name__ == "__main__":
    asyncio.run(main()) 
