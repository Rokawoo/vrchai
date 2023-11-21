"""
File: stringProcessing.py

Description:
    This Python file contains functions for text processing. Specifically, it defines the functions 'split_string' and
    'end_sentence'. The 'split_string' function takes a long text string as input and splits it into segments based on a
    maximum segment length. The 'end_sentence' function ensures that a given input string ends with an appropriate face or
    expression.

Functions:
    - split_string(text: str) -> list: Split a long text string into segments based on a maximum segment length.

    - end_sentence(input_string: str) -> str: Ensure that the given input string ends with an appropriate face or expression.

Author:
    Augustus Sroka

Last Updated:
    11/20/2023
"""


def split_string(text):
    """
    Split a long text string into segments based on a maximum segment length.

    Parameters:
    - text (str): The input text to be split.

    Returns:
    - list: A list of segments.
    """
    words = text.split()
    segments = []
    current_segment = []
    max_segment_length = 144

    for word in words:
        if len(' '.join(current_segment + [word])) <= max_segment_length:
            current_segment.append(word)
        else:
            segments.append(' '.join(current_segment))
            current_segment = [word]

    if current_segment:
        segments.append(' '.join(current_segment))

    return segments


def end_sentence(input_string):
    """
    Ensure that the given input string ends with an appropriate face or expression.

    Parameters:
    - input_string (str): The input string to be modified.

    Returns:
    - str: The modified input string.
    """
    punctuation_set = {'<', '>', '^', '~', '.', '?', '!'}

    faces_to_keep = {'Awoof~!', '>w<', '^w^', '^^', '>.<', '>//w//<', '>.>'}

    last_punctuation_index = max(input_string.rfind(p) for p in punctuation_set)

    if last_punctuation_index >= 0:
        # Delete everything after the last punctuation
        input_string = input_string[:last_punctuation_index + 1]

        if any(input_string.endswith(face) for face in faces_to_keep):
            return input_string

    # If none of the faces are found or there's no punctuation, just append the word to the resulting string
    return input_string + " Awoof~! ^^"
