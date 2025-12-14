"""Decorators for pipeline utilities."""

import functools
from collections.abc import Callable
from typing import Any


def with_progress_callback(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator that ensures a function has a progress_callback parameter.

    If progress_callback is not provided when calling the function,
    injects a no-op lambda so the function can call it without checking.

    Example:
        @with_progress_callback
        def process_images(images: list[str], progress_callback):
            for i, img in enumerate(images):
                process(img)
                progress_callback((i + 1) / len(images) * 100)

        # Call with progress tracking
        process_images(images, progress_callback=context.update_step_progress)

        # Call without progress tracking (no-op injected automatically)
        process_images(images)

    Args:
        func: Function to decorate

    Returns:
        Wrapped function with automatic progress_callback injection
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if "progress_callback" not in kwargs:
            kwargs["progress_callback"] = lambda _: None
        return func(*args, **kwargs)

    return wrapper
