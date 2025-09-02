# Debian Manual Install Notes

This is the notes for the manual install that we've used to get information for
the pre-seed and test the install.

## Media setup

  Copy Debian Trixie (netinstall) to a USB device (Balena-etcher under windows)

## Bios setup
  ESC or F10 for bios menu
  Virtualization on, set USB as the first boot device

## Step by step choices

  - If the disk was previously setup, wipe it
  - Select Install (not Graphical Install)
  - (Localization)
    - English
    - United States
    - American English Keymap
  - (Network)
    - (Will attempt to find link on all network adapters)
    - Setup whatever adapter it's plugged into
      - During testing, used wifi adapter
  - (Hostname:) debian-13-host
  - (Domain name:) lab.internal
  - (Set root password)
  - (Set user name and password)
  - (Set time zone)
  - Partitioning
    - EFI
      - 512 MB (? - Verify this, it may create 1 GB)
      - Location for new partition: Beginning
      - Use as: EFI System Partition
      - Bootable flag: off
    - /boot
      - 1 GB
      - Location for new partition: Beginning
      - Use as: Ext4 journaling file system
      - Mount point: /boot
    - Volume group
      - 120 GB
      - Location for new partition: Beginning
      - Use as: physical volume for LVM
    - Swap
      - 32 GB
      - Location for new partition: End
      - Use as: Swap area
  - Configure the LVM
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
  - Configure the LVs
    - All are EXT4
    - Set mount points to /, /tmp, /var and /var/log
  - (Package manager)
    - Debian mirror: US
    - Default archive mirror
  - (Popularity contest)
    - Yes (why not?)
  - Software selection
    - *Unselect*
      - Debian desktop environment
      - Gnome
    - Select
      - SSH server
