#!/usr/bin/env python3
"""
Retry Handler - Gold Tier Error Recovery
Implements exponential backoff retry logic for transient failures.
"""

import time
import logging
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def with_retry(max_attempts=3, base_delay=1, max_delay=60):
    """
    Decorator that implements exponential backoff retry logic.

    Args:
        max_attempts (int): Maximum number of retry attempts (default: 3)
        base_delay (float): Initial delay in seconds (default: 1)
        max_delay (float): Maximum delay between retries in seconds (default: 60)

    Returns:
        Decorated function with retry logic

    Example:
        @with_retry(max_attempts=3, base_delay=2, max_delay=30)
        def fetch_data():
            # Your code here
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0

            while attempt < max_attempts:
                try:
                    # Attempt to execute the function
                    return func(*args, **kwargs)

                except Exception as e:
                    attempt += 1

                    # Check if this was the last attempt
                    if attempt >= max_attempts:
                        logger.error(
                            f"[RETRY FAILED] {func.__name__} failed after {max_attempts} attempts. "
                            f"Last error: {type(e).__name__}: {str(e)}"
                        )
                        raise  # Re-raise the exception after all retries exhausted

                    # Calculate exponential backoff delay
                    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)

                    logger.warning(
                        f"[RETRY {attempt}/{max_attempts}] {func.__name__} failed with {type(e).__name__}: {str(e)}. "
                        f"Retrying in {delay:.1f} seconds..."
                    )

                    # Wait before retrying
                    time.sleep(delay)

        return wrapper
    return decorator


# Example usage and testing
if __name__ == '__main__':
    print("Testing retry handler...\n")

    # Test 1: Function that succeeds on third attempt
    attempt_counter = {'count': 0}

    @with_retry(max_attempts=5, base_delay=1, max_delay=10)
    def flaky_function():
        attempt_counter['count'] += 1
        if attempt_counter['count'] < 3:
            raise ConnectionError(f"Simulated network error (attempt {attempt_counter['count']})")
        return "Success!"

    try:
        result = flaky_function()
        print(f"Test 1 Result: {result}\n")
    except Exception as e:
        print(f"Test 1 Failed: {e}\n")

    # Test 2: Function that always fails
    @with_retry(max_attempts=3, base_delay=0.5, max_delay=5)
    def always_fails():
        raise ValueError("This always fails")

    try:
        always_fails()
    except ValueError as e:
        print(f"Test 2 Expected Failure: {e}\n")

    print("Retry handler tests complete!")
