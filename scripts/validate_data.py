"""Pilot verisini kontrol et ve isteğe bağlı yakın tekrar ara."""
import argparse
from deasciification.validation import validate_data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data")
    parser.add_argument("--check", help="Pilot ile karşılaştırılacak aday cümle")
    args = parser.parse_args()
    validate_data(args.data, args.check)


if __name__ == "__main__":
    main()
