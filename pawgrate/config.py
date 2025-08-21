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
    user: str
    table: str
    geomtype: str
    srid: str
    host: str = "localhost"
    port: str = "5432"
    schema: str = "public"
    mode: str = "append"
    prompt_password: bool = False
    dry_run: bool = False