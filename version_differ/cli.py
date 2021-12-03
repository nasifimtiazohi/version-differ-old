"""Console script for version_differ."""
import argparse
import sys
from version_differ import get_version_diff_stats, ecosystems


def main():
    """Console script for version_differ."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--ecosystem", choices=ecosystems, help="package registry", required=True
    )
    parser.add_argument("--package", type=str, help="package name", required=True)
    parser.add_argument("--old_version", type=str, help="old version", required=True)
    parser.add_argument("--new_version", type=str, help="new version", required=True)
    parser.add_argument(
        "--repository_url",
        type=str,
        help="provide repository url if the ecosystem is NuGet or Go",
    )

    args = parser.parse_args()
    print(args)

    print(
        get_version_diff_stats(
            args.ecosystem,
            args.package,
            args.old_version,
            args.new_version,
            args.repository_url,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
