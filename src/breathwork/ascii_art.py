"""ASCII art definitions for displaying large numbers."""

# ASCII art digits (5 lines tall)
ASCII_DIGITS = {
    "0": [" ███ ", "█   █", "█   █", "█   █", " ███ "],
    "1": ["  █  ", " ██  ", "  █  ", "  █  ", " ███ "],
    "2": [" ███ ", "█   █", "   █ ", "  █  ", "█████"],
    "3": [" ███ ", "█   █", "  ██ ", "█   █", " ███ "],
    "4": ["█   █", "█   █", "█████", "    █", "    █"],
    "5": ["█████", "█    ", "████ ", "    █", "████ "],
    "6": [" ███ ", "█    ", "████ ", "█   █", " ███ "],
    "7": ["█████", "    █", "   █ ", "  █  ", " █   "],
    "8": [" ███ ", "█   █", " ███ ", "█   █", " ███ "],
    "9": [" ███ ", "█   █", " ████", "    █", " ███ "],
    ":": ["     ", "  █  ", "     ", "  █  ", "     "],
    " ": ["     ", "     ", "     ", "     ", "     "],
}


def get_ascii_time(minutes: int, seconds: int) -> list:
    """Convert time to ASCII art representation.

    Args:
        minutes: Minutes to display
        seconds: Seconds to display

    Returns:
        List of strings representing the time in ASCII art
    """
    # Format time as MM:SS
    time_str = f"{minutes:02d}:{seconds:02d}"

    # Build ASCII art lines
    lines = ["", "", "", "", ""]
    for char in time_str:
        if char in ASCII_DIGITS:
            for i, line in enumerate(ASCII_DIGITS[char]):
                lines[i] += line + " "

    return lines


def get_ascii_number(number: int) -> list:
    """Convert a number to ASCII art representation.

    Args:
        number: Number to display (0-999)

    Returns:
        List of strings representing the number in ASCII art
    """
    # Convert to string and pad if necessary
    num_str = str(min(999, max(0, number)))

    # Build ASCII art lines
    lines = ["", "", "", "", ""]
    for char in num_str:
        if char in ASCII_DIGITS:
            for i, line in enumerate(ASCII_DIGITS[char]):
                lines[i] += line + " "

    return lines
