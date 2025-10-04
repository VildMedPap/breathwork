"""Timer implementation using monotonic time for drift-free timing."""

import time
from typing import Optional


class Timer:
    """A drift-free timer using monotonic time."""

    def __init__(self, duration: float, countdown_threshold: float = 3.0):
        """Initialize timer with duration and countdown threshold.

        Args:
            duration: Timer duration in seconds
            countdown_threshold: Seconds before expiry to enter countdown mode
        """
        if duration <= 0:
            raise ValueError("Duration must be positive")
        if countdown_threshold < 0:
            raise ValueError("Countdown threshold must be non-negative")

        self.duration = duration
        self.countdown_threshold = countdown_threshold
        self._start_time: Optional[float] = None
        self._is_running = False

    def start(self):
        """Start the timer."""
        if self._is_running:
            raise RuntimeError("Timer is already running")
        self._start_time = time.monotonic()
        self._is_running = True

    def reset(self):
        """Reset the timer to initial state."""
        self._start_time = None
        self._is_running = False

    def is_running(self) -> bool:
        """Check if timer is currently running."""
        return self._is_running

    def is_expired(self) -> bool:
        """Check if timer has expired."""
        if not self._is_running:
            return False
        return self.elapsed() >= self.duration

    def is_complete(self) -> bool:
        """Alias for is_expired()."""
        return self.is_expired()

    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self._start_time is None:
            return 0.0
        return time.monotonic() - self._start_time

    def remaining_time(self) -> float:
        """Get remaining time in seconds."""
        if not self._is_running:
            return self.duration
        remaining = self.duration - self.elapsed()
        return max(0.0, remaining)

    def in_countdown(self) -> bool:
        """Check if timer is in countdown phase."""
        if not self._is_running:
            return False
        if self.countdown_threshold == 0:
            return False
        return 0 < self.remaining_time() <= self.countdown_threshold

    def __str__(self) -> str:
        """String representation of timer."""
        if not self._is_running:
            return f"Timer({self.duration}s, not started)"
        elif self.is_expired():
            return f"Timer({self.duration}s, expired)"
        else:
            return f"Timer({self.duration}s, {self.remaining_time():.1f}s remaining)"

    def __repr__(self) -> str:
        """Detailed representation of timer."""
        return (
            f"Timer(duration={self.duration}, "
            f"countdown_threshold={self.countdown_threshold}, "
            f"is_running={self._is_running}, "
            f"elapsed={self.elapsed():.1f})"
        )
