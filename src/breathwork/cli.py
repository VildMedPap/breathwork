import typer
from typing_extensions import Annotated
from breathwork import __version__
from breathwork.models import ExerciseConfig
from breathwork.core import run_exercise, validate_config


def main(
    hold: Annotated[
        int,
        typer.Option(
            "--hold",
            "-h",
            help="Hold breath duration in seconds (1-300)",
            min=1,
            max=300,
        ),
    ] = 60,
    steps: Annotated[
        str,
        typer.Option(
            "--steps",
            "-s",
            help="Breath steps in seconds, comma-separated (e.g., '30,20,10')",
        ),
    ] = "30,20,10",
    countdown: Annotated[
        int,
        typer.Option(
            "--countdown",
            "-c",
            help="When to start countdown beeps in seconds before phase ends",
            min=0,
        ),
    ] = 5,
    preparation: Annotated[
        int,
        typer.Option(
            "--preparation",
            "-p",
            help="Preparation phase duration in seconds (0 to skip)",
            min=0,
        ),
    ] = 0,
    tui: Annotated[
        bool,
        typer.Option(
            "--tui/--plain",
            help="Use TUI mode with colors and ASCII art, or plain text mode",
        ),
    ] = True,
    audio: Annotated[
        str,
        typer.Option(
            "--audio",
            "-a",
            help="Audio cues: 'beep' for terminal bell, 'off' for silent",
        ),
    ] = "beep",
    version: Annotated[
        bool, typer.Option("--version", help="Show version and exit")
    ] = False,
):
    """Breathwork CLI - Guided breathing exercise with timed breath holds."""
    if version:
        typer.echo(f"breathwork version {__version__}")
        raise typer.Exit(0)

    # Validate audio option (must be exact match, case-sensitive)
    if audio not in ["beep", "off"]:
        typer.echo(
            f"Error: Invalid audio option '{audio}'. Must be exactly 'beep' or 'off' (lowercase).",
            err=True,
        )
        raise typer.Exit(1)
    audio_lower = audio

    try:
        # Create configuration from CLI arguments
        config = ExerciseConfig.from_cli_args(
            hold=hold,
            steps=steps,
            countdown=countdown,
            preparation=preparation,
            tui=tui,
            audio=audio_lower,
        )

        # Validate configuration
        is_valid, error_msg = validate_config(config)
        if not is_valid:
            typer.echo(f"Error: {error_msg}", err=True)
            raise typer.Exit(1)

        # Run the exercise
        success = run_exercise(config)

        # Exit with appropriate code
        if not success:
            raise typer.Exit(130)  # Standard exit code for SIGINT (Ctrl-C)
        # If successful, just return normally (exit code 0)

    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    except KeyboardInterrupt:
        # Handle Ctrl-C gracefully
        typer.echo("\nExercise interrupted.", err=True)
        raise typer.Exit(130)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        raise typer.Exit(1)


app = typer.Typer()
app.command()(main)

if __name__ == "__main__":
    app()
