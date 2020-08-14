"""Context manager for the package."""

from functools import partial
from typing import Any, Callable


class HistoryManager:
    """
    Define a base context manager.

    It records a list of actions to be taken at a later time.
    This is used to implement context managers that allow temporary
    changes to a `cobra.core.Model`.

    """

    def __init__(self):
        """Initialize the class."""
        # this acts like a stack
        self._history = []

    def __call__(self, operation: Callable[[Any], Any]):
        """Add the corresponding operation to the history stack.

        Parameters
        ----------
        operation : callable
            A function to be called at a later time.

        """
        self._history.append(operation)

    def reset(self):
        """Trigger executions for all items in the stack in reverse order."""
        while self._history:
            entry = self._history.pop()
            entry()


def get_context(obj):
    """Search for a context manager.

    Parameters
    ----------
    obj: cobra.Object
        The cobra.Object for which to search context manager.

    Returns
    -------
    None

    Raises
    ------
    AttributeError
        If no context manager is found.
    IndexError
        If no context manager is found.

    """
    # works for cobra.core.Model objects
    try:
        return obj._contexts[-1]
    except (AttributeError, IndexError):
        pass
    # works for objects other than cobra.core.Model
    try:
        return obj._model._contexts[-1]
    except (AttributeError, IndexError):
        pass

    return None


def resettable(f: Callable[[Any], Any]):
    """
    Simplify the context management of simple object attributes.

    It gets the value of the attribute prior to setting it, and stores
    a function to set the value to the old value in the
    `cobra.util.HistoryManager`.

    Parameters
    ----------
    f: callable
        The function to decorate.

    Returns
    -------
    callable
        The decorated function.

    """

    def wrapper(self, new_value):
        context = get_context(self)
        if context:
            old_value = getattr(self, f.__name__)
            # Don't clutter the context with unchanged variables
            if old_value == new_value:
                return
            context(partial(f, self, old_value))

        f(self, new_value)

    return wrapper
