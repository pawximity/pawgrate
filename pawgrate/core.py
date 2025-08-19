import sys
import time

from pawgrate.config import ImportConfig
from pawgrate.loader import load_data
import yaml


def process_file(args):
    config_file = args.config
    if config_file:
        try:
            print("[*] Loading config file", config_file)
            import_config = ImportConfig(**load_yaml(config_file))
            return process_config(import_config)
        except FileNotFoundError:
            print("[!] Could not find file", config_file)
            return 1
        except yaml.YAMLError as e:
            print("[!] Invalid yaml", e)
            return 1
    print("[!] Config file was not provided")
    return 1


def process_manual(args):
    import_config = ImportConfig(src=args.src,
                                 dbname=args.dbname,
                                 schema=args.schema,
                                 user=args.user,
                                 host=args.host,
                                 port=args.port,
                                 table=args.table,
                                 geomtype=args.geomtype,
                                 srid=args.srid,
                                 mode=args.mode,
                                 prompt_password=args.prompt_password,
                                 dry_run=args.dry_run)
    return process_config(import_config)


def process_config(config):
    print(f"[*] Importing {config.src} into {config.dbname}.{config.table}")
    command, process = load_data(config)
    command_output = ' '.join(command)
    if process is None and config.dry_run:
        print("[+]", command_output)
        return 0
    print("[*] Executing command")
    print("[+]", command_output)
    show_progress(process)
    if process.returncode == 0:
        print("[+] Import completed successfully")
    else:
        print(f"[!] Import failed with record code {process.returncode}")
        print(f"[!] stderr {process.stderr}")
        print("[-]", " ".join(command))
    return process.returncode


def show_progress(process):
    counter = 0
    display = '@' * 50
    while process.poll() is None:
        line = f"{display[:counter % len(display)]}"
        sys.stdout.write("\r\033[K" + line)
        sys.stdout.flush()
        counter += 1
        time.sleep(1.00)
    sys.stdout.write("\r\033[K")


def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)