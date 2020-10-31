import statistics
import time
from functools import wraps
from typing import List


def time_execution(func):
    """
    Decorator to time function execution
    :param func: function to wrap
    :return: wrapped function
    """

    @wraps(func)
    def wrapped_function(*args, **kwargs):
        """
        Wrapped function execution
        :return: output and execution time
        """
        start_time = time.time()
        output = func(*args, **kwargs)
        end_time = time.time()
        return output, end_time - start_time

    return wrapped_function


def percentile(values: List[float], percent: float):
    """
    Find the percentile of a list of values
    :param values: list of values
    :param percent: float value from 0.0 to 1.0
    :return: the percentile of the values
    """
    return statistics.quantiles(values, n=100, method="inclusive")[
        int(percent * 100 - 1)
    ]


def median(values: List[float]):
    """
    Function to calculate median value from a list of values
    :param values: list of values
    :return: median value of the list
    """
    return statistics.median(values)
