"""Core logic for running breathing exercises."""

import time
from typing import Optional
from breathwork.models import ExerciseConfig, DisplayMode
from breathwork.exercise import Exercise
from breathwork.display import Display
from breathwork.configuration import timing_config, exercise_defaults


def run_exercise(config: ExerciseConfig) -> bool:
    """Run a complete breathing exercise.

    Args:
        config: Exercise configuration

    Returns:
        True if exercise completed successfully, False if interrupted
    """
    # Initialize components
    exercise = Exercise(config)

    # Start the exercise to generate phases
    exercise.start()

    # Initialize display with all phases for progress tracking
    display = Display(config.display_mode, phases=exercise.phases)

    try:
        # Start live display for TUI mode (this also clears the screen)
        display.start_live_display()

        # Main exercise loop
        last_second = -1
        countdown_beeps_played = set()  # Track which seconds we've beeped for

        while not exercise.is_complete():
            phase = exercise.get_current_phase()
            timer = exercise.timer

            if not phase or not timer:
                break

            # Check for countdown transition
            if timer.in_countdown() and phase.is_in_progress():
                phase.enter_countdown()

            # Update display only when second changes
            remaining = int(timer.remaining_time())
            if remaining != last_second:
                display.show_countdown(remaining, phase, exercise.current_phase_index)

                # Play countdown beeps based on countdown_beep_threshold
                if (
                    config.audio_enabled
                    and 1 <= remaining <= config.countdown_beep_threshold
                    and remaining not in countdown_beeps_played
                ):
                    display.beep("countdown")
                    countdown_beeps_played.add(remaining)

                # Play transition sound at 0 (except for Complete phase)
                is_complete_phase = phase.instruction == "Complete"
                if (
                    config.audio_enabled
                    and remaining == 0
                    and 0 not in countdown_beeps_played
                    and not is_complete_phase
                ):
                    display.beep("transition")
                    countdown_beeps_played.add(0)

                last_second = remaining

            # Check if phase is complete
            if timer.is_expired():
                # Advance to next phase (transition sound already played at 0)
                if not exercise.advance_phase():
                    break

                # Reset for new phase
                last_second = -1
                countdown_beeps_played.clear()  # Reset countdown beeps for new phase

                # Show transition if there's a next phase (only in plain mode)
                next_phase = exercise.get_current_phase()
                if next_phase:
                    display.show_phase_transition(phase, next_phase)
                    # Only pause in plain mode
                    if config.display_mode == DisplayMode.PLAIN:
                        time.sleep(timing_config.TRANSITION_PAUSE)

            # Small sleep to prevent CPU spinning
            time.sleep(timing_config.LOOP_SLEEP_INTERVAL)

        # Advance to the final "Complete" phase
        if not exercise.is_complete():
            exercise.advance_phase()
            final_phase = exercise.get_current_phase()
            if final_phase:
                final_phase.start()
                # Show the complete phase briefly
                display.show_countdown(0, final_phase, exercise.current_phase_index)
                time.sleep(1)

        # Stop live display
        display.stop_live_display()

        # Wait for user confirmation before closing
        try:
            input("\nPress Enter to exit...")
        except (KeyboardInterrupt, EOFError):
            pass

        return True

    except KeyboardInterrupt:
        # Handle Ctrl-C gracefully
        display.stop_live_display()
        display.show_instruction(exercise_defaults.INTERRUPTION_MESSAGE, "yellow")
        return False

    except Exception as e:
        # Handle other errors
        display.stop_live_display()
        display.show_error(str(e))
        return False


def validate_config(config: ExerciseConfig) -> tuple[bool, Optional[str]]:
    """Validate exercise configuration.

    Args:
        config: Configuration to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        config.validate()
        return True, None
    except ValueError as e:
        return False, str(e)
