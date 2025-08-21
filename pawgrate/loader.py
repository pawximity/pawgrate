from getpass import getpass
import os
import shutil
import subprocess

from pawgrate.config import ConfigError
from pawgrate.config import ImportConfig
from pawgrate.config import ImportError


def load_data(config):
    """Loads config data into an ogr2ogr command.

    Builds a command and spawns a subprocess unless dry_run is set.
    Returns the command and the process object. Raises an error if 
    ogr2ogr isn't found on the class path.
    """
    if not shutil.which("ogr2ogr"):
        raise ImportError(
            "ogr2ogr not found in PATH. Make sure GDAL is installed")
    command = build_command(config)
    if config.dry_run:
        return command, None
    env_copy = os.environ.copy()
    if config.prompt_password:
        env_copy["PGPASSWORD"] = getpass("[!] Postgres password ")
    # specifically using subprocess to avoid the messy dependencies of the bindings...
    process = subprocess.Popen(command,
                               env=env_copy,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)
    return command, process


def build_command(config):
    command = [
        'ogr2ogr',
        '-f',
        'PostgreSQL',
        f'PG:host={config.host} dbname={config.dbname} user={config.user} port={config.port}',
        config.src,
        '-nln',
        f'{config.schema}.{config.table}',
        '-lco',
        f'SCHEMA={config.schema}',
        '-nlt',
        config.geomtype,
        '-lco',
        'GEOMETRY_NAME=geom',
        '-lco',
        'FID=gid',
        '-lco',
        'SPATIAL_INDEX=GIST',
        '-t_srs',
        f'EPSG:{config.srid}',
    ]
    command.append(write_mode(config.mode))
    return command


def write_mode(mode):
    if mode == "append":
        return "-append"
    elif mode == "overwrite":
        return "-overwrite"
    else:
        raise ConfigError(f"Invalid mode: {mode}")