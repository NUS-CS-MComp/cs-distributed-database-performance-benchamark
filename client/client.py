import argparse


def parse():
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "--load", help="path to the data to be loaded into the db"
    )
    parser.add_argument(
        "--run", help="path to the transaction file to be executed"
    )
    parser.add_argument("--purge", help="purge the database contents")

    args = parser.parse_args()
    return args


def main():
    args = parse()
    if args.load:
        load_data(args.load)
    elif args.purge:
        purge()
    elif args.run:
        run()
    print("Success!")


def load_data(path):
    pass


def purge():
    pass


def run():
    pass


main()
