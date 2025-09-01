# Host Partition Setup Notes

## Limits
1TB SSD per host

## Old Partition Table

| Name    | Size   | Utilization | Mount Point |
|---------|--------|-------------|-------------|
| sda1    | 380MB  |  7%         | /boot/efi   |
| sda2    | 1GB    | 10%         | /boot       |
| sda3    | 300GB  | 7%          | /           |
| sda4    | 32GB   | N/A         | swap        |
| sda5    | Rest   |             | LVM-Ceph    |


## Analysis of Usage

The /boot and /boot/efi seem to be the right size.
The root filesystem (/) is horribly underutilized.
100 GB seems better.  Perhaps in its own LVM,
and we could split that down into smaller partitions
if needed.

Thinking of doing a /data partition that's around 100GB
for misc data that we may want to keep locally.

I'm not going to do Ceph again. The benefits to proxmox
clustering aren't worth it in this environment, and
the performance on consumer hardware isn't great.  In
addition, I have a suspiciously high amount of drives that
are failing after a few years.

I may try ZFS replication instead.

## New partition table

This is not set in stone yet.


| Size   |  Mount Point |
|--------|--------------|
| 380MB  |  /boot/efi   |
| 1GB    |  /boot       |
| 100GB  | LVM?         |
| 100GB  | /data        |
| 32GB   |  swap        |
| 100GB       | Proxmox ZFS? |
| Rest   | Proxmox?      |


