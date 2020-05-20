from itertools import zip_longest


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
