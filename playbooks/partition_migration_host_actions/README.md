# Automated Host-Side Actions for Partition Migration

## Table of Contents

- [Objective](#objective)
- [Prerequisites](#prerequisites)
- [Playbooks](#playbooks)
- [Configuration](#configuration)
  - [Inventory](#inventory)
  - [Variables](#variables)
- [How It Works](#how-it-works)
- [Ansible Logging](#ansible-logging)
- [Extending to New Operating Systems](#extending-to-new-operating-systems)
- [Authors](#authors)


## Objective

This Ansible playbook suite automates **host-side actions** required while migrating storage partitions from one IBM FlashSystem to another.
It continuously monitors partition migration events on the FlashSystems and performs the appropriate actions on mapped hosts (Linux / Windows) to ensure paths are properly discovered, rescan, and validated before commit or rollback.

## Prerequisites

### Controller Requirements

- IBM Storage Virtualize Ansible Collection plugins **v2.7.4 or above** must be installed.
- The Ansible controller machine must have **Python 3.10+**.

### Target Host Requirements

#### Common

- All remote hosts must have **Python 3.8+**.
- Ensure:
  - **Zoning** is present between the host and the **target FlashSystem** (for FC).
  - **IP connectivity** is available between the host and the **iSCSI target** (for iSCSI).

#### Windows Hosts

- Must have either:
  - `sshpass`, or  
  - `winRM` utility installed.
- SSH access must be set up between the Windows host and the Ansible controller.
- Playbooks use **PowerShell** and require **Administrator** privileges.
- **Microsoft iSCSI Initiator Service** must be installed and running.

#### Linux Hosts

- `rescan-scsi-bus.sh` (package `scsitools`) installed.
- Multipath utilities (e.g. `multipath`, `multipathd`) installed and configured.
- Playbooks use `rescan-scsi-bus.sh`, which requires **root** privileges.
- `iscsiadm` installed and available in `PATH`.

### FlashSystem Requirements

- **iSCSI**
  - Host-type **portset** must be configured with data IPs.
  - The user can either:
    - Provide specific IPs in `inventory.ini`, or
    - Let the playbook perform discovery/login on **all IPs** present in the portset.
- **FC**
  - No specific requirement other than correct **zoning**.

> [!NOTE]
> - The playbooks **do not** create portsets or assign IPs to portsets.
> - The same framework supports hosts using **FC**, **iSCSI**, or **both**.

## Playbooks

The main files in this directory are:

- `main.yml`  
  Entry-point playbook. Monitors partition migrations and orchestrates all other playbooks.
  Usage: ```ansible-playbook main.yml -i inventory.ini```

- `inventory.ini`  
  Defines:
  - `application_server` (or other host groups): hosts mapped to FlashSystems
  - `flash_systems`: FlashSystems to monitor for migration events

- `vars.yml`  
  User-tunable parameters controlling behavior (min paths, deployment type, inventory path, log path, etc.).

- `host_identification.yml`  
  Identifies hosts mapped to a migrating partition, and determines OS (Linux / Windows / others).

- `discover_multipath_devices.yml`  
  Performs device and multipath discovery (e.g. iSCSI login, SCSI rescan, multipath detection) on target hosts.

- `rescan_multipath_devices.yml`  
  Handles `host_rescan_requested` events by rescanning devices and refreshing multipath information on mapped hosts.

- `verify_multipath_devices.yml`  
  For `commit_or_rollback` events, verifies active path counts per device and per node, and checks compliance with `min_active_path`.  
  > Currently supports **Linux** only.

- `iscsi_logout.yml`  
  Handles iSCSI logout actions for appropriate scenarios (e.g. cleanup after migration / rollback).

- `test_and_rescan_hosts.yml`  
  Helper playbook to test connectivity and perform host-side rescans where needed.

## Configuration

### Inventory

`inventory.ini` defines the hosts and FlashSystems with their access credentials.

#### Example – FC

```
[application_server]
linux1 ansible_host=x.x.x.x ansible_user=root ansible_ssh_pass=password ansible_connection=ssh
windows1 ansible_host=x.x.x.x ansible_user=Administrator ansible_ssh_pass=password ansible_connection=ssh ansible_shell_type=cmd

[flash_systems]
fs1 ansible_host=x.x.x.x ansible_user=superuser ansible_password=password
fs2 ansible_host=x.x.x.x ansible_user=superuser ansible_password=password
```

#### Example – iSCSI
```
[application_server]
win1   ansible_host=x.x.x.x ansible_user=admin ansible_ssh_pass=password ansible_connection=ssh ansible_shell_type=cmd ansible_iscsi_ips='["x.x.x.x","x.x.x.x"]'
linux1 ansible_host=x.x.x.x ansible_user=root  ansible_ssh_pass=password ansible_connection=ssh ansible_iscsi_ips='["x.x.x.x","x.x.x.x"]'
linux2 ansible_host=x.x.x.x ansible_user=root  ansible_ssh_pass=password ansible_connection=ssh

[flash_systems]
fs1 ansible_host=x.x.x.x ansible_user=superuser ansible_password=password
fs2 ansible_host=x.x.x.x ansible_user=superuser ansible_password=password
```

### Variables

All user-configurable parameters are defined in vars.yml:
| Parameter            | Description                                                                                             |
| -------------------- | --------------------------------------------------------------------------------------------------------|
| `min_active_path`    | Minimum required active paths per node-to-host for all devices. Use 0 to skip auto commit of migration. |
| `hosts_name`         | Host group name from `inventory.ini` (e.g., `application_server` or `localhost`)                        |
| `deployment_type`    | `1`: Localhost; `2`: Ansible Tower  (or other central controller).                                      |
| `io_stability_time`  | Wait time (in seconds) to ensure I/O stability before validation/commit.                                |
| `inventory_file`     | Path to the inventory file (e.g. inventory.ini).                                                        |
| `logpath`            | Path to store log files (update logrotate configuration if using a custom directory).                   |
| `temp_file_location` | Directory to store temporary files during script execution.                                             |
  
  
## How It Works

These playbooks monitor partition migration status on FlashSystems and trigger host-side actions to keep paths consistent and compliant.

>[!NOTE]
>The framework supports at least the following migration events:
> - `host_rescan_requested`
> - `commit_or_rollback`

>[!WARNING]
>The solution uses rescan-scsi-bus.sh on Linux.
>This can impact I/O for other volumes mapped to the same host.
>Carefully choose when to run the playbook (e.g. outside critical peak load).

### Event Handling Workflow

Monitoring / Dispatch (main.yml)-
Continuously queries FlashSystems for active partition migrations.
Identifies migration events and mapped hosts using host_identification.yml.
For each event, dispatches the appropriate helper playbook.

host_rescan_requested-
Triggers rescan_multipath_devices.yml on the identified hosts.
Performs device / SCSI rescan and multipath refresh.
Retries up to 5 times if rescan validation fails (configurable via vars if required).

commit_or_rollback-
Triggers verify_multipath_devices.yml on Linux hosts.
Verifies path counts per device, per node.
Compares results against min_active_path configured in vars.yml.
If all devices are compliant and min_active_path > 0:
The playbook can auto-commit the migration on FlashSystem.

If validation fails:
The partition migration is not auto-committed, and details are logged for manual inspection.
Skip Conditions for commit_or_rollback
The commit_or_rollback event will be skipped if any of the following is true:
Deployment type is set to 1 (localhost) but the partition has multiple hosts mapped.
The number of detected hosts on FlashSystem does not match the hosts defined in the inventory.
The partition includes hosts with unsupported operating systems.
No host is mapped to the migrating partition.

>[!NOTE]
>By default, auto-commit is disabled by setting min_active_path = 0.
>Fixing commit_or_rollback events and auto-committing will delete the partition from the source copy.

Monitor:
Ansible output for event handling and decisions.
Logs written to the configured logpath (if any).

## Ansible Logging
To enable Ansible logging, set the following environment variable on the controller:
```
export ANSIBLE_LOG_PATH=/var/log/ansible.log
```
You can customize the path if needed; ensure the directory exists and has appropriate permissions.

## Extending to New Operating Systems
To support additional operating systems, add OS-specific blocks to the following playbooks:
- host_identification.yml
  - Currently supports Linux and Windows.
  - For a new OS, ensure it can be identified (e.g. via facts or custom conditions).
  - Provide host identifiers in the desired format, for example:

    FC Example
    ```
    fc_host_wwpns_upper: [
      "10000090FAA0B824",
      "10000090FAA0B825"
    ]
    ```

    iSCSI Example
    ```
    iscsi_ips: [
      "10.10.10.14",
      "10.10.10.15",
      "10.10.10.16",
      "10.10.10.17"
    ]
    iscsi_name: [
      "iqn.1994-05.com.redhat:529611838e5d"
    ]
    ```

- rescan_multipath_devices.yml
  - Currently supports Linux and Windows.
  - For new OS types, provide:
    - Rescan CLI path, or
    - The rescan method/commands required for that OS.

- verify_multipath_devices.yml
  - Currently supports Linux.
  - For a new OS, ensure the script produces (or can convert to) output in the following format:

    ```
    {
      "data": [
        {
          "active_paths_on_tgt": {
            "dm-0": {
              "node1": {
                "active_no_paths": 2,
                "inactive_no_paths": 0
              },
              "node2": {
                "active_no_paths": 2,
                "inactive_no_paths": 0
              },
              "uuid": "(36005076810da8186b80000000000006e)"
            },
            "dm-1": {
              "node1": {
                "active_no_paths": 2,
                "inactive_no_paths": 0
              },
              "node2": {
                "active_no_paths": 2,
                "inactive_no_paths": 0
              },
              "uuid": "(36005076810da8186b80000000000006f)"
            },
            "inventory_name": "linux1"
          },
          "non_compliant_devices": []
        }
      ]
    }
    ```
    The verification logic expects this structure when evaluating compliance with min_active_path.

## Authors

- Prateek Mandge (prateekmandge@ibm.com)
- Mohit Chitlange (mochitla@in.ibm.com)
- Ashwin Joshi (ashjosh1@in.ibm.com)
- Chetan Borkar (chetan.borkar@ibm.com)
- Sumit Kumar Gupta (sumit.gupta16@ibm.com)
- Aditya Bhosale (adityabhosale@ibm.com)