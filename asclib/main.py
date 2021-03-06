"""The main subprogram for our style checker."""
import os
import sys

from asclib.cmdline import parse_cmdline
from asclib.checkers import FileCheckerError
from asclib.checkers.typific.factory import get_file_checker
from asclib.config import Config
import asclib.logging
from asclib.logging import log_error


def style_checker(argv=None):
    """Run the style checker with the given command-line arguments.

    :param argv: Same as in parse_cmdline.
    :type argv: list[str] | None
    """
    args = parse_cmdline(argv)
    asclib.logging.logging_level = args.verbose_level

    if not args.filenames:
        # No filename provided, which means the user wants us to
        # read the list of filesnames from standard input.
        args.filenames = [
            filename for filename in sys.stdin.read().splitlines() if filename
        ]

    config = Config(
        args.system_config, args.module_name, args.module_config, args.forced_year
    )

    n_files_with_errors = 0
    for filename in args.filenames:
        try:
            # Before even trying to launch the style checker, first verify
            # that the file exists, and if it doesn't then report the error,
            # and look at the next file to check...
            if not os.path.isfile(filename):
                raise FileCheckerError(
                    "Error: `%s' is not a valid filename." % filename
                )

            checker = get_file_checker(filename, config)
            if checker is None:
                # No checks for this kind of file.
                continue
            checker.check_file()
        except FileCheckerError as e:
            n_files_with_errors += 1
            if n_files_with_errors > args.max_files_with_errors:
                log_error("[other files with style violations were found]")
                break
            else:
                log_error(e.args)

    return n_files_with_errors == 0
