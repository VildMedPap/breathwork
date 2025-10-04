"""Display module for showing exercise progress using Rich."""

import os
import sys
from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from breathwork.ascii_art import get_ascii_time
from breathwork.models import DisplayMode, Phase, PhaseState
from breathwork.configuration import display_config, exercise_defaults, timing_config


class Display:
    """Handles display output for the breathing exercise."""

    def __init__(
        self, mode: DisplayMode = DisplayMode.TUI, phases: Optional[List[Phase]] = None
    ):
        """Initialize display with specified mode.

        Args:
            mode: Display mode (TUI or PLAIN)
            phases: List of all phases in the exercise for progress tracking
        """
        self.mode = mode
        self.console = Console()
        self._last_output = ""
        self._display_initialized = False
        self.all_phases = phases or []
        self.current_phase_index = 0

    def start_live_display(self):
        """Start live display for TUI mode."""
        if self.mode == DisplayMode.TUI:
            # Clear screen and hide cursor
            sys.stdout.write(display_config.CLEAR_SCREEN)
            sys.stdout.write(display_config.HOME_CURSOR)
            sys.stdout.write(display_config.HIDE_CURSOR)
            sys.stdout.flush()
            self._display_initialized = True

    def stop_live_display(self):
        """Stop live display."""
        if self.mode == DisplayMode.TUI and self._display_initialized:
            # Show cursor (but don't clear - keep the final display visible)
            sys.stdout.write(display_config.SHOW_CURSOR)
            sys.stdout.flush()
            self._display_initialized = False

    def clear_screen(self):
        """Clear the terminal screen."""
        if self.mode == DisplayMode.TUI:
            os.system("cls" if os.name == "nt" else "clear")

    def set_current_phase_index(self, index: int):
        """Update the current phase index for progress tracking."""
        self.current_phase_index = index

    def _build_sidebar(self) -> List[str]:
        """Build the progress sidebar showing all phases."""
        sidebar_lines = []
        sidebar_width = display_config.SIDEBAR_WIDTH

        for idx, phase in enumerate(self.all_phases):
            # Determine phase status
            if idx < self.current_phase_index:
                indicator = display_config.PROGRESS_COMPLETED
                style = "dim"
            elif idx == self.current_phase_index:
                # Check if this is the last phase and it's completed
                if phase._state == PhaseState.COMPLETED:
                    indicator = display_config.PROGRESS_COMPLETED
                    style = "dim"
                else:
                    indicator = display_config.PROGRESS_CURRENT
                    style = "current"
            else:
                indicator = display_config.PROGRESS_PENDING
                style = "pending"

            # Get phase color
            color_code = display_config.COLORS.get(
                phase.color, display_config.COLORS["white"]
            )

            # Format phase name with duration in brackets (except for Complete phase)
            if phase.instruction == "Complete":
                phase_name = phase.instruction
            else:
                phase_name = f"{phase.instruction} ({phase.duration}s)"

            if len(phase_name) > sidebar_width - 3:
                phase_name = phase_name[: sidebar_width - 6] + "..."

            # Build the line with color
            if style == "current":
                line = f"\033[{display_config.COLORS['bold']};{color_code}m{indicator} {phase_name}\033[{display_config.COLORS['reset']}m"
            elif style == "dim":
                line = f"\033[2m{indicator} {phase_name}\033[{display_config.COLORS['reset']}m"
            else:
                line = f"\033[{color_code}m{indicator} {phase_name}\033[{display_config.COLORS['reset']}m"

            sidebar_lines.append(line)

        return sidebar_lines

    def show_countdown(
        self,
        seconds: int,
        phase: Optional[Phase] = None,
        phase_index: Optional[int] = None,
    ):
        """Display countdown timer.

        Args:
            seconds: Seconds remaining
            phase: Current phase for context
            phase_index: Index of current phase for progress tracking
        """
        # Update current phase index for progress tracking
        if phase_index is not None:
            self.set_current_phase_index(phase_index)

        if self.mode == DisplayMode.TUI:
            self._show_tui_countdown(seconds, phase)
        else:
            self._show_plain_countdown(seconds, phase)

    def _show_tui_countdown(self, seconds: int, phase: Optional[Phase]):
        """Show countdown in TUI mode with ASCII art."""
        if not self._display_initialized:
            return

        minutes = seconds // 60
        secs = seconds % 60

        # Get terminal dimensions

        # Get ASCII art for the time
        ascii_lines = get_ascii_time(minutes, secs)

        # Get phase info
        if phase:
            title = phase.instruction.upper()
            color_code = display_config.COLORS.get(
                phase.color, display_config.COLORS["white"]
            )
        else:
            title = "Breathwork Exercise"
            color_code = display_config.COLORS["white"]

        # Disable warning effect for now
        should_warn = False

        # Build the display manually
        lines = []

        # Fixed box width for consistency
        box_width = display_config.BOX_WIDTH

        # Top border with title
        title_display = f" {title} " if title else ""
        top_border = (
            display_config.BORDER_TOP_LEFT
            + display_config.BORDER_HORIZONTAL
            * ((box_width - len(title_display) - 2) // 2)
            + title_display
        )
        top_border += (
            display_config.BORDER_HORIZONTAL * (box_width - len(top_border) - 1)
            + display_config.BORDER_TOP_RIGHT
        )

        # Add color to top border (with warning brightness if needed)
        if should_warn:
            lines.append(
                f"\033[{display_config.WARNING_STYLE};{color_code}m{top_border}\033[{display_config.COLORS['reset']}m"
            )
        else:
            lines.append(
                f"\033[{color_code}m{top_border}\033[{display_config.COLORS['reset']}m"
            )

        # Calculate vertical padding
        (len(ascii_lines) + display_config.PADDING_TOP + display_config.PADDING_BOTTOM)
        padding_top = display_config.PADDING_TOP
        padding_bottom = display_config.PADDING_BOTTOM

        # Determine border and content styles based on warning
        if should_warn:
            border_style = f"\033[{display_config.WARNING_STYLE};{color_code}m"
            content_style = f"\033[{display_config.WARNING_STYLE};{color_code}m"  # Brighter, more vivid
        else:
            border_style = f"\033[{color_code}m"
            content_style = f"\033[{display_config.COLORS['bold']};{color_code}m"

        reset = f"\033[{display_config.COLORS['reset']}m"

        # Add top padding
        for _ in range(padding_top):
            lines.append(
                f"{border_style}{display_config.BORDER_VERTICAL}{reset}"
                + " " * (box_width - 2)
                + f"{border_style}{display_config.BORDER_VERTICAL}{reset}"
            )

        # Add ASCII art lines (centered)
        for line in ascii_lines:
            padding_needed = box_width - 2 - len(line)
            left_pad = padding_needed // 2
            right_pad = padding_needed - left_pad
            content = " " * left_pad + f"{content_style}{line}{reset}" + " " * right_pad
            lines.append(
                f"{border_style}{display_config.BORDER_VERTICAL}{reset}{content}{border_style}{display_config.BORDER_VERTICAL}{reset}"
            )

        # Add bottom padding
        for _ in range(padding_bottom):
            lines.append(
                f"{border_style}{display_config.BORDER_VERTICAL}{reset}"
                + " " * (box_width - 2)
                + f"{border_style}{display_config.BORDER_VERTICAL}{reset}"
            )

        # Bottom border (always without text)
        bottom_border = (
            display_config.BORDER_BOTTOM_LEFT
            + display_config.BORDER_HORIZONTAL * (box_width - 2)
            + display_config.BORDER_BOTTOM_RIGHT
        )
        lines.append(f"{border_style}{bottom_border}{reset}")

        # Build sidebar if enabled
        if display_config.SIDEBAR_ENABLED and self.all_phases:
            sidebar_lines = self._build_sidebar()

            # Combine main display with sidebar
            combined_lines = []
            max_lines = max(len(lines), len(sidebar_lines))

            for i in range(max_lines):
                main_line = lines[i] if i < len(lines) else " " * box_width
                sidebar_line = sidebar_lines[i] if i < len(sidebar_lines) else ""

                if display_config.SIDEBAR_POSITION == "right":
                    combined_line = (
                        main_line + " " * display_config.SIDEBAR_PADDING + sidebar_line
                    )
                else:  # left
                    combined_line = (
                        sidebar_line + " " * display_config.SIDEBAR_PADDING + main_line
                    )

                combined_lines.append(combined_line)

            output = "\n".join(combined_lines)
        else:
            output = "\n".join(lines)

        # Only update if content changed
        if output != self._last_output:
            # Move cursor to home and redraw everything
            sys.stdout.write(display_config.HOME_CURSOR)
            sys.stdout.write(output)
            # Clear any remaining lines from previous render
            sys.stdout.write(display_config.CLEAR_TO_END)
            sys.stdout.flush()
            self._last_output = output

    def _show_plain_countdown(self, seconds: int, phase: Optional[Phase]):
        """Show countdown in plain mode."""
        minutes = seconds // 60
        secs = seconds % 60

        if phase:
            instruction = phase.instruction
        else:
            instruction = "Breathwork Exercise"

        # Use carriage return to update same line
        output = f"\r{instruction}: {minutes:02d}:{secs:02d}    "
        sys.stdout.write(output)
        sys.stdout.flush()

    def show_instruction(self, instruction: str, color: str = "cyan"):
        """Display an instruction message.

        Args:
            instruction: Instruction text to display
            color: Color for the text
        """
        if self.mode == DisplayMode.TUI:
            self._show_tui_instruction(instruction, color)
        else:
            self._show_plain_instruction(instruction)

    def _show_tui_instruction(self, instruction: str, color: str):
        """Show instruction in TUI mode."""
        text = Text(instruction, style=f"bold {color}")
        panel = Panel(
            Align.center(text, vertical="middle"), border_style=color, height=5
        )
        self.console.print(panel)

    def _show_plain_instruction(self, instruction: str):
        """Show instruction in plain mode."""
        print(f"\n{instruction}")

    def show_phase_transition(self, from_phase: Optional[Phase], to_phase: Phase):
        """Display phase transition message.

        Args:
            from_phase: Previous phase (None if starting)
            to_phase: New phase
        """
        # In TUI mode, don't show transition messages as they disrupt the display
        if self.mode == DisplayMode.TUI:
            return

        if from_phase:
            message = (
                f"Transitioning from {from_phase.type.value} to {to_phase.type.value}"
            )
        else:
            message = f"Starting {to_phase.type.value} phase"

        self.show_instruction(message, to_phase.color)

    def show_completion(self):
        """Display exercise completion message."""
        message = exercise_defaults.COMPLETION_MESSAGE

        if self.mode == DisplayMode.TUI:
            # Clear the display first
            if self._display_initialized:
                sys.stdout.write(
                    display_config.CLEAR_SCREEN + display_config.HOME_CURSOR
                )
                sys.stdout.flush()

            text = Text(message, style="bold green")
            panel = Panel(
                Align.center(text, vertical="middle"),
                title=exercise_defaults.COMPLETION_TITLE,
                border_style="green",
                height=5,
            )
            self.console.print(panel)
        else:
            print(f"\n{message}")

    def show_error(self, error: str):
        """Display an error message.

        Args:
            error: Error message to display
        """
        if self.mode == DisplayMode.TUI:
            self.console.print(
                f"[bold red]{exercise_defaults.ERROR_PREFIX}[/bold red] {error}"
            )
        else:
            print(f"{exercise_defaults.ERROR_PREFIX} {error}", file=sys.stderr)

    def beep(self, sound_type: str = "countdown"):
        """Play audio beep using system sounds.

        Args:
            sound_type: Type of sound to play - "countdown" for tick sounds, "transition" for phase changes
        """
        import subprocess
        import platform

        try:
            system = platform.system()

            if system == "Darwin":  # macOS
                # Choose sound based on type
                if sound_type == "countdown":
                    sound_file = (
                        "/System/Library/Sounds/Ping.aiff"  # Short tick for countdown
                    )
                else:  # transition
                    sound_file = "/System/Library/Sounds/Glass.aiff"  # Distinct sound for phase change

                subprocess.Popen(
                    ["afplay", sound_file],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            elif system == "Linux":
                # Try paplay (PulseAudio) or aplay (ALSA)
                try:
                    subprocess.Popen(
                        ["paplay", "/usr/share/sounds/freedesktop/stereo/message.oga"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                except FileNotFoundError:
                    # Fallback to terminal bell
                    sys.stdout.write("\a")
                    sys.stdout.flush()
            elif system == "Windows":
                import winsound

                # Different frequencies for different sound types
                freq = 800 if sound_type == "countdown" else 1200
                winsound.Beep(freq, timing_config.BEEP_DURATION)  # type: ignore[attr-defined]
            else:
                # Fallback to terminal bell
                sys.stdout.write("\a")
                sys.stdout.flush()
        except Exception:
            # Final fallback to terminal bell
            sys.stdout.write("\a")
            sys.stdout.flush()
