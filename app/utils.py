import os
import tempfile
from itertools import zip_longest
from flask import send_file


def map_values_to_int(values: dict):
    #values = [map(int, i) for i in list(values.values())]
    return zip_longest(*values.values(), fillvalue=None)


def calculate_mean(values: list) -> float:
    print(values)
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


def get_values_from_list_of_answers(page_question, answers):
    page_id = page_question[0]
    question_id = page_question[1]
    for _answer in answers:
        try:
            if _answer.question_idquestion == question_id and \
                    _answer.page_idpage == page_id:
                return int(_answer.answer)
        except AttributeError:
            if _answer.embody_question_idembody == question_id and \
                    _answer.page_idpage == page_id:
                return _answer
    return None


def map_answers_to_questions(answers, questions):
    '''
    questions = [(4, 1), (4, 2), (5, 1), (5, 2), (6, 1), (6, 2)]
    +
    answers = [{p:6, q:1, a:100}, {p:6, q:2, a:99}]
    ->
    partial_answer = [None, None, None, None, 100, 99]
    '''
    return list(map(
        lambda x: get_values_from_list_of_answers(x, answers),
        questions))
