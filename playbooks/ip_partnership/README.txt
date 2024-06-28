Objective:
Configure IP Partnership and create multiple Remote Copy replationships along with volumes in an easy way.

Prerequisite:
- IBM storage Virtualize ansible collection plugins must be installed

These playbooks creates IP partnership and Remote copy relationships between a primary cluster and the secondary cluster.
  - It uses storage virtualize ansible modules.
  - The playbook is designed to create IP partnership between source cluster to destination cluster. It takes the input IPs and portset details and configures theIP Partnership, if portset details are missing then it automatically fetches the it for the input IPs and create the partnership.
  - These playbooks also create multiple Remote copy relationships (Metro Mirror, Global Mirro, Global Mirror with Change Volume).


There are total 3 files used for this use-case.
  1. ip_partnership_vars:
     This file has all the variables required for playbooks.
         - primary_cluster*     : Parameters starting with primary_cluster contain primary cluster details from where user wants to replicate data.
         - secondary_cluster*   : Parameters starting with secondary_cluster contain secondary cluster details to where volume will be replicated to
         - linkbandwidthmbits   : It is the aggregate bandwidth of the replication link between primary and secondary clusters. If its not specified then the default value would be 100.
         - backgroundcopyrate   : It is the maximum percentage of aggregate replication link bandwidth that can be used for bacground copy operations. If its not specifed then the default value would be 50.
         - compressed           : It ensures f compression should be enabled or not for replication between clusters. The default value is no.
         - primary_link*	: Parameters starting with primary_link contain primary cluster link details such as IPs, portsets. 
         - secondary_link* 	: Parameters starting with secondary_link contain secondary cluster link details such as IPs, portsets.
	 - vdisk* 		: Parameters starting vdisk contain details for vdisk such as name prefix and size for the vdisks to be created.
  	 - num_of_GMCVrel, num_of_MMrel, num_of_GMrel	: It is the number of Global Mirror with Change volume (GMCV), Metro Mirror (MM) or Globa Mirro (GM) relations to be created between clusters.
	 - changeVolprefix	: It is the prefix for change volumes which will be creaed for GMCV relations only.
	 - host_name		: It is the host name to which all the volumes should be mapped after creation. It assumes Host Ips are already assigned and host is already created on both clusters and are logged in.

  2. create_partnership:
     This playbook creates the IP partnership between primary and secondary clusters using input IPs & portset details. Incase portset detail is not provided, then it fetches the portste values of input IPs and creates the partnership. It keeps backgroundcopy as 50 and linkbandwidthmbits as 100 default values if not provided by user
  
  3. create_MM_relationships:
     This playbook creates the Metro mirror relationships for the partnership configured using above playbook "create_partnership" or on an existing partnership. This playbook creates associated vdisks with vdisk_prefix name specified in inventroy file ip_partnership_vars. It also maps all the vdisks to specified host.

  4. create_GM_relationships:
     This playbook creates the Global mirror relationships for the partnership configured using above playbook "create_partnership" or on an existing partnership. This playbook creates associated vdisks with vdisk_prefix name specified in inventroy file ip_partnership_vars. It also maps all the vdisks to specified host.

  5. create_GMCV_relationships:
     This playbook creates the Global mirror change volume relationships for the partnership configured using above playbook "create_partnership" or on an existing partnership. This playbook creates associated vdisks with vdisk_prefix name and change volumes with changeVolprefix name specified in inventroy file ip_partnership_vars. It also maps all the vdisks to specified host.

 Authors: Aakanksha Mathur (aamathur@in.ibm.com)
          Akshada Thorat  (akshada.thorat@ibm.com)
          Aditi Pande (aditi.pande1@ibm.com)
          Hencilla DSouza (hencilla.dsouza@ibm.com)
