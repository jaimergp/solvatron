if __name__ == "__main__":
    import sys
    from .cli import cli, main

    sys.exit(main(cli()))
