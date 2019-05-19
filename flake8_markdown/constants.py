import subprocess
import sys


if sys.version_info.major == 3 and sys.version_info.minor >= 7:
    SUBPROCESS_ARGS = dict(
        capture_output=True,
        text=True,
    )
else:
    SUBPROCESS_ARGS = dict(
        encoding='ascii',
        universal_newlines=True,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
