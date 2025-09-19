#!/usr/bin/env bash

SCRIPT_DIR="$(cd $(dirname '${BASH_SOURCE[0]}') && pwd)"
DEBUG=1		# If undefined, no debug messages
TMP_DIR="${SCRIPT_DIR}/tmp"
OUTPUT_ISO="${SCRIPT_DIR}/custom.iso"
PRESEED_FILE="${SCRIPT_DIR}/preseed.cfg"
INSTALL_ARCH_DIR="${TMP_DIR}/install.amd"
LOG_DIR="${SCRIPT_DIR}/log"

debug() {
	if [ "$DEBUG" ]; then
		echo "[DEBUG]: $*"
	fi
}

fatal() {
	echo "[FATAL]: $*" >&2
	exit 1
}

# Function to check what commands we need
check_command() {
	if ! command -v "$1" &> /dev/null; then
		echo -n "Error: '$1' command is required but not found.  " >&2
		echo "Please install it before proceeding." >&2
		exit 1
	fi
}

check_iso_var() {
	local not_def_msg="STOCK_ISO needs to be defined!"

	debug "Stock iso is: $STOCK_ISO"

	if [ -z "$STOCK_ISO" ]; then
		fatal $not_def_msg
	elif [ -f "$STOCK_ISO" ]; then
		debug "'$STOCK_ISO' is a normal file."
	elif [ -L "$STOCK_ISO" ] && [ -f "$(readlink -f '$STOCK_ISO')" ]; then
		debug "'$STOCK_ISO' is a symlink to a normal file."
	else
		fatal "STOCK_ISO must be a normal file or a symlink to a normal file."
	fi
}

verify_empty_dir() {
	debug "$TMP_DIR"
	if [ -d "$TMP_DIR" ] && [ -z "$(ls -A "$TMP_DIR")" ]; then
		debug "$TMP_DIR) is empty"
	else
		fatal "$TMP_DIR is not empty or does not exist"
	fi
}

add_preseed_to_initrd() {
	debug "Extracting iso files"
	debug "Extract command: '7z x -o\"$TMP_DIR\" \"$STOCK_ISO\""
	7z x -o"$TMP_DIR" "$STOCK_ISO" > "$LOG_DIR/7z.log" 2>&1

	debug "Copying preseed.cfg to iso directory"
	cp "${PRESEED_FILE}" "${TMP_DIR}/preseed.cfg"

	debug "Setting write permissions on the iso directory"
	chmod +w -R "${INSTALL_ARCH_DIR}"

	debug "Decompressing initrd.gz"
	gunzip "${INSTALL_ARCH_DIR}/initrd.gz"

	debug "Copying preseed.cfg to end of initrd"
	echo preseed.cfg | cpio -H newc -o -A -F "${INSTALL_ARCH_DIR}/initrd"

	debug "Compressing initrd again"
	gzip "${INSTALL_ARCH_DIR}/initrd"
	chmod -w -R "${INSTALL_ARCH_DIR}"

	debug "Preseed successful"
}

regenerate_md5sums() {
	PWD=$(pwd)

	debug "Changing into extracted iso directory"
	cd "$TMP_DIR"

	debug "Adding write access to md5sum.txt"
	chmod +w md5sum.txt

	debug "Regenerating md5sums"
	find -follow -type f ! -name md5sum.txt -print0 | xargs -0 md5sum > md5sum.txt

	debug "Removing write access to md5sum.txt"
	chmod -w md5sum.txt

	debug "Changing back to original directory"
	cd "${PWD}"
}

rebuild_iso_image() {
	# Create the iso image
	debug "Creating the ISO image"
	genisoimage -o "$OUTPUT_ISO" \
		-b isolinux/isolinux.bin \
		-c isolinux/boot.cat \
		-no-emul-boot \
		-boot-load-size 4 \
		-boot-info-table \
		-r -J \
		"$TMP_DIR" > "$LOG_DIR/genisoimage.log" 2>&1

	debug "Making ISO work with USB drives"
	isohybrid "$OUTPUT_ISO"

	debug "ISO image created"
}

create_preseed_iso() {
	set -e			# Exit on error
	set +o pipefail		# Exit if a pipeline fails

	verify_empty_dir
	add_preseed_to_initrd
	rebuild_iso_image


	echo "Preseed ISO can be found at '$OUTPUT_ISO'"
}

check_iso_var
check_command 7z		# For extracting iso image
check_command genisoimage	# For recreating iso image
check_command gunzip
check_command cpio
check_command isohybrid

create_preseed_iso

