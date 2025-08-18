from getpass import getpass
import os
import shutil
import subprocess

from pawgrate.config import ImportConfig


def load_data(config):
    if not shutil.which("ogr2ogr"):
        raise RuntimeError(
            "ogr2ogr not found in PATH. Make sure GDAL is installed")
    env_copy = os.environ.copy()
    if config.prompt_password:
        env_copy['PGPASSWORD'] = getpass("[!] Postgres password: ")
    # specifically using subprocess to avoid the messy dependencies of the bindings...
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
    process = subprocess.Popen(command,
                               env=env_copy,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)
    return command, process


def write_mode(mode):
    if mode == 'append':
        return "-append"
    elif mode == 'overwrite':
        return "-overwrite"
    else:
        raise ValueError(f"Invalid mode: {mode}")