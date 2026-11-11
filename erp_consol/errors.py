"""Exception types and exit codes shared by the command line interface."""

EXIT_OK = 0
EXIT_USAGE = 2  # bad input, bad options, unreadable files
EXIT_GATE = 3  # a requested pass or fail gate was not met


class InputError(Exception):
    """The user supplied something the tool cannot work with.

    The message is written for a person: it names the file, the problem and,
    where possible, what to do about it.
    """
