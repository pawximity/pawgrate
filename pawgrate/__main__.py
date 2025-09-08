"""
pawgrate - a lightweight CLI wrapper for ogr2ogr.

This tool reads configuration from YAML files or CLI flags and generates 
ogr2ogr commands to import data into PostgreSQL/PostGIS. 

Usage:
    pawgrate import file --config config.yaml
    pawgrate import manual --src mydata.shp --dbname pawx --table roads
"""
import argparse

from pawgrate.config import PawgrateError
from pawgrate.core import process_file
from pawgrate.core import process_manual


def puppy():
    return r"""
    / \__
(    @\___
/         O
/   (_____/
/_____/ U
"""


def main():
    print(puppy())
    parser = arg_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except PawgrateError as e:
        print("[!]", e)
        return 1


def arg_parser():
    parser = argparse.ArgumentParser(
        description="pawgrate: friendly ogr2ogr wrapper for PostGIS")
    commands_subparser = parser.add_subparsers(title="commands",
                                               dest="command",
                                               required=True)
    # import parent
    import_parser = commands_subparser.add_parser(
        "import", help="import a file into PostGIS")
    import_subparser = import_parser.add_subparsers(dest="mode", required=True)
    file_parser(import_subparser)
    manual_parser(import_subparser)
    return parser


def file_parser(import_subparser):
    # import flags using a yaml config file
    file_parser = import_subparser.add_parser(
        "file", help="import using a yaml config")
    file_parser.add_argument("--config",
                             required=True,
                             help="use a yaml config file")
    file_parser.set_defaults(func=process_file)


def manual_parser(import_subparser):
    # import flags individually through the cli
    manual_parser = import_subparser.add_parser("manual",
                                                help="import using flags")
    manual_parser.add_argument(
        "--src",
        required=True,
        help="path to the import file (e.g. .geojson, .shp)")
    manual_parser.add_argument("--host",
                               help="postgres host (default: localhost)")
    manual_parser.add_argument("--port", help="postgres port (default: 5432)")
    manual_parser.add_argument("--user", required=True, help="postgres user")
    manual_parser.add_argument("--prompt-password",
                               action="store_true",
                               help="prompt for postgres password")
    manual_parser.add_argument("--dbname",
                               required=True,
                               help="postgres database")
    manual_parser.add_argument("--schema", help="postgres schema")
    manual_parser.add_argument("--table",
                               required=True,
                               help="destination table")
    manual_parser.add_argument(
        "--geomtype",
        required=True,
        help="geometry type (e.g. MULTILINESTRING, MULTIPOLYGON)")
    manual_parser.add_argument("--srid",
                               required=True,
                               help="SRID of the geometry column")
    manual_parser.add_argument("--mode",
                               choices=["append", "overwrite"],
                               help="append or overwrite an existing table")
    manual_parser.add_argument("--dry-run",
                               action="store_true",
                               help="print the ogr2ogr command and exit")
    manual_parser.set_defaults(func=process_manual)


if __name__ == '__main__':
    raise SystemExit(main())