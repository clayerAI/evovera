import signal
import time

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Algorithm timed out")

def run_with_timeout(func, timeout_seconds):
    """Run a function with timeout."""
    # Set the signal handler
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    
    try:
        result = func()
        signal.alarm(0)  # Cancel the alarm
        return result
    except TimeoutException:
        return None
    finally:
        signal.alarm(0)  # Ensure alarm is always cancelled
