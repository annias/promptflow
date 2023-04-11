"""
Utility functions for promptflow.
"""

import time
import random
import logging
import openai


# from https://github.com/openai/openai-cookbook/blob/main/examples/How_to_handle_rate_limits.ipynb
def retry_with_exponential_backoff(
    func,
    initial_delay: float = 1,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 10,
    errors: tuple = (
        openai.error.RateLimitError,  # type: ignore
        openai.error.ServiceUnavailableError,  # type: ignore
    ),
):
    """Retry a function with exponential backoff."""

    def wrapper(*args, **kwargs):
        # Initialize variables
        num_retries = 0
        delay = initial_delay

        # Loop until a successful response or max_retries is hit or an exception is raised
        while True:
            try:
                return func(*args, **kwargs)

            # Retry on specified errors
            except errors as oai_err:
                logging.warning(f"Error: {oai_err}. Retrying in {delay} seconds.")
                # Increment retries
                num_retries += 1

                # Check if max retries has been reached
                if num_retries > max_retries:
                    raise ConnectionError(
                        f"Maximum number of retries ({max_retries}) exceeded."
                    ) from oai_err

                # Increment the delay
                delay *= exponential_base * (1 + jitter * random.random())

                # Sleep for the delay
                time.sleep(delay)

            # Raise exceptions for any errors not specified
            except Exception as oai_err:
                raise oai_err

    return wrapper
