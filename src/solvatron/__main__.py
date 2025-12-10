if __name__ == "__main__":
    import sys
    from .cli import ArgumentError, cli, main

    try:
        sys.exit(main(cli()))
    except ArgumentError as exc:
        sys.exit(f"ArgumentError: {exc}")
