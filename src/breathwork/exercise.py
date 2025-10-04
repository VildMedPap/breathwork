"""Exercise orchestration for breathing exercises."""

from typing import List, Optional
from breathwork.models import ExerciseConfig, Phase, PhaseType
from breathwork.timer import Timer
from breathwork.configuration import exercise_defaults, display_config


class Exercise:
    """Orchestrates a complete breathing exercise."""

    def __init__(self, config: Optional[ExerciseConfig] = None):
        """Initialize exercise with configuration.

        Args:
            config: Exercise configuration, uses defaults if None
        """
        self.config = config or ExerciseConfig()
        self.phases: List[Phase] = []
        self.current_phase_index: Optional[int] = None
        self.timer: Optional[Timer] = None
        self._started = False
        self._completed = False

    def _generate_phases(self):
        """Generate phases from configuration."""
        phases = []

        # Preparation phase (breathing) - only if preparation_duration > 0
        if self.config.preparation_duration > 0:
            prep_phase = Phase(
                type=PhaseType.BREATHING,
                duration=self.config.preparation_duration,
                instruction=exercise_defaults.PREPARATION_INSTRUCTION,
                color="blue",
            )
            phases.append(prep_phase)

        # Alternate between breathing and hold phases
        # Pattern: breathe -> hold -> breathe -> hold -> ... -> hold
        for i, breathing_duration in enumerate(self.config.step_durations):
            # Breathing phase (decreasing durations from steps)
            breathing_phase = Phase(
                type=PhaseType.BREATHING,
                duration=breathing_duration,
                instruction=exercise_defaults.BREATHING_INSTRUCTION.format(
                    duration=breathing_duration
                ),
                color=display_config.PHASE_COLORS["breathing"],
            )
            phases.append(breathing_phase)

            # Hold phase (same duration each time)
            hold_phase = Phase(
                type=PhaseType.HOLD,
                duration=self.config.hold_duration,
                instruction=exercise_defaults.HOLD_INSTRUCTION,
                color=display_config.PHASE_COLORS["hold"],
            )
            phases.append(hold_phase)

        # Add a final "Complete" phase to mark the end
        complete_phase = Phase(
            type=PhaseType.BREATHING,
            duration=1,  # Short 1-second phase just to show completion
            instruction="Complete",
            color="blue",
        )
        phases.append(complete_phase)

        self.phases = phases

    def start(self):
        """Start the exercise."""
        if self._started and not self._completed:
            raise RuntimeError("Exercise already started")
        if self._completed:
            raise RuntimeError(
                "Exercise already completed. Call reset() to start again"
            )

        self._generate_phases()
        self._started = True
        self._completed = False
        self.current_phase_index = 0

        # Start the first phase
        current_phase = self.phases[0]
        current_phase.start()

        # Create timer for first phase
        self.timer = Timer(
            duration=current_phase.duration,
            countdown_threshold=self.config.countdown_beep_threshold,
        )
        self.timer.start()

    def advance_phase(self) -> bool:
        """Advance to the next phase.

        Returns:
            True if advanced to next phase, False if exercise is complete
        """
        if not self._started:
            raise RuntimeError("Exercise not started")

        if self._completed:
            return False

        # Check if current phase timer is complete
        if self.timer and not self.timer.is_expired():
            raise RuntimeError("Current phase not complete")

        # Complete current phase
        if self.current_phase_index is not None:
            self.phases[self.current_phase_index].complete()

        # Move to next phase
        if (
            self.current_phase_index is not None
            and self.current_phase_index < len(self.phases) - 1
        ):
            self.current_phase_index += 1
            next_phase = self.phases[self.current_phase_index]
            next_phase.start()

            # Create new timer for next phase
            self.timer = Timer(
                duration=next_phase.duration,
                countdown_threshold=self.config.countdown_beep_threshold,
            )
            self.timer.start()
            return True
        else:
            # Exercise complete
            self._completed = True
            self.current_phase_index = None
            return False

    def get_current_phase(self) -> Optional[Phase]:
        """Get the current active phase.

        Returns:
            Current phase or None if not started/completed
        """
        if not self._started or self._completed:
            return None

        if self.current_phase_index is not None:
            return self.phases[self.current_phase_index]

        return None

    def is_complete(self) -> bool:
        """Check if exercise is complete.

        Returns:
            True if all phases are complete
        """
        return self._completed

    def reset(self):
        """Reset the exercise to initial state."""
        self.phases = []
        self.current_phase_index = None
        self.timer = None
        self._started = False
        self._completed = False

    def get_phases(self) -> List[Phase]:
        """Get all phases in the exercise.

        Returns:
            List of phases
        """
        return self.phases

    def __str__(self) -> str:
        """String representation of exercise."""
        if not self._started:
            return "Exercise(not started)"
        elif self._completed:
            return "Exercise(completed)"
        else:
            return f"Exercise(phase {self.current_phase_index + 1}/{len(self.phases)})"
