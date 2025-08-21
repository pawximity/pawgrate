import types
import pytest
from io import StringIO
import sys


def test_process_file(monkeypatch, tmp_path):
    from pawgrate import core

    config_file_path = create_yaml(tmp_path)

    called = {}

    def fake_process_config(config):
        called["config"] = config
        return 0

    monkeypatch.setattr(core, "process_config", fake_process_config)

    args = make_args(config=str(config_file_path))
    return_code = core.process_file(args)
    assert return_code == 0 or return_code is None
    assert called["config"].src == "/tmp/a.shp"
    assert called["config"].dbname == "pawx"
    assert called["config"].table == "t"


def test_process_file_missing_config_raises():
    from pawgrate import core
    from pawgrate.config import ConfigError

    with pytest.raises(ConfigError):
        core.process_file(make_args(config=None))


def test_process_file_not_found_raises(tmp_path):
    from pawgrate import core
    from pawgrate.config import ConfigError

    missing = tmp_path / "missing.yml"
    with pytest.raises(ConfigError):
        core.process_file(make_args(config=str(missing)))


def test_process_file_invalid_yaml_raises(monkeypatch, tmp_path):
    from pawgrate import core
    from pawgrate.config import ConfigError

    invalid = tmp_path / "invalid.yml"
    invalid.write_text("src: [unterminated\n")
    with pytest.raises(ConfigError):
        core.process_file(make_args(config=str(invalid)))


def test_process_manual_filters_and_delegates(monkeypatch):
    from pawgrate import core

    called = {}

    def fake_process_config(config):
        called["config"] = config
        return 0

    monkeypatch.setattr(core, "process_config", fake_process_config)

    args = types.SimpleNamespace(src="/tmp/a.shp",
                                 dbname="pawx",
                                 table="t",
                                 geomtype="PROMOTE_TO_MULTI",
                                 srid="26912",
                                 user="postgres",
                                 schema="public",
                                 host="localhost",
                                 port="5432",
                                 mode="append",
                                 prompt_password=False,
                                 dry_run=False,
                                 command="import",
                                 func="process_manual")

    return_code = core.process_manual(args)
    assert return_code == 0 or return_code is None
    config = called["config"]
    assert config.src == "/tmp/a.shp"
    assert not hasattr(config, "command")
    assert not hasattr(config, "func")


def test_process_config_dry_run_prints_command(monkeypatch):
    from pawgrate import core

    def fake_load_data(config):
        return ([
            "ogr2ogr", "-f", "PostgreSQL", "PG:...", config.src, "-nln",
            f"{config.schema}.{config.table}"
        ], None)

    monkeypatch.setattr(core, "load_data", fake_load_data)

    buf, old = StringIO(), sys.stdout
    sys.stdout = buf
    try:
        return_code = core.process_config(create_config(dry_run=True))
    finally:
        sys.stdout = old

    stdout = buf.getvalue()
    assert "ogr2ogr" in stdout
    assert "-nln public.t" in stdout
    assert return_code is None


def test_process_config_success(monkeypatch):
    from pawgrate import core

    monkeypatch.setattr(core, "show_progress", lambda progress: None)

    class FakeProc:
        returncode = 0

        def communicate(self):
            return ("ok", "")

        def poll(self):
            return 0

    def fake_load_data(config):
        return (["ogr2ogr", ""], FakeProc())

    monkeypatch.setattr(core, "load_data", fake_load_data)

    return_code = core.process_config(create_config())
    assert return_code is None


def test_process_config_failure_raises_with_stderr(monkeypatch):
    from pawgrate import core
    from pawgrate.config import ImportError

    monkeypatch.setattr(core, "show_progress", lambda progress: None)
    stderr_msg = "error"

    class FakeProc:
        returncode = 2

        def communicate(self):
            return ("", stderr_msg)

        def poll(self):
            return 0

    def fake_load_data(config):
        return (["ogr2ogr", "--flag", ""], FakeProc())

    monkeypatch.setattr(core, "load_data", fake_load_data)

    with pytest.raises(ImportError) as e:
        core.process_config(create_config())

    err_msg = str(e.value)
    assert "return code 2" in err_msg
    assert stderr_msg in err_msg


def make_args(**kw):
    return types.SimpleNamespace(**kw)


def create_yaml(tmp_path):
    yaml_file = tmp_path / "cfg.yml"
    yaml_file.write_text("src: /tmp/a.shp\n"
                         "dbname: pawx\n"
                         "table: t\n"
                         "geomtype: PROMOTE_TO_MULTI\n"
                         "srid: '26912'\n"
                         "user: postgres\n")
    return yaml_file


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