# High-Level Overview

(Generated with ChatGPT - here be dragons)

## Step 1 — Prepare the Hardware

Make sure each HP t730 is ready:

16 GB RAM installed
1 TB SSD installed

Network connected (1 GbE onboard is fine)

## Optional: add a second NIC for future VM/replication traffic if desired.

Step 2 — Install Debian Trixie

Boot from the Debian Trixie installer USB.

Partition the disk as GPT  The partitions should look as follows:
- /boot/efi → 512 MB (EFI system partition)
- /boot → 1 GB (non-ZFS, ext4)
- 120 GB LVM for OS
  - / - 30 GB
  - /var - 15 GB
  - /var/log - 15 GB
  - /tmp - 5 GB
  - 55 GB free on the LVM for later issues
- 32 GB swap
- Remaining space → reserved for single ZFS pool

Install minimal Debian system, including SSH for remote management.

Make sure your system boots in UEFI mode if using /boot/efi.

# Step 3 — Prepare ZFS

Install ZFS packages on Debian:

- sudo apt update
- sudo apt install zfsutils-linux

Create the ZFS pool using the remaining space:

- sudo zpool -o ashift=12 create -f rpool /dev/sda

## Step 4 — Carve ZFS Datasets

Inside rpool, create the datasets for different purposes:

  - Datasets
    - For Proxmox
      - vms - vm disks
      - ct - containers
      - iso - isos
      - backup - backups
      - templates - container templates
    - Other
      - data - misc data

Commands:
````
zfs create -o compression=lz4 rpool/vms
zfs create -o compression=lz4 rpool/ct
zfs create -o compression=lz4 rpool/iso
zfs create -o compression=lz4 rpool/backup
zfs create -o compression=lz4 rpool/templates
zfs create -o compression=lz4 rpool/data
````
TODO: Set quotas?  Y/N?

## Step 5 — Install Proxmox

WARNING - Do not believe ChatGPT for this, look up the Proxmox Trixie guide

Add Proxmox repository to Debian:

echo "deb http://download.proxmox.com/debian/pve trixie pve-no-subscription" | sudo tee /etc/apt/sources.list.d/pve.list
wget -qO - http://download.proxmox.com/debian/proxmox-release-trixie.gpg | sudo apt-key add -
sudo apt update
sudo apt install proxmox-ve postfix open-iscsi

During install, choose the existing ZFS pool (rpool) as default storage for VM disks, or let it create its own ZFS storage.

## Step 6 — Configure Proxmox Storage

In the Proxmox web GUI:

Go to Datacenter → Storage → Add → ZFS

Point to rpool or dataset rpool/vms for VM storage.

Go to Datacenter → Storage → Add → Directory

Point to rpool/iso → ISO/template storage.

Point to rpool/data → optional backup/data storage.

Decide which VM datasets you want replicated. Proxmox will handle snapshots and incremental sends automatically.

## Step 7 — Optional Tuning

*FIXME* We want 4GB, not 6GB.  LLM is being silly again

ARC memory cap (to avoid starving your 16 GB RAM):

echo "options zfs zfs_arc_max=6442450944" | sudo tee /etc/modprobe.d/zfs.conf
sudo update-initramfs -u

This caps ARC at ~6 GB.

## Step 8 — Start Using the Cluster

Create VMs/CTs and assign storage to ZFS datasets.

Upload ISO images to rpool/isos.

Add replication jobs for selected VMs to other nodes in the cluster.

Use /rpool/data for backups, logs, or extra storage.
