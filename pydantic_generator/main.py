import argparse

from .cli import CLI


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_", "--input", required=True)
    parser.add_argument("-o", "--output")

    args, _ = parser.parse_known_args()
    exit(CLI().run(**vars(args)).value)


if __name__ == "__main__":
    main()
