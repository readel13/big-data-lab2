import functools
from time import perf_counter

def measure_time(func):
    """Measures the execution time of the function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = perf_counter()

        # Execute the function
        func(*args, **kwargs)

        end = perf_counter()
        measured_time = round(end - start, 5)

        print(f"Function {func.__name__} has been executed in {measured_time * 1000} ms")
    return wrapper

def sep_print_block(symbol):
    """Separates printing block with desired characters."""
    def inner_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            separator = symbol * 42

            print(separator)

            # Execute the function
            func(*args, *kwargs)

            print(separator)
        return wrapper
    return inner_decorator