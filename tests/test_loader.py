import pytest
import types


def test_load_data_ogr2ogr_missing_raises(monkeypatch):
    from pawgrate import loader
    from pawgrate.config import ImportError

    monkeypatch.setattr(loader.shutil, "which", lambda *_: None)

    with pytest.raises(ImportError):
        loader.load_data(create_config())


def test_load_data_dry_run(monkeypatch):
    from pawgrate import loader

    monkeypatch.setattr(loader.shutil, "which", lambda *_: "/usr/bin/ogr2ogr")

    cmd, proc = loader.load_data(create_config(dry_run=True))
    assert proc is None
    assert cmd[0] == "ogr2ogr"


def test_load_data_spawns_process(monkeypatch):
    from pawgrate import loader

    monkeypatch.setattr(loader.shutil, "which", lambda *_: "/usr/bin/ogr2ogr")
    monkeypatch.setattr(loader, "getpass", lambda prompt="": "secret")

    class FakeProc:

        def __init__(self, *a, **k):
            self.returncode = None

        def poll(self):
            return None

        def communicate(self):
            return ("", "")

    seen = {}

    def fake_popen(cmd, **kw):
        seen["cmd"] = cmd
        return FakeProc()

    monkeypatch.setattr(loader.subprocess, "Popen", fake_popen)

    cmd, proc = loader.load_data(create_config())
    assert proc is not None
    assert seen["cmd"][0] == "ogr2ogr"


def test_build_command_flags():
    from pawgrate import loader

    config = create_config(mode="append")
    cmd = loader.build_command(config)
    cmd_output = " ".join(cmd)
    assert cmd[0] == "ogr2ogr"
    assert "-append" in cmd and "-overwrite" not in cmd
    assert f"-nln {config.schema}.{config.table}" in cmd_output
    assert "-t_srs" in cmd and f"EPSG:{config.srid}" in cmd_output
    assert "-nlt" in cmd and config.geomtype in cmd


def test_write_mode_invalid_raises():
    from pawgrate import loader
    from pawgrate.config import ConfigError

    with pytest.raises(ConfigError):
        loader.write_mode("nope")


def create_config(**data):
    Config = types.SimpleNamespace
    config_map = dict(host="localhost",
                      dbname="pawx",
                      user="u",
                      port="5432",
                      src="/tmp/a.shp",
                      schema="public",
                      table="t",
                      geomtype="PROMOTE_TO_MULTI",
                      srid="26912",
                      mode="append",
                      prompt_password=False,
                      dry_run=False)
    config_map.update(data)
    return Config(**config_map)