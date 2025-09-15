# Debian Manual Install Notes

This is the notes for the manual install that we've used to get information for
the pre-seed and test the install.

Keeping this here in case we need to replicated this for a newer Debian release

## Media setup

  Copy Debian Trixie (netinstall) to a USB device (Balena-etcher under windows)

## Bios setup
  ESC or F10 for bios menu
  Virtualization on, set USB as the first boot device

## Step by step choices

  - If the disk was previously setup, wipe it
  - Select "Advanced options ..."
    - Select "Expert install" (*NOT* "Graphical expert install")
  - Choose language
    - English
    - United States
    - "United States - en\_US.UTF-8" locale
      - No additional locales
    - American English Keymap
  - Skip "Access the installer using a Braille display"
  - Configure the keyboard
    - American English
  - Detect and mount installation media
  - Load installer components from installation media
    - All defaults
  - Detect network hardware
  - Configure the network
    - (Will attempt to find link on all network adapters)
    - Note - my current hardware setup
      - Intel is the low profile NIC - shows up as enp1s0
      - Realtek is the onboard NIC - shows up as enp2s0
    - Setup whatever adapter it's plugged into
      - During testing, used onboard NIC
  - (Hostname:) debian-13-vhost
  - (Domain name:) lab.internal
  - (Set root password)
  - (Set user name and password)
  - (Set time zone)
  - Detect disks
  - Partition Disks
    - Manual
      - Partitioning
        - Select GPT partition type if prompted
        - EFI
          - Name: ESP
          - 1 GB (this is likely overkill)
          - Location for new partition: Beginning
          - Use as: EFI System Partition
          - Bootable flag: off
          - Mount point: /boot/efi
        - /boot
          - Name: BOOT
          - 1 GB
          - Location for new partition: Beginning
          - Use as: Ext4 journaling file system
          - Mount point: /boot
        - Volume group
          - Name: ROOT\_LVM
          - 120 GB
          - Location for new partition: Beginning
          - Use as: physical volume for LVM
        - Swap
          - Name: SWAP
          - 32 GB
          - Location for new partition: **End**
          - Use as: Swap area
        - Note: >850GB will be available as free space - this is for ZFS,
          which will be setup later
        - Go up to "Configure the Logical Volume Manager"
          - Write changes to disk
          - Create volume group
            - Volume group name: debian-vg
            - Select previously created partition (120000MB)
          - Create logical volume (all use the debian-vg)
            - root
              - Logical volume name: root
              - Logical volume size: 30GB
            - var
              - Logical volume name: var
              - Logical volume size: 15GB
            - var-log
              - Logical volume name: var-log
              - Logical volume size: 15GB
            - tmp
              - Logical volume name: tmp
              - Logical volume size: 5GB
          - Finish
          - Note: Space will be left over in the volume group - that's fine.
            Plenty of space is free to extend any LV as needed later
        - Configure the LVs
          - All are EXT4
          - Set mount points to /, /tmp, /var and /var/log
        - Select "Finish partitioning and write changes to disk"
          - Review, and select "Yes" to "Write the changes to disk?"
  - Install the base system
    - Kernel to install:  linux-image-amd64
      - (Doesn't really matter, proxmox will replace this)
    - Drivers
      - Generic: include all available drivers
        - Probably doesn't matter, since we are going to be installing proxmox,
          but this gives us a recovery option if we swap the ssd to a different
          machine
  - Configure the package manager
    - Use a network mirror - yes
      - https
    - Debian mirror: US
    - Default archive mirror
    - Use non-free firmware
    - Do not use non-free software (default)
    - No contrib software (default)
    - Enable source repositories in apt (default)
    - Security updates and release updates
    - No automatic updates
      - We want to update each machine one by one
  - (Popularity contest)
    - Yes (why not?)
  - Software selection
    - *Unselect*
      - Debian desktop environment
      - Gnome
    - Select
      - SSH server
  - Boot loader: Grub (most compatible)
    - Go with defaults
  - Finish the installation
  - System clock is set to UTC time
  - Remove installation media and reboot
