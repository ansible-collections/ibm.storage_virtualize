Objective:
  - Set up and configure PBRHA (3-site).

Prerequisite:
  - IBM storage Virtualize ansible collection plugins must be installed.
  - From here on, refer to highly-available site 1 as HA1, highly-available site 2 as HA2, and the disaster recovery
    site as DR1.
  - Partition-based High-availability (PBHA) must be configured between HA1 and HA2 sites. Please refer to 'PBHA'
    and 'move_existing_objects_into_PBHA_env' directories in 'playbooks' folder to configure PBHA for new and existing
    objects respectively.
  - Disaster recovery (DR) site must be in partnership with both HA1 and HA2 sites.
  - DR site must have a pool for replication.

Tasks performed via this playbook:
  - Set replication pool link uid on DR site.
  - Create Storage Partition at DR site. (Note: Existing partition can also be specified in inventory.)
  - Configure DR link to HA1's Storage Partition.
  - Create async-dr replication policy in HA1 stoarge.
  - Assign DR replication-policy to existing volumegroups.

There are total 3 files used for this use-case:
  1. main.yml:
     main.yml will configure PBRHA 3-site over existing PBHA. This is the main file to be executed as below:
     ansible-playbook main.yml -i inventory.ini

  2. inventory.ini:
     This inventory file contains following:
      - clusters: A list containing AMS system from PBHA configuration and DR site.
        - name: cluster's name
        - clustername: cluster's IP
        - username: cluster's user login name
        - password: cluster's user password
        - pool_name: Storage pool name to be used for linking
        - partition_name: Name of Storage partition being used in PBRHA

      - ha_policy_name: HA Replication policy name
      - dr_policy_name: DR Replication policy name
      - volume_group_name: List of volumegroups
      - log_path: Log path of playbook. (default: "/tmp/ansiblePBRHA.log").

    3. remove_dr_link.yml:
       remove_dr_link.yml will remove async-dr replication policy from volumgroup, removes the DR system from PBRHA setup,
       and it will remove partition used for DR-link.
Note: 
  - There are 2 relevant playbook directories as below in 'playbooks' section of this collection:
		- PBHA (for configuring new PBHA setup)
		- move_existing_objects_into_PBHA_env (for configuring PBHA for existing volumegroups)

Author: Sandip Gulab Rajbanshi (sandip.rajbanshi@ibm.com)
