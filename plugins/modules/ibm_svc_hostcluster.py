#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2021 IBM CORPORATION
# Author(s): Shilpi Jain <shilpi.jain1@ibm.com>
#            Lavanya C R <lavanya.c.r1@ibm.com>
#            Sandip Gulab Rajbanshi <sandip.rajbanshi@ibm.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: ibm_svc_hostcluster
short_description: This module manages host cluster on IBM Storage Virtualize family systems
version_added: "1.5.0"
description:
  - Ansible interface to manage 'mkhostcluster', 'chhostcluster' and 'rmhostcluster' host commands.
options:
    name:
        description:
            - Specifies a name or label for the new host cluster object.
        required: true
        type: str
    state:
        description:
            - Creates (C(present)) or removes (C(absent)) a host cluster.
        choices: [ absent, present ]
        required: true
        type: str
    clustername:
        description:
            - The hostname or management IP of the Storage Virtualize system.
        required: true
        type: str
    domain:
        description:
            - Domain for the Storage Virtualize system.
            - Valid when hostname is used for the parameter I(clustername).
        type: str
    username:
        description:
            - REST API username for the Storage Virtualize system.
            - The parameters I(username) and I(password) are required if not using I(token) to authenticate a user.
        type: str
    password:
        description:
            - REST API password for the Storage Virtualize system.
            - The parameters I(username) and I(password) are required if not using I(token) to authenticate a user.
        type: str
    token:
        description:
            - The authentication token to verify a user on the Storage Virtualize system.
            - To generate a token, use the M(ibm.storage_virtualize.ibm_svc_auth) module.
        type: str
    ownershipgroup:
        description:
            - The name of the ownership group to which the host cluster object is being added.
            - Parameters I(ownershipgroup) and I(noownershipgroup) are mutually exclusive.
            - Applies when I(state=present).
        type: str
        version_added: '1.6.0'
    noownershipgroup:
        description:
            - If specified True, the host cluster object is removed from the ownership group to which it belongs.
            - Parameters I(ownershipgroup) and I(noownershipgroup) are mutually exclusive.
            - Applies when I(state=present) to modify an existing hostcluster.
        type: bool
        version_added: '1.6.0'
    removeallhosts:
        description:
            - Specifies that all hosts in the host cluster and the associated host cluster object be deleted.
            - Applies when I(state=absent), to delete a host cluster with all its hosts.
            - Parameters I(removeallhosts) and I(removemappings) are mutually exclusive.
        type: bool
    site:
        description:
            - Specifies the site name of the all hosts in the hostcluster.
            - Valid when I(state=present), to modify an existing hostcluster.
        type: str
        version_added: '2.7.0'
    partition:
        description:
            - Specifies the partition or draft partition name in which user wants to create the hostcluster.
            - Valid when I(state=present), to create and modify an existing hostcluster.
        type: str
        version_added: '3.0.0'
    removemappings:
        description:
            - Removes specified mappings from the hostcluster.
            - Valid when I(state=absent), to delete a hostcluster.
            - If specified as true, removes all the host-to-volume mappings.
            - If specified as false, keeps the host-to-volume mappings (works as keepmappings).
            - Parameters I(removeallhosts) and I(removemappings) are mutually exclusive.
        type: bool
        version_added: '3.0.0'
    log_path:
        description:
            - Path of debug log file.
        type: str
    validate_certs:
        description:
            - Validates certification.
        default: false
        type: bool
author:
    - Shilpi Jain (@Shilpi-J)
    - Lavanya C R (@lavanyacr)
    - Sandip Gulab Rajbanshi (@Sandip-Rajbanshi)
notes:
    - This module supports C(check_mode).
'''

EXAMPLES = '''
- name: Define a new host cluster
  ibm.storage_virtualize.ibm_svc_hostcluster:
    clustername: "{{ clustername }}"
    domain: "{{ domain }}"
    username: "{{ username }}"
    password: "{{ password }}"
    log_path: /tmp/playbook.debug
    name: hostcluster0
    state: present
    ownershipgroup: group1
- name: Define a new host cluster with partition
  ibm.storage_virtualize.ibm_svc_hostcluster:
    clustername: "{{ clustername }}"
    domain: "{{ domain }}"
    username: "{{ username }}"
    password: "{{ password }}"
    log_path: /tmp/playbook.debug
    name: hostcluster0
    state: present
    partition: partition1
- name: Update the ownershipgroup of a host cluster
  ibm.storage_virtualize.ibm_svc_hostcluster:
    clustername: "{{ clustername }}"
    domain: "{{ domain }}"
    username: "{{ username }}"
    password: "{{ password }}"
    log_path: /tmp/playbook.debug
    name: hostcluster0
    state: present
    noownershipgroup: 'True'
