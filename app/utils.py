import os
import tempfile
import time
from itertools import zip_longest
from flask import send_file


from app import app


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('{} {:2.2f} ms'.format(method.__name__, (te - ts) * 1000))
        return result

    return timed


def map_values_to_int(values: dict):
    #values = [map(int, i) for i in list(values.values())]
    return zip_longest(*values.values(), fillvalue=None)


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


def question_matches_answer(question, answer):
    if (answer.page_idpage == question[0] and answer.question_idquestion == question[1]):
        return True
    return False


def map_answers_to_questions(answers, questions):
    '''
    questions = [(4, 1), (4, 2), (5, 1), (5, 2), (6, 1), (6, 2)]
    +
    answers = [{p:6, q:1, a:100}, {p:6, q:2, a:99}]
    ->
    partial_answer = [None, None, None, None, 100, 99]
    '''

    # results = []
    results = list(map(lambda x: None, questions))

    nth_answer = 0

    for nth_question, question in enumerate(questions):

        try:
            current_answer = answers[nth_answer]
        except IndexError:
            break

        if question_matches_answer(question, current_answer):
            results[nth_question] = int(current_answer.answer)
            nth_answer += 1

    return results

    '''
    return list(map(
        lambda x: get_values_from_list_of_answers(x, answers),
        questions))
    '''


'''
select sub.answer_set_idanswer_set, group_concat(concat(
    COALESCE(sub.aa, ''), 
    COALESCE(sub.ab, ''), 
    COALESCE(sub.ba, ''), 
    COALESCE(sub.bb, ''), 
    COALESCE(sub.ca, ''), 
    COALESCE(sub.cb, '')
)) 
FROM (     
    select  *, 
        case when page_idpage = 4 and question_idquestion = 1 then answer end as aa,
        case when page_idpage = 4 and question_idquestion = 2 then answer end as ab,
        case when page_idpage = 5 and question_idquestion = 1 then answer end as ba,
        case when page_idpage = 5 and question_idquestion = 2 then answer end as bb,
        case when page_idpage = 6 and question_idquestion = 1 then answer end as ca,
        case when page_idpage = 6 and question_idquestion = 2 then answer end as cb
    from answer where answer_set_idanswer_set in ( select idanswer_set from answer_set where experiment_idexperiment = 2 and answer_counter != 0 )  
) as sub 
group by sub.answer_set_idanswer_set;




# all possible page/question comobs
select distinct p.idpage, q.idquestion from question q join page p on p.experiment_idexperiment=q.experiment_idexperiment where p.experiment_idexperiment = 2 order by p.idpage,q.idquestion;
'''