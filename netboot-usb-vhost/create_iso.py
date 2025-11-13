#!/usr/bin/env python3
"""
This script is designed to create a custom Debian preseed ISO. It automates the
extraction of a base ISO, modifies its contents, and regenerates the ISO with
custom configurations such as GRUB and preseed files.

Functionality:
- Validates required commands and environment variables.
- Asks for information about the preseeded system(s)
- Extracts an existing Debian ISO.
- Generates preseed configuration files for automated server installations.
- Updates GRUB configuration for boot customization.
- Regenerates necessary checksums (e.g., md5sums).
- Repackages the modified ISO.

Usage:
Ensure that the STOCK_ISO environment variable is set to the path of the input
ISO file. Run the script directly to create the custom ISO.

Requirements:
- External tools: 7z, xorriso, gunzip, cpio
- Python dependencies: jinja2
"""

import logging
import os
import sys
import shutil
import subprocess
from create_iso_utils.server_opts import ServerOpts
from jinja2 import Environment, FileSystemLoader

class Config:
    """
    A configuration class for managing script parameters and default paths.

    Attributes:
        SCRIPT_DIR (str): Directory of the script.
        TMP_DIR (str): Temporary directory for extracted ISO.
        INSTALL_ARCH_DIR (str): Directory for installation files.
        PRESEED_PREFIX (str): Path to the preseed configuration file.
        DEBUG (bool): Debug mode flag.
        EFI_IMG (str): Path to the EFI boot image in the ISO.
        STOCK_ISO (str): Path to the stock ISO file.
        OUTPUT_ISO (str): Path for the output custom ISO.
        LOG_DIR (str): Directory for log files.
    """
    SCRIPT_DIR = os.path.dirname(__file__)
    TMP_DIR = os.path.join(f"{SCRIPT_DIR}", "tmp/")
    INSTALL_ARCH_DIR=f"{TMP_DIR}/install.amd"
    PRESEED_PREFIX = os.path.join(os.path.abspath(os.path.dirname(__file__)), "preseed.cfg")
    DEBUG = os.getenv("DEBUG", "1").lower() in ("1", "true", "yes")
    EFI_IMG="boot/grub/efi.img"                 #  Location in iso
    STOCK_ISO = os.getenv("STOCK_ISO")
    OUTPUT_ISO=f"{SCRIPT_DIR}/custom.iso"
    LOG_DIR=f"{SCRIPT_DIR}/log"

def setup_logging(debug: bool) -> None:
    log_level = logging.INFO
    if debug:
        log_level = logging.DEBUG

    """Configure logging module"""
    logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("log/create_iso.log"),
                logging.StreamHandler()
            ]
        )


def log_subprocess_output(output) -> None:
    output_lines = output.splitlines()
    for line in output_lines:
        if line.strip():
            logging.info(f"Subprocess output: {line}")


def fatal(message):
    """Print fatal error messages and exit."""
    logging.error(message)
    sys.exit(message)


def check_command(command):
    """Check if a command exists on the system."""
    if not shutil.which(command):
        fatal(f"Error: '{command}' command is required but not found. " +
            "Please install it before proceeding.")


def check_iso_var(stock_iso):
    """Validate the STOCK_ISO variable."""
    logging.info(f"Stock iso is: {stock_iso}")

    if not stock_iso:
        fatal("STOCK_ISO needs to be defined!")
    elif os.path.isfile(stock_iso):
        logging.debug(f"'{stock_iso}' is a normal file.")
    elif os.path.islink(stock_iso) and os.path.isfile(os.path.realpath(stock_iso)):
        logging.debug(f"'{stock_iso}' is a symlink to a normal file.")
    else:
        fatal("STOCK_ISO must be a normal file or a symlink to a normal file.")


def verify_empty_dir(tmp_dir):
    """Verify that TMP_DIR exists and is empty."""
    logging.debug(f"Temp directory is {tmp_dir}")
    if os.path.isdir(tmp_dir) and not os.listdir(tmp_dir):
        logging.debug(f"{tmp_dir} is empty")
    else:
        fatal(f"{tmp_dir} is not empty or does not exist")


