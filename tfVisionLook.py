import asyncio
import os

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

# Load label map and category index
label_map_path = files['LABELMAP']  # Replace with the actual path to your label map
category_index = label_map_util.create_category_index_from_labelmap(label_map_path, use_display_name=True)

# Load pipeline config and build a detection model
configs = config_util.get_configs_from_pipeline_file(files['PIPELINE_CONFIG'])
detection_model = model_builder.build(model_config=configs['model'], is_training=False)

# Restore checkpoint
ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
ckpt.restore(os.path.join(paths['CHECKPOINT_PATH'], 'ckpt-50')).expect_partial()


async def cleanup():
    # Additional cleanup steps can be added here
    mss.mss.close()
    cv2.destroyAllWindows()


async def read_image_async(file_path):
    async with aiofiles.open(file_path, 'rb') as file:
        return await file.read()


async def move_cursor_smoothly(destination_x, destination_y, duration=2, steps_multiplier=10, sensitivity=1.0):
    # Get the current cursor position
    current_x, current_y = pydirectinput.position()

    # Calculate the number of steps based on the duration
    steps = int(duration * steps_multiplier)

    # Calculate the step size for each axis with sensitivity adjustment
    step_size_x = (destination_x - current_x) / steps * sensitivity
    step_size_y = (destination_y - current_y) / steps * sensitivity

    # Press the Escape key before starting the movement
    pydirectinput.press('esc')

    # Move the cursor in steps
    for step in range(steps + 1):
        # Press the Escape key after the first step
        if step == 1:
            pydirectinput.press('esc')

        new_x = int(current_x + step_size_x * step)
        new_y = int(current_y + step_size_y * step)

        pydirectinput.moveTo(new_x, new_y)

        # Introduce a small delay between steps
        await asyncio.sleep(duration / steps)


async def detect_and_process(frame):
    input_tensor = tf.convert_to_tensor(np.expand_dims(frame, 0), dtype=tf.float32)
    detections = detect_fn(input_tensor)

    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy()
                  for key, value in detections.items()}
    detections['num_detections'] = num_detections

    label_id_offset = 1
    image_np_with_detections = frame.copy()

    # Sort detections based on scores in descending order
    sorted_indices = np.argsort(detections['detection_scores'])[::-1]

    for i in range(num_detections):
        index = sorted_indices[i]
        score = detections['detection_scores'][index]

        if score >= 0.8:
            box = detections['detection_boxes'][index]
            class_id = int(detections['detection_classes'][index]) + label_id_offset

            # Extracting coordinates
            ymin, xmin, ymax, xmax = box
            im_height, im_width, _ = frame.shape

            # Convert box coordinates to integers
            (left, right, top, bottom) = (
                int(xmin * im_width), int(xmax * im_width), int(ymin * im_height), int(ymax * im_height))

            # Calculate and print the center coordinates
            center_x = (left + right) / 2
            center_y = (top + bottom) / 2

            # Print coordinates
            print(f"Box {i + 1} with Highest Score - Class: {category_index[class_id]['name']}, Score: {score:.2f}")
            print(f"    Coordinates (x, y): {center_x:.2f}, {center_y:.2f}")

            # Check if the amount needed to move is minimal
            current_x, current_y = pydirectinput.position()
            distance = np.sqrt((center_x - current_x) ** 2 + (center_y - current_y) ** 2)
            print(distance)
            if distance > 50:  # Adjust the threshold as needed
                await move_cursor_smoothly(center_x, center_y, 1, 10, 0.45)
    '''
    detection_classes_int = detections['detection_classes'].astype(int)

    viz_utils.visualize_boxes_and_labels_on_image_array(
        image_np_with_detections,
        detections['detection_boxes'],
        detection_classes_int + label_id_offset,
        detections['detection_scores'],
        category_index,
        use_normalized_coordinates=True,
        max_boxes_to_draw=3,
        min_score_thresh=.8,
        agnostic_mode=False
    )
    
    cv2.imshow('object detection', cv2.resize(image_np_with_detections, (1280, 720)))
    '''


@tf.function
def detect_fn(image):
    image, shapes = detection_model.preprocess(image)
    prediction_dict = detection_model.predict(image, shapes)
    detections = detection_model.postprocess(prediction_dict, shapes)
    return detections


async def capture_and_process():
    sct = mss.mss()
    while True:
        sct.shot(output='temp.png')  # Save the screenshot to a temporary file
        image_data = await read_image_async('temp.png')  # Read the screenshot from the file
        frame = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        await detect_and_process(frame)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            sct.close()
            cv2.destroyAllWindows()
            break


async def main():
    try:
        await asyncio.gather(
            asyncio.create_task(move_cursor_smoothly(0, 0)),  # Initial call to move_cursor_smoothly
            capture_and_process()
        )
    finally:
        await cleanup()


if __name__ == "__main__":
    asyncio.run(main())
