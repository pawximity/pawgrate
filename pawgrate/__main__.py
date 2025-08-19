import argparse

from pawgrate.core import process_file, process_manual


def puppy():
    return r"""
    / \__
(    @\___
/         O
/   (_____/
/_____/ U
"""


def main():
    parser = arg_parser()
    args = parser.parse_args()
    print(puppy())
    return args.func(args)


def arg_parser():
    parser = argparse.ArgumentParser(
        description="pawgrate: friendly ogr2ogr wrapper for PostGIS")
    commands_subparser = parser.add_subparsers(title="Commands",
                                               dest="command")
    # import parent
    import_parser = commands_subparser.add_parser(
        "import", help="Import a file into PostGIS")
    import_subparser = import_parser.add_subparsers(dest="mode", required=True)
    # import flags using a yaml config file
    file_parser = import_subparser.add_parser(
        "file", help="Import using a yaml config")
    file_parser.add_argument("--config",
                             required=True,
                             help="Use a yaml config file")
    file_parser.set_defaults(func=process_file)
    # import flags individually through the cli
    manual_parser = import_subparser.add_parser(
        "manual", help="Import using individual flags")
    manual_parser.add_argument(
        "--src",
        required=True,
        help="Path to the import file (e.g. .geojson, .shp)")
    manual_parser.add_argument("--dbname",
                               required=True,
                               help="Name of the Postgres database")
    manual_parser.add_argument("--schema",
                               default="public",
                               help="Name of the Postgres schema")
    manual_parser.add_argument("--user",
                               required=True,
                               help="Name of the Postgres user")
    manual_parser.add_argument("--host",
                               default="localhost",
                               help="Name of the Postgres host")
    manual_parser.add_argument("--port",
                               default="5432",
                               help="Postgres port (Default: 5432)")
    manual_parser.add_argument("--table",
                               required=True,
                               help="Name of the destination table")
    manual_parser.add_argument(
        "--geomtype",
        required=True,
        help="Geometry type (e.g. MULTILINESTRING, MULTIPOLYGON)")
    manual_parser.add_argument("--srid",
                               required=True,
                               help="SRID of the geometry column")
    manual_parser.add_argument("--mode",
                               choices=["append", "overwrite"],
                               help="Append or overwrite an existing table")
    manual_parser.add_argument("--prompt-password",
                               action="store_true",
                               help="Prompt for Postgres password")
    manual_parser.add_argument("--dry-run",
                               action="store_true",
                               help="Print the ogr2ogr command and exit")
    manual_parser.set_defaults(func=process_manual)
    return parser


if __name__ == '__main__':
    raise SystemExit(main())