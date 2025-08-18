import os
import shutil
import subprocess
from getpass import getpass

from pawgrate.config import ImportConfig


def load_data(config: ImportConfig) -> tuple[list[str], subprocess.CompletedProcess]:
    if not shutil.which("ogr2ogr"):
        raise RuntimeError("ogr2ogr not found in PATH. Make sure GDAL is installed")

    if config.prompt_password:
        os.environ['PGPASSWORD'] = getpass("Postgres password: ")
    # specifically using subprocess to avoid the messy dependencies of the bindings...
    command = [
        'ogr2ogr',
        '-f', 'PostgreSQL',
        f'PG:host={config.host} dbname={config.dbname} user={config.user} port={config.port}',
        config.src,
        '-nln', f'{config.schema}.{config.table}',
        '-lco', f'SCHEMA={config.schema}',
        '-nlt', config.geomtype,
        '-lco', 'GEOMETRY_NAME=geom',
        '-lco', 'FID=gid',
        '-lco', 'SPATIAL_INDEX=GIST',
        '-t_srs', f'EPSG:{config.srid}',
    ]
    if config.mode == 'append':
        command.append("-append")
    elif config.mode == 'overwrite':
        command.append("-overwrite")
    else:
        raise ValueError(f"Invalid mode: {config.mode}")
    command.append("-progress")
    result = subprocess.run(command, capture_output=True, text=True)
    return command, result
