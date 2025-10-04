"""Data models for the breathwork application."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class PhaseType(Enum):
    """Types of phases in a breathing exercise."""

    BREATHING = "breathing"
    HOLD = "hold"


class PhaseState(Enum):
    """States of a phase during execution."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COUNTDOWN = "countdown"
    COMPLETED = "completed"


class DisplayMode(Enum):
    """Display modes for the application."""

    TUI = "tui"
    PLAIN = "plain"


@dataclass
class Phase:
    """Represents a single phase in a breathing exercise."""

    type: PhaseType
    duration: int  # in seconds
    instruction: str
    color: str = "cyan"
    _state: PhaseState = field(default=PhaseState.NOT_STARTED, init=False)

    @property
    def state(self) -> PhaseState:
        """Get the current state of the phase."""
        return self._state

    def start(self):
        """Start the phase."""
        if self._state != PhaseState.NOT_STARTED:
            raise RuntimeError(f"Cannot start phase in state {self._state}")
        self._state = PhaseState.IN_PROGRESS

    def enter_countdown(self):
        """Enter countdown state."""
        if self._state != PhaseState.IN_PROGRESS:
            raise RuntimeError(f"Cannot enter countdown from state {self._state}")
        self._state = PhaseState.COUNTDOWN

    def complete(self):
        """Mark the phase as completed."""
        if self._state not in (PhaseState.IN_PROGRESS, PhaseState.COUNTDOWN):
            raise RuntimeError(f"Cannot complete phase in state {self._state}")
        self._state = PhaseState.COMPLETED

    def is_not_started(self) -> bool:
        """Check if phase has not started."""
        return self._state == PhaseState.NOT_STARTED

    def is_in_progress(self) -> bool:
        """Check if phase is in progress."""
        return self._state == PhaseState.IN_PROGRESS

    def is_in_countdown(self) -> bool:
        """Check if phase is in countdown."""
        return self._state == PhaseState.COUNTDOWN

    def is_completed(self) -> bool:
        """Check if phase is completed."""
        return self._state == PhaseState.COMPLETED

    def __str__(self) -> str:
        """String representation of the phase."""
        return f"{self.type.value} ({self.duration}s) - {self._state.value}"

    def __repr__(self) -> str:
        """Detailed representation of the phase."""
        return f"Phase(type={self.type}, duration={self.duration}, state={self._state})"

    def __eq__(self, other) -> bool:
        """Check equality based on type, duration, instruction, and color."""
        if not isinstance(other, Phase):
            return False
        return (
            self.type == other.type
            and self.duration == other.duration
            and self.instruction == other.instruction
            and self.color == other.color
        )


@dataclass
class ExerciseConfig:
    """Configuration for a breathing exercise."""

    hold_duration: int = 60  # seconds
    step_durations: List[int] = field(default_factory=lambda: [30, 20, 10])  # seconds
    countdown_beep_threshold: int = (
        5  # when to start countdown beeps (seconds before phase ends)
    )
    preparation_duration: int = 0  # preparation phase duration in seconds
    audio_enabled: bool = True
    display_mode: DisplayMode = DisplayMode.TUI

    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()

    def validate(self):
        """Validate the configuration."""
        if self.hold_duration <= 0:
            raise ValueError(
                f"Hold duration must be positive (got {self.hold_duration})"
            )
        if self.hold_duration > 300:
            raise ValueError(
                f"Hold duration cannot exceed 300 seconds (got {self.hold_duration})"
            )

        if not self.step_durations:
            raise ValueError(
                "Step durations cannot be empty. Provide at least one breathing step duration."
            )

        for i, duration in enumerate(self.step_durations):
            if duration <= 0:
                raise ValueError(
                    f"All step durations must be positive. Step {i + 1} has invalid duration: {duration}"
                )
            if duration > 120:
                raise ValueError(
                    f"Step durations cannot exceed 120 seconds. Step {i + 1} has duration: {duration}"
                )

        if self.countdown_beep_threshold < 0:
            raise ValueError(
                f"Countdown beep threshold must be non-negative (got {self.countdown_beep_threshold})"
            )

        if self.preparation_duration < 0:
            raise ValueError(
                f"Preparation duration must be non-negative (got {self.preparation_duration})"
            )

    @classmethod
    def from_cli_args(
        cls,
        hold: int,
        steps: str,
        countdown: int,
        preparation: int,
        tui: bool,
        audio: str,
    ) -> "ExerciseConfig":
        """Create config from CLI arguments."""
        # Parse steps string
        if not steps or not steps.strip():
            raise ValueError(
                "Step durations cannot be empty. Provide at least one breathing step duration (e.g., '30,20,10')"
            )

        try:
            parts = steps.split(",")
            step_durations = []
            for i, part in enumerate(parts):
                stripped = part.strip()
                if not stripped:
                    raise ValueError(
                        f"Invalid steps format '{steps}'. Empty value at position {i + 1}. Must be comma-separated positive integers (e.g., '30,20,10')"
                    )
                step_durations.append(int(stripped))
        except (ValueError, AttributeError) as e:
            # Re-raise if it's already our custom error
            if "Invalid steps format" in str(
                e
            ) or "Step durations cannot be empty" in str(e):
                raise
            # Otherwise provide helpful message for parsing errors
            raise ValueError(
                f"Invalid steps format '{steps}'. Must be comma-separated positive integers (e.g., '30,20,10')"
            )

        # Parse audio setting
        audio_enabled = audio.lower() == "beep"

        # Parse display mode
        display_mode = DisplayMode.TUI if tui else DisplayMode.PLAIN

        return cls(
            hold_duration=hold,
            step_durations=step_durations,
            countdown_beep_threshold=countdown,
            preparation_duration=preparation,
            audio_enabled=audio_enabled,
            display_mode=display_mode,
        )
