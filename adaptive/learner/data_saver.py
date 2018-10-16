# -*- coding: utf-8 -*-
from collections import OrderedDict
import functools


class DataSaver:
    """Save extra data associated with the values that need to be learned.

    Parameters
    ----------
    learner : `~adaptive.BaseLearner` instance
        The learner that needs to be wrapped.
    arg_picker : function
        Function that returns the argument that needs to be learned.

    Example
    -------
    Imagine we have a function that returns a dictionary
    of the form: ``{'y': y, 'err_est': err_est}``.
    
    >>> from operator import itemgetter
    >>> _learner = Learner1D(f, bounds=(-1.0, 1.0))
    >>> learner = DataSaver(_learner, arg_picker=itemgetter('y'))
    """

    def __init__(self, learner, arg_picker):
        self.learner = learner
        self.extra_data = OrderedDict()
        self.function = learner.function
        self.arg_picker = arg_picker

    def __getattr__(self, attr):
        return getattr(self.learner, attr)

    def tell(self, x, result):
        y = self.arg_picker(result)
        self.extra_data[x] = result
        self.learner.tell(x, y)

    def tell_pending(self, x):
        self.learner.tell_pending(x)


def _ds(learner_type, arg_picker, *args, **kwargs):
    args = args[2:]  # functools.partial passes the first 2 arguments in 'args'!
    return DataSaver(learner_type(*args, **kwargs), arg_picker)


def make_datasaver(learner_type, arg_picker):
    """Create a `DataSaver` of a `learner_type` that can be instantiated
    with the `learner_type`'s key-word arguments.

    Parameters
    ----------
    learner_type : `~adaptive.BaseLearner` type
        The learner type that needs to be wrapped.
    arg_picker : function
        Function that returns the argument that needs to be learned.

    Example
    -------
    Imagine we have a function that returns a dictionary
    of the form: ``{'y': y, 'err_est': err_est}``.

    >>> from operator import itemgetter
    >>> DataSaver = make_datasaver(Learner1D, arg_picker=itemgetter('y'))
    >>> learner = DataSaver(function=f, bounds=(-1.0, 1.0))

    Or when using `adaptive.BalancingLearner.from_product`:

    >>> learner_type = make_datasaver(adaptive.Learner1D,
    ...     arg_picker=itemgetter('y'))
    >>> learner = adaptive.BalancingLearner.from_product(
    ...     jacobi, learner_type, dict(bounds=(0, 1)), combos)
    """
    return functools.partial(_ds, learner_type, arg_picker)
