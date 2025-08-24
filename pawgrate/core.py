import shlex
import sys
import time

from pawgrate.config import ConfigError
from pawgrate.config import ImportConfig
from pawgrate.config import ImportError
from pawgrate.loader import load_data
import yaml


def process_file(args):
    """Processes a YAML config file.

    Loads a YAML file and creates an ImportConfig object from its contents. 
    The resulting config is passed on for further processing. 
    Raises errors if the file path wasn't provided, it can't find the file on disk, 
    and if the yaml within the file is invalid.
    """
    config_file = args.config
    if not config_file:
        raise ConfigError("Config file was not provided")
    try:
        print("[*] Loading config file", config_file)
        with open(config_file, 'r') as f:
            yaml_data = yaml.safe_load(f) or {}
        return process_config(ImportConfig(**yaml_data))
    except FileNotFoundError:
        raise ConfigError(f"Could not find config file {config_file}")
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid yaml {e}")


def process_manual(args):
    """Processes manually provided args.

    Loads manually provided args and creates an ImportConfig object.
    The resulting config is passed on for further processing.
    """
    args_dict, allowed = vars(args), ImportConfig.__dataclass_fields__.keys()
    filtered_args = {
        k: v
        for k, v in args_dict.items() if k in allowed and v is not None
    }
    return process_config(ImportConfig(**filtered_args))


def process_config(config):
    """Processes the ImportConfig object.

    Builds an ogr2ogr command from the provided config, spawns the
    subprocess, and monitors its execution. Raises an error if 
    the process fails.
    """
    print(f"[*] Importing {config.src} into {config.dbname}.{config.table}")
    command, process = load_data(config)
    command_output = shlex.join(command)
    if process is None and config.dry_run:
        print("[+]", command_output)
        return
    print("[*] Executing command")
    print("[+]", command_output)
    show_progress(process)
    _, stderr = process.communicate()
    if process.returncode == 0:
        print("[+] Import completed successfully")
        return
    else:
        print("\n[-]", command_output)
        raise ImportError(
            f"ogr2ogr failed with return code {process.returncode}\n\n{stderr.strip()}"
        )


def show_progress(process):
    counter, display = 0, '@' * 50
    while process.poll() is None:
        line = f"{display[:counter % len(display)]}"
        sys.stdout.write("\r\033[K" + line)
        sys.stdout.flush()
        counter += 1
        time.sleep(0.25)
    sys.stdout.write("\r\033[K")