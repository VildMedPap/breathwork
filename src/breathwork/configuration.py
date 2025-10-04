"""Configuration module for breathwork display and behavior settings."""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class DisplayConfig:
    """Display configuration settings."""

    # Box dimensions
    BOX_WIDTH: int = 40
    PADDING_TOP: int = 3
    PADDING_BOTTOM: int = 3

    # Sidebar settings
    SIDEBAR_ENABLED: bool = True
    SIDEBAR_WIDTH: int = 25
    SIDEBAR_POSITION: str = "right"  # "left" or "right"
    SIDEBAR_PADDING: int = 2

    # Progress indicators
    PROGRESS_COMPLETED: str = "✓"
    PROGRESS_CURRENT: str = "▶"
    PROGRESS_PENDING: str = " "

    # Visual effects
    WARNING_THRESHOLD: int = (
        5  # Start warning visual when countdown reaches this many seconds
    )
    WARNING_STYLE: str = (
        "1"  # ANSI code for bright/bold (makes colors brighter/more vivid)
    )

    # Phase colors (ANSI color codes)
    COLORS: Dict[str, str] = field(
        default_factory=lambda: {
            "cyan": "36",
            "yellow": "33",
            "green": "32",
            "red": "31",
            "white": "37",
            "blue": "34",
            "bold": "1",
            "reset": "0",
        }
    )

    # Phase color mapping
    PHASE_COLORS: Dict[str, str] = field(
        default_factory=lambda: {
            "breathing": "cyan",
            "hold": "yellow",
            "countdown": "red",
        }
    )

    # Phase titles
    PHASE_TITLES: Dict[str, str] = field(
        default_factory=lambda: {
            "prepare": "Prepare",
            "hold": "Hold breath",
            "breathe": "Breathe {duration}s",
            "final_hold": "Final hold",
        }
    )

    # Border characters
    BORDER_TOP_LEFT: str = "╭"
    BORDER_TOP_RIGHT: str = "╮"
    BORDER_BOTTOM_LEFT: str = "╰"
    BORDER_BOTTOM_RIGHT: str = "╯"
    BORDER_HORIZONTAL: str = "─"
    BORDER_VERTICAL: str = "│"

    # Terminal control sequences
    HIDE_CURSOR: str = "\033[?25l"
    SHOW_CURSOR: str = "\033[?25h"
    CLEAR_SCREEN: str = "\033[2J"
    HOME_CURSOR: str = "\033[H"
    CLEAR_TO_END: str = "\033[J"

    # Audio settings
    BELL_CHAR: str = "\x07"
    BELL_PRINT: str = "\a"


@dataclass
class ExerciseDefaults:
    """Default exercise configuration values."""

    # Default durations
    DEFAULT_HOLD_DURATION: int = 60
    DEFAULT_STEP_DURATIONS: str = "30,20,10"
    DEFAULT_COUNTDOWN_THRESHOLD: int = 0

    # Duration limits
    MIN_HOLD_DURATION: int = 1
    MAX_HOLD_DURATION: int = 300
    MIN_STEP_DURATION: int = 1
    MAX_STEP_DURATION: int = 300
    MIN_COUNTDOWN: int = 0
    MAX_COUNTDOWN: int = 10

    # Phase messages
    PREPARATION_INSTRUCTION: str = "Prepare"
    HOLD_INSTRUCTION: str = "Hold"
    BREATHING_INSTRUCTION: str = "Breathe"

    # Completion messages
    COMPLETION_MESSAGE: str = "Exercise Complete! Great job!"
    COMPLETION_TITLE: str = "Congratulations"
    INTERRUPTION_MESSAGE: str = "\nExercise interrupted by user"

    # Error messages
    ERROR_PREFIX: str = "Error:"
    UNEXPECTED_ERROR_PREFIX: str = "Unexpected error:"


@dataclass
class TimingConfig:
    """Timing configuration for the exercise loop."""

    # Main loop timing
    LOOP_SLEEP_INTERVAL: float = 0.1  # Sleep between loop iterations
    TRANSITION_PAUSE: float = 1.0  # Pause for phase transitions in plain mode

    # Beep timing (for Windows)
    BEEP_FREQUENCY: int = 800  # Hz
    BEEP_DURATION: int = 200  # milliseconds


# Create singleton instances
display_config = DisplayConfig()
exercise_defaults = ExerciseDefaults()
timing_config = TimingConfig()
