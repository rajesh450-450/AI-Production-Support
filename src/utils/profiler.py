import os
import sys
from datetime import datetime

# ------------------------------------------------------------------
# Globals
# ------------------------------------------------------------------

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
    )
)

_depth = 0
_enabled = False
_trace_file = None


# ------------------------------------------------------------------
# Internal profiler callback
# ------------------------------------------------------------------

def _profiler(frame, event, arg):

    global _depth
    global _trace_file

    if event not in ("call", "return"):
        return _profiler

    filename = os.path.abspath(frame.f_code.co_filename)

    # Ignore everything outside src/
    if not filename.startswith(PROJECT_ROOT):
        return _profiler

    relative_path = os.path.relpath(
        filename,
        PROJECT_ROOT,
    )

    function_name = frame.f_code.co_name

    indent = "│   " * _depth

    if event == "call":

        _trace_file.write(
            f"{indent}>>> {relative_path} :: {function_name}\n"
        )

        _trace_file.flush()

        _depth += 1

    elif event == "return":

        _depth -= 1

        indent = "│   " * _depth

        # _trace_file.write(
        #     f"{indent}<<< {relative_path} :: {function_name}\n"
        # )

        # _trace_file.flush()

    return _profiler


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def start_profiler(log_file: str | None = None):
    """
    Start execution profiling.

    If log_file is not provided, a timestamped log file is created
    under the project's logs directory.
    """

    global _enabled
    global _depth
    global _trace_file

    if _enabled:
        return

    if log_file is None:

        logs_dir = os.path.abspath(
            os.path.join(
                PROJECT_ROOT,
                "..",
                "logs",
            )
        )

        os.makedirs(
            logs_dir,
            exist_ok=True,
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        log_file = os.path.join(
            logs_dir,
            # f"execution_trace_{timestamp}.log",
            f"execution_trace.log",
        )

    else:

        os.makedirs(
            os.path.dirname(log_file),
            exist_ok=True,
        )

    _trace_file = open(
        log_file,
        "w",
        encoding="utf-8",
    )

    _enabled = True
    _depth = 0

    _trace_file.write("=" * 80 + "\n")
    _trace_file.write("Execution Trace Started\n")
    _trace_file.write("=" * 80 + "\n\n")

    sys.setprofile(_profiler)


def stop_profiler():
    """
    Stop execution profiling.
    """

    global _enabled
    global _trace_file

    if not _enabled:
        return

    sys.setprofile(None)

    _trace_file.write("\n")
    _trace_file.write("=" * 80 + "\n")
    _trace_file.write("Execution Trace Finished\n")
    _trace_file.write("=" * 80 + "\n")

    _trace_file.close()

    _trace_file = None
    _enabled = False