# Automated Firmware Upgrade of IBM FlashSystem Using Ansible Playbook

This document explains the Ansible playbook required for upgrading IBM FlashSystem firmware. The playbooks are designed to automate the upgrade process, ensuring a smooth and efficient transition to the latest software version.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Overview](#overview)
- [Variables](#variables)

## Prerequisites
- IBM Storage Virtualize Ansible Collection must be installed.
- The pexpect `package` must be installed in the execution environment.
- The latest Upgrade Test Utility should be downloaded from the IBM Fix Central site. (https://www.ibm.com/support/fixcentral/)
- The desired firmware version must be downloaded from IBM Support website.

## Overview

The playbook to upgrade IBM FlashSystem firmware performs the following steps:
- Copies the Upgrade Test Utility to the system.
- Verifies whether system can be upgraded to desired firmware update from current firmware level.
- Copies the firmware upgrade package to the system.
- Updates the firmware.
- Ensure firmware upgrade is successful.

The playbook structure is as below: 
```
ibm.storage_virtualize
│
└─playbooks
  │
  └─firmware_upgrade
    │
    └─main.yaml
    └─README.md
    └─inventory.ini
...
```

## Variables
### These variables should be defined in inventory.ini file


| Variable                   | Notes                                                                                 |
|----------------------------|---------------------------------------------------------------------------------------|
| clustername                | Cluster's FQDN or cluster IP address                                                  |
| username                   | Username for the system                                                               |
| password                   | Password for the system                                                               |
| firmware_package_src_path  | Path of the downloaded firmware package on the Ansible controller                     |
| firmware_version_number    | Version of the firmware package to be installed on the system                         |
| upgrade_test_util_src_path | Path of the downloaded Upgrade Test Utility on the Ansible controller                 |
| poll_period                | Polling period in seconds for checking the upgrade status (default: 900 seconds)      |
| poll_retries               | Number of retries for checking the upgrade status (default: 30 retries)               |

**Example inventory.ini File**  
Here is an example inventory.ini file that demonstrates how to configure the variables:
```
clustername: X.X.X.X
username: username1234
password: password1234
firmware_package_src_path: /Users/IBM_FlashSystem_NVMe_INSTALL_8.7.3.2.tgz.gpg
firmware_version_number: 8.7.3.2
upgrade_test_util_src_path: /Users/IBM_INSTALL_FROM_8.5_AND_LATER_upgradetest_46.14
```

> [!CAUTION]
> If the `Run svcupgradetest utility` task fails due to upgrade readiness issues (errors or warnings), the playbook will stop with a clear error message.
> 
> To proceed despite these warnings, please set the `ignore_errors` to true in the `Run svcupgradetest utility` task and re-run the playbook.
> 
> ```yaml
> ignore_errors: true 
> ```

> [!IMPORTANT] 
> The playbook uses SCP to transfer the firmware package to the FlashSystem. If Ansible controller supports SFTP, remove the `-O` flag before running the playbook.

## Authors

- Sumit Kumar Gupta (SUMIT.GUPTA16@ibm.com)
- Aditya Bhosale (adityabhosale@ibm.com)
- Prathamesh Deshpande (prathamesh.deshpande1@ibm.com)
