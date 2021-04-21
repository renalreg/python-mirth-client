import inspect
import warnings
from functools import wraps
from typing import Any, Callable, TypeVar, cast

T = TypeVar("T", bound=Callable)  # pylint: disable=invalid-name


def deprecated(func: T) -> T:  # pylint: disable=missing-function-docstring
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        warnings.warn(
            f"{func.__qualname__} is deprecated and will be removed in version 0.5.0",
            DeprecationWarning,
            stacklevel=2,
        )
        return func(*args, **kwargs)

    wrapper.__signature__ = inspect.signature(func)  # type: ignore
    return cast(T, wrapper)
