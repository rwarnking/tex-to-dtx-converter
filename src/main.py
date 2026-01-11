import os
import argparse
import sys
from pathlib import Path

# https://stackoverflow.com/questions/404744/
if getattr(sys, "frozen", False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app path
    APP_PATH = Path(os.path.dirname(sys.executable))
else:
    APP_PATH = Path(os.path.dirname(os.path.abspath(__file__)))


def main():
    parser = argparse.ArgumentParser(
        description="Example program with CLI and GUI modes"
    )

    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the graphical user interface"
    )

    # TODO there is no check in place whether the given or default path exist
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path(os.path.normpath(APP_PATH / ".." / "test-data" / "source")),
        help="Source directory path"
    )

    parser.add_argument(
        "--target-dir",
        type=Path,
        default=Path(os.path.normpath(APP_PATH / ".." / "test-data" / "target")),
        help="Target directory path"
    )

    args = parser.parse_args()

    if args.gui:
        from gui.main_window import GuiApp
        main_app = GuiApp(args.source_dir, args.target_dir)
    else:
        from cli import CliApp
        main_app = CliApp(args.source_dir, args.target_dir)
        main_app.run()

if __name__ == "__main__":
    main()