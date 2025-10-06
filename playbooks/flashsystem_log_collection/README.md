# Playbook to collect IBM FlashSystem logs

## Table of Contents
- [Objective](#objective)
- [Prerequisites](#prerequisites)
- [Playbook Overview](#playbook-overview)
- [Variables](#variables)

## Objective
  - Capture IBM FlashSystem logs (snaps and dumps) and copy them to the Ansible host.

## Prerequisites
  - IBM Storage Virtualize ansible collection version 2.2.0 or above must be installed.
  - All nodes of the cluster should share same username and password.

## Playbook Overview
- This playbook collects logs (snaps and dumps) from IBM FlashSystem.
- A directory named `log_<cluster_name>_<timestamp>` is created under user's home directory on the ansible controller to store the logs.
- Logs are validated and transferred from IBM FlashSystem nodes to the ansible controller.
- Playbook can be executed as: `ansible-playbook main.yml`

The playbook structure is as below: 
```
ibm.storage_virtualize
│
└─playbooks
  │
  └─flashsystem_log_collection
    │
    └─main.yaml
    └─README.md
    └─inventory.ini
...
```

## Variables
### These variables should be defined in your inventory.ini file,

| Parameter         | Description                                                                                                         |
|-------------------|---------------------------------------------------------------------------------------------------------------------|
| `cluster_ip`      | FQDN or IP address of the cluster.                                                                                  |
| `cluster_username`| Username for authentication.                                                                                        |
| `cluster_password`| Password for authentication.                                                                                        |
| `log_path`        | (Optional) Path on the Ansible host where playbook logs will be stored. Defaults to `/tmp/log_collection.log`.      |

## Author
- Akshada Thorat  (akshada.thorat@ibm.com)
