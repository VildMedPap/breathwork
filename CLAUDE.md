# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Breathwork is a Python CLI/TUI application for guided breathing exercises with timed breath-holds. The application uses Typer for CLI, Rich for terminal UI, and implements a state machine pattern for exercise orchestration.

## Installation & Development

**Package manager**: Uses `uv` for dependency management

**Install for development**:
```bash
uv pip install -e .
```

**Run the application**:
```bash
# Using uvx (recommended)
uvx breathwork

# Or after installation
breathwork
```

**Run with custom options**:
```bash
breathwork --hold 90 --steps "45,30,15" --preparation 30
```

**Code quality checks**:
```bash
uvx ruff format && uvx ruff check && uvx ty check
```

**IMPORTANT**: After every code change, run the code quality checks above. All three commands must pass before the work is considered complete.

## Architecture

### Core Components

1. **Exercise Flow**: `Exercise` class (`exercise.py`) orchestrates phase progression
   - Generates phases from config (preparation → breathing → hold cycles)
   - Manages phase transitions using state machine pattern
   - Each phase has state: NOT_STARTED → IN_PROGRESS → COUNTDOWN → COMPLETED

2. **Timer System**: `Timer` class (`timer.py`) provides drift-free timing
   - Uses `time.monotonic()` for accuracy
   - Supports countdown threshold for final seconds alert
   - Independent of phase logic

3. **Display Layer**: `Display` class (`display.py`) handles rendering
   - Two modes: TUI (Rich-based with ASCII art) and PLAIN (simple text)
   - Uses Rich's Live display for TUI mode to avoid flicker
   - ASCII art digits defined in `ascii_art.py`

4. **Data Models**: (`models.py`)
   - `Phase`: Represents single breathing/hold phase with state management
   - `ExerciseConfig`: Configuration with validation
   - Enums: `PhaseType`, `PhaseState`, `DisplayMode`

5. **Execution**: `run_exercise()` in `core.py`
   - Main loop checks timer, updates display, handles audio cues
   - Updates only on second changes to minimize CPU
   - Graceful Ctrl-C handling

### Key Design Patterns

- **State Machine**: Phases transition through explicit states with validation
- **Separation of Concerns**: Timer, Exercise, Display are independent
- **Configuration Validation**: Config validated at construction time
- **Monotonic Timing**: Prevents drift from system clock adjustments

### File Structure
```
src/breathwork/
  cli.py           # Typer CLI entry point
  core.py          # Main exercise execution loop
  exercise.py      # Exercise orchestration and phase management
  models.py        # Data models (Phase, ExerciseConfig, enums)
  timer.py         # Drift-free timer using monotonic time
  display.py       # TUI/plain rendering
  ascii_art.py     # ASCII digit definitions for countdown
  configuration.py # Default settings and constants
```

## Important Implementation Details

**Phase Generation**: Exercise creates phases dynamically from config - preparation (optional) → N cycles of (breathe → hold) → complete marker

**Audio Cues**: Terminal bell (`\a`) for countdown beeps (1-5 seconds) and double beep for transitions

**State Validation**: Phase state transitions enforce strict rules (e.g., can't complete a NOT_STARTED phase)

**Display Updates**: Only updates on second changes to prevent flicker and reduce CPU usage
