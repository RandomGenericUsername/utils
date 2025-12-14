import re

from .log_types import (
    LogLevelOptions,
    LogLevels,
    VerbosityToLogLevel,
)


def get_log_level_map(
    options_class: type[LogLevelOptions] = LogLevelOptions,
) -> dict[str, LogLevels]:
    """
    Dynamically create a log level mapping from options class.

    Args:
        options_class: Class containing log level options

    Returns:
        Dictionary mapping all variants to LogLevels enum values
    """
    level_map = {}
    full_name_pattern = re.compile(
        r"^[a-zA-Z]+$"
    )  # Full names like 'debug', 'info'
    abbrev_pattern = re.compile(r"^[a-zA-Z]$")  # Single letter abbreviations

    # Get all class attributes that are lists (our log level options)
    for attr_name in dir(options_class):
        if not attr_name.startswith("_"):
            attr_value = getattr(options_class, attr_name)
            if isinstance(attr_value, list) and attr_value:
                # First element should be the full log level name
                base_level = attr_value[0]

                # Validate base level format
                if not full_name_pattern.match(base_level):
                    raise ValueError(f"Invalid log level format: {base_level}")

                # Get the corresponding LogLevels enum value
                try:
                    log_level_enum = getattr(LogLevels, base_level.upper())
                except AttributeError:
                    raise ValueError(
                        f"Unknown log level: {base_level}"
                    ) from AttributeError

                # Process all variants in the list
                for i, variant in enumerate(attr_value):
                    # Validate format based on position
                    if i == 0:  # Full name
                        if not full_name_pattern.match(variant):
                            raise ValueError(
                                f"Invalid full name format: {variant}"
                            )
                    else:  # Abbreviations
                        if not abbrev_pattern.match(variant):
                            raise ValueError(
                                f"Invalid abbreviation format: {variant}"
                            )

                    # Add to map (case-insensitive)
                    level_map[variant.lower()] = log_level_enum

    return level_map


def validate_log_level_string(
    value: str, options_class: type[LogLevelOptions] = LogLevelOptions
) -> LogLevels:
    """
    Validate and convert a string log level to LogLevels enum.

    Args:
        value: String representation of log level
        options_class: Class containing log level options

    Returns:
        LogLevels enum value

    Raises:
        ValueError: If the log level string is invalid
    """
    level_map = get_log_level_map(options_class)
    normalized_value = value.lower()

    if normalized_value in level_map:
        return level_map[normalized_value]

    # Create a user-friendly list of valid options
    valid_options = []
    for attr_name in ["debug", "info", "warning", "error", "critical"]:
        if hasattr(options_class, attr_name):
            options = getattr(options_class, attr_name)
            valid_options.extend(options)

    valid_options_str = ", ".join(valid_options)
    raise ValueError(
        f"Invalid log level '{value}'. Valid options are: {valid_options_str}"
    )


def get_log_level_from_verbosity(verbosity: int) -> LogLevels:
    """
    Convert verbosity count to LogLevels enum.

    Args:
        verbosity: Verbosity count (1-3)

    Returns:
        LogLevels enum value corresponding to verbosity level

    Raises:
        ValueError: If verbosity is negative or exceeds maximum
    """
    if verbosity < 0:
        raise ValueError(f"Verbosity cannot be negative, got: {verbosity}")

    max_verbosity = max(VerbosityToLogLevel.mapping.keys())
    if verbosity > max_verbosity:
        raise ValueError(
            f"Verbosity level {verbosity} exceeds maximum {max_verbosity}. "
            f"Using maximum level {max_verbosity}."
        )

    return VerbosityToLogLevel.mapping.get(verbosity, LogLevels.CRITICAL)


def parse_log_level(
    log_level_str: str | None, verbosity: int, fallback: LogLevels
) -> LogLevels:
    if verbosity > 0:
        return get_log_level_from_verbosity(verbosity)
    if log_level_str:
        return validate_log_level_string(log_level_str)
    return fallback
