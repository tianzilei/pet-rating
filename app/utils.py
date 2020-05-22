import os
import tempfile
from itertools import zip_longest
from flask import send_file


def map_values_to_int(values: dict):
    values = [map(int, i) for i in list(values.values())]
    return zip_longest(*values, fillvalue=None)


def calculate_mean(values: list) -> float:
    n_answers = sum(x is not None for x in values)
    sum_of_answers = float(sum(filter(None, values)))
    mean = sum_of_answers / n_answers
    return round(mean, 2)


def get_mean_from_slider_answers(answers):
    return [calculate_mean(values) for values in map_values_to_int(answers)]


def saved_data_as_file(filename, data):
    """write CSV data to temporary file on host and send that file
    to requestor"""
    try:
        fd, path = tempfile.mkstemp()
        with os.fdopen(fd, 'w') as tmp:
            tmp.write(data)
            tmp.flush()
            return send_file(path,
                             mimetype='text/csv',
                             as_attachment=True,
                             attachment_filename=filename)
    finally:
        os.remove(path)
