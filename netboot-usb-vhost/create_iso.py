#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess
from create_iso_utils.server_opts import ServerOpts
from jinja2 import Environment, FileSystemLoader

class Config:
    SCRIPT_DIR = os.path.dirname(__file__)
    TMP_DIR = os.path.join(f"{SCRIPT_DIR}", "tmp/")
    INSTALL_ARCH_DIR=f"{TMP_DIR}/install.amd"
    PRESEED_PREFIX = os.path.join(os.path.abspath(os.path.dirname(__file__)), "preseed.cfg")
    DEBUG = os.getenv("DEBUG", "1").lower() in ("1", "true", "yes")
    EFI_IMG="boot/grub/efi.img"                 #  Location in iso
    STOCK_ISO = os.getenv("STOCK_ISO")
    OUTPUT_ISO=f"{SCRIPT_DIR}/custom.iso"
    LOG_DIR=f"{SCRIPT_DIR}/log"

def debug(message):
    """Print debug messages if DEBUG is set."""
    if Config.DEBUG:
        print(f"[DEBUG]: {message}")

def fatal(message):
    """Print fatal error messages and exit."""
    print(f"[FATAL]: {message}", file=sys.stderr)
    sys.exit(1)

def check_command(command):
    """Check if a command exists on the system."""
    if not shutil.which(command):
        fatal(f"Error: '{command}' command is required but not found. Please install it before proceeding.")

def check_iso_var(stock_iso):
    """Validate the STOCK_ISO variable."""
    debug(f"Stock iso is: {stock_iso}")

    if not stock_iso:
        fatal("STOCK_ISO needs to be defined!")
    elif os.path.isfile(stock_iso):
        debug(f"'{stock_iso}' is a normal file.")
    elif os.path.islink(stock_iso) and os.path.isfile(os.path.realpath(stock_iso)):
        debug(f"'{stock_iso}' is a symlink to a normal file.")
    else:
        fatal("STOCK_ISO must be a normal file or a symlink to a normal file.")

def verify_empty_dir(tmp_dir):
    """Verify that TMP_DIR exists and is empty."""
    debug(tmp_dir)
    if os.path.isdir(tmp_dir) and not os.listdir(tmp_dir):
        debug(f"{tmp_dir} is empty")
    else:
        fatal(f"{tmp_dir} is not empty or does not exist")

def extract_iso(stock_iso, tmp_dir):
    """Extract ISO"""
    debug("Extracting ISO files")
    extract_command = ["7z", "x", f"-o{tmp_dir}", stock_iso]
    with open(os.path.join(Config.LOG_DIR, "7z.log"), "w") as log_file:
        subprocess.run(extract_command, stdout=log_file, stderr=subprocess.STDOUT, check=True)
    debug("Finished extracting ISO files")


def regenerate_md5sums(tmp_dir):
    """Regenerate md5sums for all files in tmp_dir and save to md5sum.txt."""

    debug("Regenerating md5sums")
    md5sum_file = os.path.join(tmp_dir, "md5sum.txt")

    try:
        with open(md5sum_file, "w") as f_out:
            for root, _, files in os.walk(tmp_dir):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    # Skip the md5sums.txt file itself
                    if os.path.relpath(file_path, tmp_dir) == "md5sum.txt":
                        continue
                    relative_path = os.path.relpath(file_path, tmp_dir)
                    result = subprocess.run(["md5sum", file_path], capture_output=True, text=True, check=True)
                    if result.stdout:
                        md5_value = result.stdout.split()[0]
                        f_out.write(f"{md5_value} ./{relative_path}\n")
                    else:
                        raise RuntimeError(f"Failed to compute md5sum for file: {file_path}")
    except Exception as e:
        debug(f"Error while regenerating md5sums: {str(e)}")
        raise

    debug(f"MD5sums written to {md5sum_file}")

def rebuild_iso_image(tmp_dir, output_iso, efi_img):
    """Create the ISO image."""
    debug("Creating the ISO image")
    iso_command = [
        "xorriso",
        "-as", "mkisofs",
        "-o", output_iso,
        "-r", "-J",
        "-isohybrid-mbr", "/usr/lib/ISOLINUX/isohdpfx.bin",
        "-partition_offset", "16",
        "-eltorito-boot", "isolinux/isolinux.bin",
        "-eltorito-catalog", "isolinux/boot.cat",
        "-no-emul-boot", "-boot-load-size", "4", "-boot-info-table",
        "-eltorito-alt-boot",
        "-e", efi_img,
        "-no-emul-boot",
        "-isohybrid-gpt-basdat",
        tmp_dir
    ]
    subprocess.run(iso_command, check=True)
    debug("ISO image created")

def create_dir(base_dir, dir_name):
    full_path = os.path.join(base_dir, dir_name)
    debug(f"Creating directory {full_path}")
    os.makedirs(full_path, exist_ok=True)
    return full_path

def generate_preseed_configs(tmp_dir, preseed_values):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("preseed.cfg.j2")
    preseed_dir = create_dir(tmp_dir, 'preseed')

    for server in preseed_values.get_hosts():
        # FIXME: Way too many arguments!
        preseed_cfg = template.render(
                    host_hostname = server['name'],
                    host_ip = server['ip'],
                    host_gateway = server['gateway'],
                    host_netmask = server['netmask'],
                    host_dns = server['dns'],
                    host_domain = server['domain'],
                )
        config_file = os.path.join(preseed_dir, server['config'])
        debug(f"Writing {server['config']} preseed file to {config_file}")

        with open(config_file, "w") as file:
            file.write(preseed_cfg)
        print(f"Config file '{server['name']}' written to '{config_file}'")

def generate_grub_config(tmp_dir, preseed_values):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("grub.cfg.j2")
    grub_cfg = ""
    try:
        grub_cfg = template.render(server_list = preseed_values.get_hosts())
    except Exception as e:
        fatal('Could not render template: ' + str(e))

    output_file = os.path.join(tmp_dir, 'boot/grub/grub.cfg')

    debug(f"Writing grub config to: {output_file}")
    with open(output_file, "w") as file:
        file.write(grub_cfg)
    debug("Grub config file written")

def create_preseed_iso(config, preseed_values):
    """Main function to create the custom preseed ISO."""
    try:
        extract_iso(config.STOCK_ISO, config.TMP_DIR)
        generate_preseed_configs(config.TMP_DIR, preseed_values)
        generate_grub_config(config.TMP_DIR, preseed_values)
        regenerate_md5sums(config.TMP_DIR)
        rebuild_iso_image(config.TMP_DIR, config.OUTPUT_ISO, config.EFI_IMG)
        print(f"Preseed ISO can be found at '{config.OUTPUT_ISO}'")
    except Exception as e:
        fatal(str(e))

if __name__ == "__main__":
    # Prep
    if not Config.STOCK_ISO:
        raise EnvironmentError("Error: 'STOCK_ISO' environmental variable is not defined.")
    check_iso_var(Config.STOCK_ISO)
    check_command("7z")
    check_command("xorriso")
    check_command("gunzip")
    check_command("cpio")

    try:
        verify_empty_dir(Config.TMP_DIR)
    except Exception as e:
        fatal(str(e))

    preseed_values = ServerOpts()

    # Making the image
    create_preseed_iso(Config, preseed_values)
