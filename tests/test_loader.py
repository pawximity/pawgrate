from pawgrate import loader
import pytest
import types


def test_load_data_ogr2ogr_missing_raises(monkeypatch):
    from pawgrate.error import ImportError

    monkeypatch.setattr(loader.shutil, "which", lambda *_: None)

    with pytest.raises(ImportError):
        loader.load_data(create_config())


def test_load_data_dry_run(monkeypatch):
    monkeypatch.setattr(loader.shutil, "which", lambda *_: "/usr/bin/ogr2ogr")

    cmd, proc = loader.load_data(create_config(dry_run=True))
    assert proc is None
    assert cmd[0] == "ogr2ogr"


def test_load_data_spawns_process(monkeypatch):
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
    config = create_config(mode="append")
    cmd = loader.build_command(config)
    cmd_output = " ".join(cmd)
    assert cmd[0] == "ogr2ogr"
    assert "-append" in cmd and "-overwrite" not in cmd
    assert f"-nln {config.schema}.{config.table}" in cmd_output
    assert "-t_srs" in cmd and f"EPSG:{config.srid}" in cmd_output
    assert "-nlt" in cmd and config.geomtype in cmd


def test_write_mode_invalid_raises():
    from pawgrate.error import ConfigError

    with pytest.raises(ConfigError):
        loader.write_mode("nope")


def create_config(**data):
    Config = types.SimpleNamespace
    config_map = dict(src="/tmp/a.shp",
                      host="localhost",
                      port="5432",
                      user="u",
                      prompt_password=False,
                      dbname="pawx",
                      schema="public",
                      table="t",
                      geomtype="PROMOTE_TO_MULTI",
                      srid="26912",
                      mode="append",
                      dry_run=False)
    config_map.update(data)
    return Config(**config_map)