# Automation of Fibre Channel Zoning for Cisco Switches


## Table of Contents

- [Objective](#objective)
- [Prerequisites](#prerequisites)
- [Variables](#variables)
- [Playbook Overview](#playbook-overview)
- [Sample Playbook Usage](#sample-playbook-usage)
- [Authors](#authors)

## Objective

Automate and synchronize Fibre Channel zoning on Cisco SAN switches using zone data defined under `lshostzone` on IBM FlashSystem clusters.

## Prerequisites

- Controller Requirements:
    - Python version 3.10 or later.
    - Install **Ansible** (*v2.16* or later)
    - Install **IBM Storage Virtualize Ansible Collection**:  
        ```bash
        ansible-galaxy collection install ibm.storage_virtualize
        ```  
    - Install **Cisco NX-OS Ansible Collection**:  
        ```bash
        ansible-galaxy collection install cisco.nxos
        ```  
    - Install Python dependency: **ansible-pylibssh**:  
        ```bash
        pip install ansible-pylibssh
        ```  
- IBM FlashSystem (*v9.1.2* or later)

- Switch Requirements:
    - Cisco MDS switch running NX-OS
    - NX-OS version 8.4(1) or later

## Variables

  - **inventory.ini** - Defines the FlashSystem clusters and Cisco switches managed by the playbook.
  ```ini
    ; Inventory File - inventory.ini
    [clusters]
    cluster1 ansible_host=x.x.x.x ansible_user=username ansible_password=password
    cluster2 ansible_host=x.x.x.x ansible_user=username ansible_password=password

    [switches]
    switch1 ansible_host=x.x.x.x ansible_user=username ansible_password=password
    switch2 ansible_host=x.x.x.x ansible_user=username ansible_password=password
  ```

## Playbook Overview

The automation consists of two playbooks:

### 1. main.yaml:
  - Entry point for execution. 
  - Run using:
     ```bash
     ansible-playbook main.yaml -i inventory.ini
     ```  
  - Target group: **clusters**
  - Collects all required data from the clusters.
  - Invokes **cisco_zone_sync.yaml** to apply zoning on the switches

### 2. cisco_zone_sync.yaml:
  - Target group: **switches**
  - Generates zone configurations based on the collected cluster data.
  - Pushes the generated zone configurations to the Cisco switches.

## Sample Playbook Usage
- On the FlashSystem cluster, create an FC portset with auto-zoning enabled:
  ```yaml
  - name: Create a portset
    ibm.storage_virtualize.ibm_svctask_command:
      command: "svctask mkportset -name {{ portset_name }} -porttype fc -autozoneenabled yes"
      clustername: "{{ clustername }}"
      username: "{{ username }}"
      password: "{{ password }}"
  ```
- Associate FlashSystem Fibre Channel I/O port ID that will be used for host connectivity to this portset.
  ```yaml
  - name: Add port ID to the portset
    ibm.storage_virtualize.ibm_svctask_command:
      command: "svctask addfcportsetmember -portset {{ portset_name }} -fcioportid {{ fcioportid }} -ignoreautozoneincapable"
      clustername: "{{ clustername }}"
      username: "{{ username }}"
      password: "{{ password }}"
  ```
> [!NOTE]
> Ensure the `ignoreautozoneincapable` flag is used when adding ports.
- Map this portset to the host object.
  ```yaml
  - name: Create a host and map to portset
    ibm.storage_virtualize.ibm_svctask_command:
      command: "svctask mkhost -fcwwpn {{ fcwwpn }} -portset {{ portset_name }}"
      clustername: "{{ clustername }}"
      username: "{{ username }}"
      password: "{{ password }}"
  ```
- On the controller, navigate to the playbook directory and update `inventory.ini` with the FlashSystem and Cisco switch credentials.
- Run the playbook:
  ```bash
  ansible-playbook main.yaml -i inventory.ini
  ```
- The playbook creates Fibre Channel zones based on the configuration reported by the `lshostzone` command on the FlashSystem.
- If the configuration changes, rerun the playbook to synchronize the zones with the updated configuration.

## Authors

- Om Dhumal (om.d@ibm.com)
- Pravin Mahajan (pravimah@in.ibm.com)
