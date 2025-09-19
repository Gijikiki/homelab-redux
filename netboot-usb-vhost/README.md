# Netboot USB VHost Setup

## Purpose
This directory is designed to create a USB image that can be written to a USB
drive. The image will preseed the configuration for a virtual host (vhost),
streamlining the setup process.

The process assumes the availability of a **Debian 13 (Debian Trixie)** ISO
image (`netboot-usb`).

The full path of the netboot-usb iso should be set as the environmental variable
'STOCK\_ISO'.

## Build System: `make`
To generate the custom ISO, this directory uses `make` as the build system. The
following options are available:

### 1. `make build`
- Generates the custom ISO image, ready for writing to a USB drive.
- The file will be saved as 'custom.iso' in the netboot-usb-vhost 
  directory

### 2. `make cleanup`
- Cleans up temporary or generated files from the build process.

Ensure you have the `make` utility installed to use these commands effectively.
