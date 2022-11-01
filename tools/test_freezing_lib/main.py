"""Test freezing-library."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from qdarktheme.util import get_logger
from tools.util import get_project_root_path

IGNORE_MESSAGES = (
    "Unable to create basic Accelerated OpenGL renderer.",
    "Core Image is now using the software OpenGL renderer. This will be slow.",
)
logger = get_logger(__name__)


class SvgFileNotFoundError(FileNotFoundError):
    """Error raise if cannot open svg file."""


def _test_pyinstaller() -> str:
    demo_app_src_path = Path(__file__).absolute().parent / "demo_app.py"
    app_name = "app"
    output_path = get_project_root_path() / "dist" / "PyInstaller"

    if output_path.exists():
        logger.info("Removing %s ...", output_path)
        shutil.rmtree(output_path)
    logger.info("Creating %s ...", output_path)
    output_path.mkdir(parents=True)

    command = [
        "pyinstaller",
        "--clean",
        "-y",
        str(demo_app_src_path),
        "-n",
        app_name,
        "--distpath",
        str(output_path),
        "--onefile",
    ]
    logger.info("Running: %s ...", command)
    subprocess.run(command)

    app_path = output_path / app_name
    logger.info("Opening %s ...", app_path)
    try:
        result = subprocess.check_output([str(app_path)], stderr=subprocess.STDOUT)
    except FileNotFoundError:
        # In GitHub action, There is time when the program sleeps in favor of other processes.
        # The PyInstaller sub-process has a timeout 60 seconds, which often results in a timeout error.
        # If the app cannot be created successfully due to a timeout, it will try to create app again.
        logger.info("Re running: %s ...", command)
        subprocess.run(command)
        logger.info("Opening %s ...", app_path)
        result = subprocess.check_output([str(app_path)], stderr=subprocess.STDOUT)
    return result.decode("utf-8")


def _check_output(output: str) -> None:
    if output == "":
        logger.info("There is no output from demo app")
        return

    if "qt.svg: Cannot open file" in output:
        raise SvgFileNotFoundError(
            "QtSvg module cannot open svg files, because: No such file or directory"
        )
    for message in IGNORE_MESSAGES:
        if message in output:
            logger.info("Ignore: %s", message)
            output = output.replace(message, "")
            continue
        logger.info("Demo app error: %s", message)
    if output.replace("\n", "") == "":
        return
    raise RuntimeError("There is unexpected output")


def main() -> None:
    """The main method of this package."""
    logger.info("PyInstaller test session start")
    output_message = _test_pyinstaller()
    logger.info("Build finished successfully!")
    _check_output(output_message)
