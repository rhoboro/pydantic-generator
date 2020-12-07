from .cli import CLI


def main():
    exit(CLI().run().value)


if __name__ == "__main__":
    main()
