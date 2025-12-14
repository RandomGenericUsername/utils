"""Test decorator functionality."""

import pytest

from task_pipeline.decorators import with_progress_callback


class TestWithProgressCallbackDecorator:
    """Test the @with_progress_callback decorator."""

    def test_decorator_injects_noop_callback(self):
        """Test that decorator injects no-op callback when not provided."""

        @with_progress_callback
        def my_function(data: str, progress_callback):
            # Should be able to call progress_callback without checking if None
            progress_callback(25.0)
            progress_callback(50.0)
            progress_callback(100.0)
            return f"processed_{data}"

        # Call without progress_callback - should not raise
        result = my_function("test")
        assert result == "processed_test"

    def test_decorator_uses_provided_callback(self):
        """Test that decorator uses provided callback when given."""
        progress_updates = []

        @with_progress_callback
        def my_function(data: str, progress_callback):
            progress_callback(25.0)
            progress_callback(50.0)
            progress_callback(75.0)
            progress_callback(100.0)
            return f"processed_{data}"

        # Call with progress_callback
        result = my_function(
            "test", progress_callback=lambda p: progress_updates.append(p)
        )

        assert result == "processed_test"
        assert progress_updates == [25.0, 50.0, 75.0, 100.0]

    def test_decorator_with_multiple_parameters(self):
        """Test decorator with function that has multiple parameters."""

        @with_progress_callback
        def complex_function(a: int, b: str, c: float, progress_callback):
            progress_callback(50.0)
            return a + len(b) + int(c)

        # Without callback
        result = complex_function(10, "hello", 5.5)
        assert result == 20  # 10 + 5 + 5

        # With callback
        updates = []
        result = complex_function(
            10, "hello", 5.5, progress_callback=lambda p: updates.append(p)
        )
        assert result == 20
        assert updates == [50.0]

    def test_decorator_preserves_function_metadata(self):
        """Test that decorator preserves function name and docstring."""

        @with_progress_callback
        def documented_function(data: str, progress_callback):
            """This is a documented function."""
            return data

        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ == "This is a documented function."

    def test_decorator_with_return_value(self):
        """Test that decorator doesn't interfere with return values."""

        @with_progress_callback
        def returns_dict(progress_callback):
            progress_callback(100.0)
            return {"status": "success", "value": 42}

        result = returns_dict()
        assert result == {"status": "success", "value": 42}

    def test_decorator_with_no_callback_calls(self):
        """Test decorator when function never calls progress_callback."""

        @with_progress_callback
        def no_progress_calls(data: str, progress_callback):
            # Never call progress_callback
            return data.upper()

        result = no_progress_calls("hello")
        assert result == "HELLO"

    def test_decorator_with_exception(self):
        """Test that decorator doesn't interfere with exception handling."""

        @with_progress_callback
        def raises_exception(progress_callback):
            progress_callback(50.0)
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            raises_exception()

    def test_decorator_callback_as_kwarg_explicitly(self):
        """Test that callback must be passed as keyword argument."""
        updates = []

        @with_progress_callback
        def my_function(data: str, progress_callback):
            progress_callback(100.0)
            return data

        # Pass callback as keyword arg (recommended way)
        result = my_function(
            "test", progress_callback=lambda p: updates.append(p)
        )
        assert result == "test"
        assert updates == [100.0]

    def test_decorator_with_default_parameters(self):
        """Test decorator with function that has default parameters."""

        @with_progress_callback
        def with_defaults(
            data: str, multiplier: int = 2, progress_callback=None
        ):
            if progress_callback:
                progress_callback(50.0)
            return data * multiplier

        # Without any optional args
        result = with_defaults("x")
        assert result == "xx"

        # With multiplier
        result = with_defaults("x", 3)
        assert result == "xxx"

        # With callback
        updates = []
        result = with_defaults(
            "x", progress_callback=lambda p: updates.append(p)
        )
        assert result == "xx"
        assert updates == [50.0]

    def test_decorator_multiple_calls(self):
        """Test that decorator works correctly across multiple calls."""
        call_count = [0]

        @with_progress_callback
        def counting_function(progress_callback):
            call_count[0] += 1
            progress_callback(100.0)
            return call_count[0]

        # First call
        result1 = counting_function()
        assert result1 == 1

        # Second call
        result2 = counting_function()
        assert result2 == 2

        # Third call with callback
        updates = []
        result3 = counting_function(
            progress_callback=lambda p: updates.append(p)
        )
        assert result3 == 3
        assert updates == [100.0]

    def test_decorator_with_kwargs_only(self):
        """Test decorator with function that uses **kwargs."""

        @with_progress_callback
        def kwargs_function(progress_callback, **kwargs):
            progress_callback(50.0)
            return kwargs

        result = kwargs_function(a=1, b=2, c=3)
        assert result == {"a": 1, "b": 2, "c": 3}