- name: Update the draftpartition of a host cluster
  ibm.storage_virtualize.ibm_svc_hostcluster:
    clustername: "{{ clustername }}"
    domain: "{{ domain }}"
    username: "{{ username }}"
    password: "{{ password }}"
    log_path: /tmp/playbook.debug
    name: hostcluster0
    state: present
    partition: draft_ptn
- name: Delete a host cluster
  ibm.storage_virtualize.ibm_svc_hostcluster:
    clustername: "{{ clustername }}"
    domain: "{{ domain }}"
    username: "{{ username }}"
    password: "{{ password }}"
    log_path: /tmp/playbook.debug
    name: hostcluster0
    state: absent
    removeallhosts: 'True'
'''

RETURN = '''#'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi, svc_argument_spec, get_logger
from ansible.module_utils._text import to_native


class IBMSVChostcluster(object):
    def __init__(self):
        argument_spec = svc_argument_spec()

        argument_spec.update(
            dict(
                name=dict(type='str', required=True),
                state=dict(type='str', required=True, choices=['absent', 'present']),
                ownershipgroup=dict(type='str'),
                noownershipgroup=dict(type='bool'),
                removeallhosts=dict(type='bool'),
                site=dict(type='str'),
                partition=dict(type='str'),
                removemappings=dict(type='bool'),
            )
        )

        self.changed = ""

        self.module = AnsibleModule(argument_spec=argument_spec,
                                    supports_check_mode=True)

        # logging setup
        log_path = self.module.params['log_path']
        log = get_logger(self.__class__.__name__, log_path)
        self.log = log.info

        # Required
        self.name = self.module.params['name']
        self.state = self.module.params['state']

        # Optional
        self.ownershipgroup = self.module.params.get('ownershipgroup', '')
        self.noownershipgroup = self.module.params.get('noownershipgroup', '')
        self.removeallhosts = self.module.params.get('removeallhosts', '')
        self.site = self.module.params.get('site', '')
        self.partition = self.module.params.get('partition', '')
        self.removemappings = self.module.params.get('removemappings', '')
        self.restapi = IBMSVCRestApi(
            module=self.module,
            clustername=self.module.params['clustername'],
            domain=self.module.params['domain'],
            username=self.module.params['username'],
            password=self.module.params['password'],
            validate_certs=self.module.params['validate_certs'],
            log_path=log_path,
            token=self.module.params['token']
        )

    def basic_checks(self):
        if self.state == 'present':
            if self.removemappings or self.removeallhosts:
                self.module.fail_json(msg="Parameter [removemappings] or [removeallhosts] can be used only while deleting hostcluster")

            if self.ownershipgroup and self.noownershipgroup:
                self.module.fail_json(msg='Mutually exclusive parameters: [ownershipgroup, noownershipgroup]')

        if self.state == 'absent':
            if self.removeallhosts and self.removemappings:
                self.module.fail_json(msg='Mutually exclusive parameters: [removeallhosts, removemappings]')

            fields = [f for f in ['ownershipgroup', 'noownershipgroup', 'site', 'partition'] if getattr(self, f)]
            if any(fields):
                self.module.fail_json(msg='Parameters [{0}] not supported while deleting a hostcluster'.format(', '.join(fields)))

    def get_existing_hostcluster(self):
        return self.restapi.svc_obj_info(cmd='lshostcluster', cmdopts=None, cmdargs=[self.name]) or {}

    def get_existing_partition(self, partition_name):
        return self.restapi.svc_obj_info(cmd='lspartition', cmdopts=None, cmdargs=[partition_name]) or {}

    def hostcluster_probe(self, data):
        props = []

        if self.ownershipgroup and self.ownershipgroup != data['owner_name']:
            props.append('ownershipgroup')

        if self.noownershipgroup and data['owner_name'] != "":
            props.append('noownershipgroup')

        if self.partition:
            partition_result = self.get_existing_partition(self.partition)
            if not partition_result:
                self.module.fail_json(msg="Partition [{0}] does not exist".format(self.partition))

            if partition_result.get('draft') == 'yes':
                if self.partition != data['draft_partition_name']:
                    if data['partition_name']:
                        self.module.fail_json(msg="Hostcluster is already associated with a partition.")
                    props.append('partition')
            else:
                if self.partition != data['partition_name']:
                    self.module.fail_json(msg="Published partition is not supported while updating host cluster")

        if self.site:
            if data['host_count'] == '0':
                self.module.fail_json(msg="Cannot update host cluster [{0}] site to [{1}] as it has no hosts.".format(self.name, self.site))

            site_update_required = False
            existing_hosts = self.restapi.svc_obj_info(cmd='lshost', cmdopts={'filtervalue' : 'host_cluster_name={0}'.format(self.name)}, cmdargs=None)

            conflict_hosts = []
            for host in existing_hosts:
                if host['site_name'] == "":
                    site_update_required = True
                elif self.site != host['site_name'] and self.site != host['site_id']:
                    conflict_hosts.append(f"{host['name']} (Current site: {host['site_name']})")

            if conflict_hosts:
                self.module.fail_json(
                    msg=f"Cannot update host cluster site to [{self.site}]. "
                        f"The following hosts already have a different site: {', '.join(conflict_hosts)}"
                )
            if site_update_required:
                props.append('site')

        self.log("hostcluster_probe props='%s'", props)

        return props

    def hostcluster_create(self):
        if self.module.check_mode:
            self.changed = True
            return
        # Make command
        cmd = 'mkhostcluster'
        cmdopts = {'name': self.name}

        fields = [f for f in ['site'] if getattr(self, f)]
        if any(fields):
            self.module.fail_json(msg='Parameters [{0}] not supported while creating a hostcluster'.format(', '.join(fields)))

        if self.ownershipgroup:
            cmdopts['ownershipgroup'] = self.ownershipgroup

        if self.partition:
            partition_result = self.get_existing_partition(self.partition)
            if not partition_result:
                self.module.fail_json(msg="Partition [{0}] does not exist".format(self.partition))
            if partition_result.get('draft') == 'yes':
                cmdopts['draftpartition'] = self.partition
            else:
                cmdopts['partition'] = self.partition

        self.log("Command options for creating host: '%s'", cmdopts)

        # Run command
        self.restapi.svc_run_command(cmd, cmdopts, cmdargs=None)
        self.changed = True

    def hostcluster_update(self, modify):
        if self.module.check_mode:
            self.changed = True
            return

        self.log("updating host cluster '%s'", self.name)
        cmd = 'chhostcluster'
        cmdopts = {}

        for param in modify:
            if param == 'partition':
                cmdopts['draftpartition'] = self.partition
            else:
                cmdopts[param] = getattr(self, param)

        if cmdopts:
            self.restapi.svc_run_command(cmd, cmdopts, cmdargs=[self.name])
            # Any error will have been raised in svc_run_command
            # chhost does not output anything when successful.
            self.changed = True
            self.log("Properties of %s updated", self.name)

    def hostcluster_delete(self, data):
        if self.module.check_mode:
            self.changed = True
            return

        self.log("deleting host cluster '%s'", self.name)

        cmd = 'rmhostcluster'
        cmdopts = {}
        cmdargs = [self.name]

        is_partition_associated = bool(data.get('partition_name') or data.get('draft_partition_name'))
        mapping_count = data.get('mapping_count')
        has_mappings = mapping_count and mapping_count != "0"

        if self.removemappings:
            if is_partition_associated:
                self.module.fail_json(
                    msg=f"Cannot remove host cluster [{self.name}] as it is associated with a partition. "
                        f"Use removemappings=false to delete the host cluster to keep host to volume mappings."
                )
            if has_mappings:
                cmdopts['removemappings'] = True
        elif (is_partition_associated or has_mappings) and not self.removeallhosts:
            cmdopts['keepmappings'] = True

        if self.removeallhosts:
            cmdopts['force'] = True
            cmdopts['removeallhosts'] = True

        self.restapi.svc_run_command(cmd, cmdopts, cmdargs)
        # Any error will have been raised in svc_run_command
        # chhost does not output anything when successful.
        self.changed = True

    def apply(self):
        changed = False
        msg = None
        modify = []

        self.basic_checks()
        hc_data = self.get_existing_hostcluster()

        if hc_data:
            if self.state == 'absent':
                self.log("CHANGED: host cluster exists, but requested "
                         "state is 'absent'")
                changed = True
            elif self.state == 'present':
                # This is where we detect if chhostcluster should be called
                modify = self.hostcluster_probe(hc_data)
                if modify:
                    changed = True
        else:
            if self.state == 'present':
                self.log("CHANGED: host cluster does not exist, "
                         "but requested state is 'present'")
                changed = True

        if changed:
            if self.state == 'present':
                if not hc_data:
                    self.hostcluster_create()
                    msg = "host cluster %s has been created." % self.name
                else:
                    # This is where we would modify
                    self.hostcluster_update(modify)
                    msg = "host cluster [%s] has been modified." % self.name
            elif self.state == 'absent':
                self.hostcluster_delete(hc_data)
                msg = "host cluster [%s] has been deleted." % self.name

            if self.module.check_mode:
                msg = "skipping changes due to check mode"
        else:
            self.log("exiting with no changes")
            if self.state == 'absent':
                msg = "host cluster [%s] did not exist." % self.name
            else:
                msg = "host cluster [%s] already exists. No modifications done." % self.name

        self.module.exit_json(msg=msg, changed=changed)


def main():
    v = IBMSVChostcluster()
    try:
        v.apply()
    except Exception as e:
        v.log("Exception in apply(): \n%s", format_exc())
        v.module.fail_json(msg="Module failed. Error [%s]." % to_native(e))


if __name__ == '__main__':
    main()
