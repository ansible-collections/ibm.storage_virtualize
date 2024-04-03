Objective:
Set up mTLS and configure Policy Based Replication.

Prerequisite:
- IBM storage Virtualize ansible collection plugins must be installed

These playbook set up mTLS and configure Policy Based Replication between a primary cluster and the secondary cluster.
  - It uses storage virtualize ansible modules.
  - This playbook is designed to set up mTLS on both the site and configure Policy Based Replication between source cluster to destination cluster. This is designed in a way that it creates Data Reduction Pool , links them, creates provision policy and replication policy 
  - These playbooks also creates multiple Volumes with specified prefix along with volume group and maps all of them to the specified host.

There are total 4 files used for this use-case.
  1. PBR_variable.txt:
     This file has all the variables required for playbooks.
         - user_data            : Parameters contain primary cluster details from where user wants to replicate data as well as secondary cluster details to where volume will be replicated to.
         - host_name		: It is the host name to which all the volumes should be mapped after creation. It assumes  host is already created on primary clusters. 
	 - volume* 		: Parameters starting volume contain details for volume such as name prefix for volume  and size for the volumes to be created.It also has a volume group name
  	 - number_of_volumes	: It is the number of volumes to be created between clusters.
         -  log_path            : It specifies the log path of playbook. If not specified then logs will generate at default path ‘/tmp/ansiblePB.debug’


  2. Create_mTLS.yml:
     This playbook sets mTLS (Mutual Transport Layer Security) which includes ceritficate generation on individual cluster, export it to remote location , creates certificate truststore which contains the certificate bundle. This operation performed on primary as well as secondary site. This playbook is called under  'Create_PBR_config.yml'.

  3. Create_mdiskgrp_drp_proviPolicy.yml:
      This playbook check the drive status , drive count based on that it creates mdiskgrp, Data reduction Pool with specified level. It links pool of both the site. It creates provision policy, replication policy.This playbook is called under  'Create_PBR_config.yml'.
     

  4. Create_PBR_config.yml:
     This is main playbook file user need to execute only this playbook it leaverages rest of the 3 files. 
     It  execute 2 playbooks like 'Create_mTLS.yml' and 'Create_mdiskgrp_drp_proviPolicy.yml' and later on this the playbook creates voulme group and associated volumes with volume_prefix name specified in inventroy file ‘PBR_variable.txt’. It also maps all the volumes to specified host.
    After first execution of this playbook for next execution we can add volumes on existing/new volume group with existing replication policy and provision policy . It mapped this newly added volumes to the existing host object.

 Authors: Akshada Thorat  (akshada.thorat@ibm.com)
