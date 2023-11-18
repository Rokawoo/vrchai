def split_string(text):
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
    punctuation_set = ('<', '^', '~', '.', '?', '!')

    faces_to_keep = ('Awoof~!', '>w<', '^w^', '^^', '>.<', '>//w//<', '>w<', '^w^', '^^', '>.<', '^^')

    last_punctuation_index = max(input_string.rfind(p) for p in punctuation_set)

    if last_punctuation_index >= 0:
        # Delete everything after the last punctuation
        input_string = input_string[:last_punctuation_index + 1]

        if any(input_string.endswith(face) for face in faces_to_keep):
            return input_string

    # If none of the faces are found or there's no punctuation, just append the word to the resulting string
    return input_string + " Awoof~! ^^"
