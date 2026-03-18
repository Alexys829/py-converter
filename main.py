import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("convert", "formats", "batch"):
        from pyconverter.cli.commands import run_cli
        run_cli()
    else:
        from pyconverter.gui.app import run_gui
        run_gui()


if __name__ == "__main__":
    main()
