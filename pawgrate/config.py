from dataclasses import dataclass


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
