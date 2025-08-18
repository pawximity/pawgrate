import argparse
import sys
import time

from pawgrate.config import ImportConfig
from pawgrate.loader import load_data


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
    if hasattr(args, "func"):
        print(puppy())
        args.func(args)
    else:
        parser.print_help()


def arg_parser():
    parser = argparse.ArgumentParser(
        description="pawgrate: Import geospatial data into PostGIS")
    subparsers = parser.add_subparsers(title="Commands", dest="command")
    import_parser = subparsers.add_parser("import",
                                          help="Import a file into PostGIS")
    import_parser.add_argument(
        "--src",
        required=True,
        help="Path to the import file (e.g. .geojson, .shp)")
    import_parser.add_argument("--dbname",
                               required=True,
                               help="Name of the Postgres database")
    import_parser.add_argument("--schema",
                               default="public",
                               help="Name of the Postgres schema")
    import_parser.add_argument("--user",
                               required=True,
                               help="Name of the Postgres user")
    import_parser.add_argument("--host",
                               default="localhost",
                               help="Name of the Postgres host")
    import_parser.add_argument("--port",
                               default="5432",
                               help="Postgres port (Default: 5432)")
    import_parser.add_argument("--table",
                               required=True,
                               help="Name of the destination table")
    import_parser.add_argument(
        "--geomtype",
        required=True,
        help="Geometry type (e.g. MULTILINESTRING, MULTIPOLYGON)")
    import_parser.add_argument("--srid",
                               required=True,
                               help="SRID of the geometry column")
    import_parser.add_argument("--mode",
                               default="append",
                               help="Append or overwrite an existing table")
    import_parser.add_argument("--prompt-password",
                               action="store_true",
                               help="Prompt for Postgres password.")
    import_parser.set_defaults(func=import_data)
    return parser


def import_data(args):
    config = ImportConfig(src=args.src,
                          dbname=args.dbname,
                          schema=args.schema,
                          user=args.user,
                          host=args.host,
                          port=args.port,
                          table=args.table,
                          geomtype=args.geomtype,
                          srid=args.srid,
                          mode=args.mode,
                          prompt_password=args.prompt_password)
    print(
        f"[*] Importing {config.src} into {config.dbname}.{config.table} as {config.user}"
    )
    command, process = load_data(config)
    print("[*] Executing command")
    print("[+]", " ".join(command))
    show_progress(process)
    if process.returncode == 0:
        print("[+] Import completed successfully")
    else:
        print(f"[!] Import failed with record code: {result.returncode}")
        print(f"[!] stderr: {result.stderr}")
        print("[-]", " ".join(command))
        sys.exit(result.returncode)


def show_progress(process):
    counter = 0
    display = '@' * 50
    while process.poll() is None:
        line = f"{display[:counter % len(display)]}"
        sys.stdout.write("\r\033[K" + line)
        sys.stdout.flush()
        counter += 1
        time.sleep(1.00)
    sys.stdout.write("\r\033[K")


if __name__ == '__main__':
    main()