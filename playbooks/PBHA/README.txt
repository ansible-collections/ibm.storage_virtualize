Objective:
  - Set up Policy Based High Availability (PBHA) Replication.

Prerequisite:
  - IBM storage Virtualize ansible collection plugins must be installed.
  - FC partnership must be present between the clusters.
  
This playbook is designed to set up and configure PBHA Replication between a source cluster and destination cluster.
  - It uses storage virtualize ansible modules.
  - This playbook is designed to set up and configure PBHA Replication between source cluster to destination cluster. This is designed in a way that it creates Data Reduction Pool, links them, creates provisionining policy. 
  - These playbooks also create multiple volumes with specified prefix, along with volume group, and maps all of them to the specified host.

There are total 3 files used for this use-case.
  1. main.yml:
     This is the main file to be executed as below:
     ansible-playbook main.yml -i inventory.ini
     main.yml leverages other files for PBHA configuration. It executes playbook like "Create_mdiskgrp_provisioningpolicy.yml" and later on, this playbook creates partition, volume group and associated volumes with volume_prefix name specified in inventory file "inevntory.ini". It also maps all the volumes to specified host.

  2. inventory.ini:
     This inventory file has following:
      - users_data: Parameters contain primary cluster (from where user wants to replicate data) details as well as secondary cluster to (where volumes will be replicated to) details.
      - host_name: It is the FC host name to which all the volumes should be mapped after creation. 
      - fcwwpn: Specifies a list of Fibre Channel (FC) WWPNs to be added to FC host.
      - pool_name: It is the name of a storage pool to be created.
      - provisioning_policy_name: It is the name of provisioning policy to be created and added to storage pool.
      - mdisk_name: It is the name of array to be created and adding it to storage pool.
      - level: Specifies the RAID level for the array that is being created.
      - drivecount: Specifies the number of the drives.
      refer the below link for RAID level combinations.
      https://www.ibm.com/docs/en/flashsystem-5x00/8.7.x?topic=commands-mkdistributedarray
      - ha_policy_name: It is the name of HA Replication policy to be created.
      - partition_name: It is the name of a storage partition to be created.
      - volume: Parameters starting volume contain details for volume such as name prefix for volume and size for the volumes to be created.It also has a volumegroup name.
      - number_of_volumes: It is the number of volumes to be created.
      - log_path: It specifies the log path of playbook. If not specified, logs will be generated in default file "/tmp/ansiblePB.debug".    

  3. create_mdiskgrp_provisioning_policy.yml:
      This playbook checks the drive status and drive count. Based on this drive info, it creates mdiskgrp, and data reduction pool with specified level. It links pools of both the sites. Then, it creates provisioning policy.

Authors: Lavanya C R (lavanya.c.r1@ibm.com)
         Sandip Rajbanshi (sandip.rajbanshi@ibm.com)
         
 