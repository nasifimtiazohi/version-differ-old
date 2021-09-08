"""Console script for version_differ."""
import argparse
import sys
from version_differ import get_stats


ecosystems = ["Cargo", "Composer", "Go", "Maven", "npm", "NuGet", "pip", "RubyGems"]


def main():
    """Console script for version_differ."""
    parser = argparse.ArgumentParser()

    parser.add_argument("ecosystem", choices=ecosystems, help="package registry")
    parser.add_argument("package", type=str, help="package name")
    parser.add_argument("old", type=str, help="old version")
    parser.add_argument("new", type=str, help="new version")

    args = parser.parse_args()

    get_stats(args.ecosystem, args.package, args.old, args.new)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
