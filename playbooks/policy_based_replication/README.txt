Objective:
  - Set up mTLS and configure Policy Based Replication.

Prerequisite:
  - IBM storage Virtualize ansible collection plugins must be installed.
  - Partnership(FC/IP) must be present between the clusters.
  - Host must be present on primary cluster.

These playbooks set up mTLS and configure Policy Based Replication between a primary cluster and the secondary cluster.
  - It uses storage virtualize ansible modules.
  - This playbook is designed to set up mTLS on both the site and configure Policy Based Replication between source cluster to destination cluster. This is designed in a way that it creates Data Reduction Pool, links them, creates provision policy and replication policy. 
  - These playbooks also creates multiple Volumes with specified prefix along with volume group and maps all of them to the specified host.

There are total 4 files used for this use-case.
  1. main.yml:
     This is the main file to be executed as below:
     ansible-playbook main.yml -i pbr_inventory.ini
     main.yml leverages other files for PBR configuration. It executes "create_mTLS.yml" and "drp_pool_setup.yml" and then creates volume group and associated volumes with volume_prefix name, specified in "pbr_inventory.ini". It also maps all the volumes to specified host.
     Any additional volumes that need to be added to volumegroup, and/or need to be mapped to existing host object (but were not part of volumegroup at the time of execution of the playbook), can be added to inventory file. They'll be added to volumegroup and mapped to host in subsequent execution of the playbook.

  2. pbr_inventory.ini:
     This file has all the variables required for playbooks.
      - users_data: Parameters contain primary cluster details from where user wants to replicate data as well as secondary cluster details to where volume will be replicated to.
      - host_name: It is the host name to which all the volumes should be mapped after creation. It assumes host is already created on primary clusters.
      - volume*: Parameters starting volume contain details for volume such as name prefix for volume and size for the volumes to be created.It also has a volumegroup name.
      - number_of_volumes: It is the number of volumes to be created between clusters.
      - log_path: It specifies the log path of playbook. If not specified then logs will generate at default path "/tmp/ansiblePB.debug".

  3. create_mTLS.yml:
     This playbook sets Mutual Transport Layer Security (mTLS) which includes generating and exporting certificate and creating truststore on both clusters.

  4. drp_pool_setup.yml:
      This playbook checks the drive status and drive count. Based on this drive info, it creates mdiskgrp, and data reduction pool with specified level. It links pools of both the sites. Then, it creates provisioning policy and replication policy. Already exiting mdiskgrps (pools) can also be used, only mention name of desired pool in pbr_inventory.ini
      If user wants to decide drives to be used in pool before running the playbook, he can create a pool and add drives to it (example below):
      Create a pool:
      mkmdiskgrp -unit mb -datareduction yes -easytier auto -encrypt no -ext 1024 -gui -guiid 0 -name mdg0-warning 80%
      Assign first 2 disks  (via drivecount parameter) to pool:
      svctask mkdistributedarray -level raid1 -driveclass 0 -drivecount 2 mdg0 (used drive 0 and drive 1) 

Authors: Akshada Thorat  (akshada.thorat@ibm.com)
         Sandip Rajbanshi (sandip.rajbanshi@ibm.com)
         Lavanya C R (lavanya.c.r1@ibm.com)