def extract_iso(stock_iso, tmp_dir):
    """Extract ISO"""
    logging.info("Extracting ISO files")
    extract_command = ["7z", "x", f"-o{tmp_dir}", stock_iso]
    try:
        result = subprocess.run(extract_command, capture_output=True, text=True)
        log_subprocess_output(result.stdout)
        logging.info("ISO image extracted")
    except subprocess.CalledProcessError as e:
        fatal(f"Subprocess failed: {e.stderr}")
    logging.info("Finished extracting ISO files")


def regenerate_md5sums(tmp_dir):
    """Regenerate md5sums for all files in tmp_dir and save to md5sum.txt."""

    logging.info("Regenerating md5sums")
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
        logging.critical(f"Error while regenerating md5sums: {str(e)}")
        raise

    logging.info(f"MD5sums written to {md5sum_file}")


def rebuild_iso_image(tmp_dir, output_iso, efi_img):
    """Create the ISO image."""
    logging.info("Creating the ISO image")
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
    try:
        result = subprocess.run(iso_command, capture_output=True, text=True)
        log_subprocess_output(result.stderr)
        logging.info("ISO image created")
    except subprocess.CalledProcessError as e:
        fatal(f"Subprocess failed: {e.stderr}")


def create_dir(base_dir, dir_name):
    """
    Create a directory if it does not exist.

    Args:
        base_dir (str): The base directory path.
        dir_name (str): The name of the directory to create.

    Returns:
        str: The full path of the created directory.
    """
    full_path = os.path.join(base_dir, dir_name)
    logging.info(f"Creating directory {full_path}")
    os.makedirs(full_path, exist_ok=True)
    return full_path


def generate_preseed_configs(tmp_dir, preseed_values):
    """
    Generate preseed configuration files for a list of servers.

    Args:
        tmp_dir (str): The temporary directory where the files will be created.
        preseed_values (ServerOpts): Object containing server configuration values.

    Returns:
        None
    """
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("preseed.cfg.j2")
    preseed_dir = create_dir(tmp_dir, 'preseed')

    for server in preseed_values.get_hosts():
        preseed_cfg = template.render(
                    host_hostname = server['name'],
                    host_ip = server['ip'],
                    host_gateway = server['gateway'],
                    host_netmask = server['netmask'],
                    host_dns = server['dns'],
                    host_domain = server['domain'],
                )
        config_file = os.path.join(preseed_dir, server['config'])
        logging.info(f"Writing {server['config']} preseed file to {config_file}")

        with open(config_file, "w") as file:
            file.write(preseed_cfg)
        logging.info(f"Config file '{server['name']}' written to '{config_file}'")


def generate_grub_config(tmp_dir, preseed_values):
    """
    Generate the GRUB configuration file based on server values.

    Args:
        tmp_dir (str): The temporary directory where the GRUB config will be written.
        preseed_values (ServerOpts): Object containing server configuration values.

    Returns:
        None
    """
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("grub.cfg.j2")
    grub_cfg = ""
    try:
        grub_cfg = template.render(server_list = preseed_values.get_hosts())
    except Exception as e:
        fatal('Could not render template: ' + str(e))

    output_file = os.path.join(tmp_dir, 'boot/grub/grub.cfg')

    logging.info(f"Writing grub config to: {output_file}")
    with open(output_file, "w") as file:
        file.write(grub_cfg)
    logging.info("Grub config file written")


def create_preseed_iso(config, preseed_values):
    """Main function to create the custom preseed ISO."""
    try:
        extract_iso(config.STOCK_ISO, config.TMP_DIR)
        generate_preseed_configs(config.TMP_DIR, preseed_values)
        generate_grub_config(config.TMP_DIR, preseed_values)
        regenerate_md5sums(config.TMP_DIR)
        rebuild_iso_image(config.TMP_DIR, config.OUTPUT_ISO, config.EFI_IMG)
        logging.info(f"Preseed ISO can be found at '{config.OUTPUT_ISO}'")
    except Exception as e:
        fatal(str(e))


if __name__ == "__main__":
    setup_logging(Config.DEBUG)
    if not Config.DEBUG:
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

    create_preseed_iso(Config, preseed_values)
