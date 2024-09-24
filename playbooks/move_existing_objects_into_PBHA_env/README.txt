Objective:
  - Move existing single-cluster objects into Policy-Based High Availability (PBHA) Replication environment.

Prerequisite:
  - IBM storage Virtualize ansible collection plugins must be installed.
  - Pool on secondary cluster must have enough space for data that is in source volumegroup(s) on primary cluster. Here,
    source volumegroup(s) points to volumegroup(s) that are being added into partition for high-availability.
  - Volumes must be added to volumegroup before running the playbooks.

Tasks performed via this playbook:
  - Setup mTLS
  - Setup FC partnership between 2 IO-groups
  - Create a draft partition
  - Add a new or existing volumegroup in draft partition
  - Add a new or existing host in a draft partition
  - Publish draft partition
  - Create a replication policy between IO-groups of 2 clusters
  - Assign replication policy to partition

There are total 3 files used for this use-case:
  1. main.yml:
     This is the main file to be executed as below:
     ansible-playbook main.yml -i inventory.ini
     main.yml leverages create_mTLS.yml and replication_setup.yml for completing its initialial setup tasks. After 
     that, it continues to move objects into a new partition, finally establishing high-availability between primary and
     secondary clusters.

  2. inventory.ini:
     This inventory file contains following:
      - clusters: A list containing primary cluster (from where user wants to replicate data) details as well as
        secondary cluster (where volumes will be replicated to) details. It is required if user wants to setup HA
        partitions between 2 clusters.

        - cluster_ip: cluster's IP
        - cluster_name: cluster's name
        - cluster_username: cluster's user login name
        - cluster_password: cluster's user password
        - pool_name: Storage pool name to be used for linking
        - truststore_name: Truststore name
        - io_grp: Id or name of the IO-Group used to create HA replication policy

      - host_name: FC (Fibre-channel) host to which all the volumes of volumegroup will be mapped
      - fcwwpn: List of FC WWPNs to be added to FC host
      - ha_policy_name: HA Replication policy name
      - partition_name: storage partition name
      - volume_group_name: Volume-group name
      - log_path: Log path of playbook. If not specified, logs will be generated in default file
      "/tmp/ansiblePB.debug".    

  3. create_mTLS.yml:
     This playbook sets up Mutual Transport Layer Security (mTLS) which includes generating and exporting
     certificate and creating truststore on both clusters.

  4. replication_setup.yml:
     This file links pools of both the sites and creates an HA replication policy
  
  Note:
    - When last task (i.e. assigning HA replication policy to partition) is completed, objects are replicated to
      secondary cluster's pool and data copy starts immediately from primary cluster to secondary. Time taken by
      data-synchronization is dependent on amount of data. After sync is complete, 'lspartition' output shows
      ha_status=established and link_status=synchronized.

Authors: Sumit Kumar Gupta (sumit.gupta16@ibm.com)
