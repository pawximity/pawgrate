from dataclasses import dataclass


class PawgrateError(Exception):
    pass


class ConfigError(PawgrateError):
    pass


class ImportError(PawgrateError):
    pass


@dataclass
class ImportConfig:
    src: str
    dbname: str
    schema: str
    user: str
    host: str
    port: str
    table: str
    geomtype: str
    srid: str
    mode: str
    prompt_password: bool
    dry_run: bool