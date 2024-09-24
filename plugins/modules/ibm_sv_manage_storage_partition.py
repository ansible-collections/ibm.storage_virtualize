#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2023 IBM CORPORATION
# Author(s): Shilpi Jain <shilpi.jain1@ibm.com>
#            Sumit Kumar Gupta <sumit.gupta16@ibm.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: ibm_sv_manage_storage_partition
short_description: This module manages storage partition on IBM Storage Virtualize family systems
version_added: '2.1.0'
description:
  - This Ansible module provides the interface to manage syslog servers through 'mksyslogserver',
    'chsyslogserver' and 'rmsyslogserver' Storage Virtualize commands.
  - The Policy based High Availability (HA) solution uses Storage Partitions. These partitions contain volumes,
    volume groups, host and host-to-volume mappings.
options:
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
    log_path:
        description:
            - Path of debug log file.
        type: str
    state:
        description:
            - Creates, updates (C(present)) or deletes (C(absent)) a storage partition.
        choices: [ present, absent ]
        required: true
        type: str
    name:
        description:
            - Specifies the name of a storage partition.
        type: str
        required: true
    replicationpolicy:
        description:
            - Specifies the replication policy for the storage partition.
        type: str
    noreplicationpolicy:
        description:
            - Unassigns the current replication policy from the volume group. This parameter, if used without
              I(deletepreferredmanagementcopy) parameter, is allowed only on active management system.
        type: bool
    preferredmanagementsystem:
        description:
            - Changes the preferred management system for the storage partition.
            - Permitted only from the system which is the active management system.
        type: str
    deletepreferredmanagementcopy:
        description:
            - This parameter is to be used along with I(noreplicationpolicy) parameter and active management system
              must NOT be the same as the preferred management system.
        type: bool
    deletenonpreferredmanagementobjects:
        description:
            - If the storage partition has a replication policy and associated objects, such as volumes, volumes groups,
              hosts or host mappings, one of the two I(deletenonpreferredmanagementobjects) or
              I(deletepreferredmanagementobjects) parmeters is required. If specified, the command is only permitted on
              the active management system, and requires that the active management system is the same as the preferred
              management system.
            - Applies when I(state=absent).
        type: bool
    deletepreferredmanagementobjects:
        description:
            - If the storage partition has a replication policy and associated objects, such as volumes, volumes groups,
              hosts or host mappings, one of the two I(deletenonpreferredmanagementobjects) or
              I(deletepreferredmanagementobjects) parmeters is required. If the storage partition cannot be managed at
              the preferred management system then I(deletepreferredmanagementobjects) to be used to remove the storage
              partition and unassign the replication policy.
            - Applies when I(state=absent).
        type: bool
    draft:
        description:
            - If specified and set to true, creates a partition in draft state. If set to false, creates a new partition
              into published state or moves an existing partition into published state.
            - Applies when I(state=present).
        type: bool
        version_added: 2.5.0
    partition_to_merge:
        description:
            - If specified, merges the I(partition_to_merge) and all its objects into partition specified with I(name).
            - After merge, partition specified with I(partition_to_merge) disappears from the list of partitions.
            - Applies when I(state=present).
        type: str
        version_added: 2.5.0
    validate_certs:
        description:
            - Validates certification.
        default: false
        type: bool
author:
    - Shilpi Jain (@Shilpi-J)
    - Sumit Kumar Gupta (@sumitguptaibm)
notes:
    - This module supports C(check_mode).
'''

EXAMPLES = '''
- name: Create Storage Partition
  ibm.storage_virtualize.ibm_sv_manage_storage_partition:
   clustername: '{{clustername}}'
   username: '{{username}}'
   password: '{{password}}'
   name: partition1
   state: present
   replicationpolicy: ha_policy_1
- name: Delete the storage partition
  ibm.storage_virtualize.ibm_sv_manage_storage_partition:
   clustername: '{{clustername}}'
   username: '{{username}}'
   password: '{{password}}'
   name: partition1
   state: absent
- name: Create a partition in draft state
  ibm.storage_virtualize.ibm_sv_manage_storage_partition:
   clustername: "{{ clustername }}"
   domain: "{{ domain }}"
   username: "{{ username }}"
   password: "{{ password }}"
   log_path: /tmp/playbook.debug
   name: partition0
   state: present
   draft: true
- name: Publish a draft partition
  ibm.storage_virtualize.ibm_sv_manage_storage_partition:
   clustername: "{{ clustername }}"
   domain: "{{ domain }}"
   username: "{{ username }}"
   password: "{{ password }}"
   log_path: /tmp/playbook.debug
   name: partition0
   state: present
   draft: false
- name: Merge partition (partition1) into partition (partition0)
  ibm.storage_virtualize.ibm_sv_manage_storage_partition:
   clustername: "{{ clustername }}"
   domain: "{{ domain }}"
   username: "{{ username }}"
   password: "{{ password }}"
   log_path: /tmp/playbook.debug
   name: partition0
   state: present
   partition_to_merge: partition1
'''

RETURN = '''#'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils import (
    IBMSVCRestApi,
    svc_argument_spec,
    get_logger
)
from ansible.module_utils._text import to_native


class IBMSVStoragePartition:

    def __init__(self):
        argument_spec = svc_argument_spec()
        argument_spec.update(
            dict(
                state=dict(
                    type='str',
                    required=True,
                    choices=['present', 'absent']
                ),
                name=dict(
                    type='str',
                    required=True
                ),
                replicationpolicy=dict(
                    type='str'
                ),
                noreplicationpolicy=dict(
                    type='bool'
                ),
                preferredmanagementsystem=dict(
                    type='str'
                ),
                deletepreferredmanagementcopy=dict(
                    type='bool'
                ),
                deletenonpreferredmanagementobjects=dict(
                    type='bool'
                ),
                deletepreferredmanagementobjects=dict(
                    type='bool'
                ),
                draft=dict(
                    type='bool'
                ),
                partition_to_merge=dict(
                    type='str'
                )

            )
        )

        self.module = AnsibleModule(argument_spec=argument_spec,
                                    supports_check_mode=True)

        # Required parameters
        self.name = self.module.params['name']
        self.state = self.module.params['state']

        # Optional parameters
        self.replicationpolicy = self.module.params.get('replicationpolicy', '')
        self.noreplicationpolicy = self.module.params.get('noreplicationpolicy', '')
        self.preferredmanagementsystem = self.module.params.get('preferredmanagementsystem', '')
        self.deletepreferredmanagementcopy = self.module.params.get('deletepreferredmanagementcopy', '')
        self.deletenonpreferredmanagementobjects = self.module.params.get('deletenonpreferredmanagementobjects', '')
        self.deletepreferredmanagementobjects = self.module.params.get('deletepreferredmanagementobjects', '')
        self.draft = self.module.params.get('draft', '')
        self.partition_to_merge = self.module.params.get('partition_to_merge', '')

        # logging setup
        self.log_path = self.module.params['log_path']
        log = get_logger(self.__class__.__name__, self.log_path)
        self.log = log.info

        # Dynamic variables
        self.changed = False
        self.msg = ''

        self.basic_checks()

        self.restapi = IBMSVCRestApi(
            module=self.module,
            clustername=self.module.params['clustername'],
            domain=self.module.params['domain'],
            username=self.module.params['username'],
            password=self.module.params['password'],
            validate_certs=self.module.params['validate_certs'],
            log_path=self.log_path,
            token=self.module.params['token']
        )

    def basic_checks(self):
        if not self.name:
            self.module.fail_json(msg='Missing mandatory parameter: name')

        if self.state == 'present':
            if self.deletenonpreferredmanagementobjects or self.deletepreferredmanagementobjects:
                self.module.fail_json(
                    msg='Parameters not allowed while creation or update: '
                        'deletenonpreferredmanagementobjects, deletepreferredmanagementobjects'
                )

            if self.draft is not None:
                invalids_with_draft_opt = (
                    'replicationpolicy',
                    'noreplicationpolicy',
                    'preferredmanagementsystem',
                    'deletepreferredmanagementcopy',
                    'partition_to_merge'
                )
                invalid_exists_for_draft_opt = ', '.join((var for var in invalids_with_draft_opt if getattr(self, var) not in {'', None}))

                if invalid_exists_for_draft_opt:
                    self.module.fail_json(
                        msg='Parameter (draft) is mutually exclusive with parameter(s): ({0})'.format(
                            invalid_exists_for_draft_opt)
                    )

            if self.partition_to_merge:
                invalids_with_partition_to_merge = (
                    'replicationpolicy',
                    'noreplicationpolicy',
                    'preferredmanagementsystem',
                    'deletepreferredmanagementcopy',
                    'draft'
                )

                invalid_exists_for_partition_to_merge_opt = ', '.join((var for var in invalids_with_partition_to_merge if getattr(self, var) not in {'', None}))

                if invalid_exists_for_partition_to_merge_opt:
                    self.module.fail_json(
                        msg='Parameter (partition_to_merge) is mutually exclusive with parameter(s): ({0})'.format(
                            invalid_exists_for_partition_to_merge_opt)
                    )

        else:
            invalids_for_delete = (
                'replicationpolicy',
                'noreplicationpolicy',
                'preferredmanagementsystem',
                'deletepreferredmanagementcopy',
                'draft',
                'partition_to_merge'
            )

            invalid_exists = ', '.join((var for var in invalids_for_delete if getattr(self, var) not in {'', None}))

            if invalid_exists:
                self.module.fail_json(
                    msg='state=absent but following parameter(s) have been passed: {0}'.format(invalid_exists)
                )

    def get_storage_partition_details(self, name):
        merged_result = {}

        data = self.restapi.svc_obj_info(cmd='lspartition', cmdopts=None, cmdargs=[name])
        if isinstance(data, list):
            for d in data:
                merged_result.update(d)
        else:
            merged_result = data

        return merged_result

    def create_storage_partition(self):
        unsupported = ('noreplicationpolicy', 'preferredmanagementsystem', 'deletepreferredmanagementcopy')
        unsupported_exists = ', '.join((field for field in unsupported if getattr(self, field) not in {'', None}))

        if unsupported_exists:
            self.module.fail_json(
                msg='Parameters not supported while creation: {0}'.format(unsupported_exists)
            )

        if self.module.check_mode:
            self.changed = True
            return

        cmd = 'mkpartition'
        cmdopts = {
            'name': self.name
        }

        if self.draft is True:
            cmdopts['draft'] = self.draft
        if self.replicationpolicy:
            cmdopts['replicationpolicy'] = self.replicationpolicy

        self.restapi.svc_run_command(cmd, cmdopts, cmdargs=None)
        self.log('Storage Partition (%s) created', self.name)
        self.changed = True

    def partition_probe(self, data):
        if self.replicationpolicy and self.noreplicationpolicy:
            self.module.fail_json(msg='Mutual exclusive parameters: {0}, {1}'.format("replicationpolicy",
                                                                                     "noreplicationpolicy"))
        if self.replicationpolicy and self.preferredmanagementsystem:
            self.module.fail_json(msg='Mutual exclusive parameters: {0}, {1}'.format("replicationpolicy",
                                                                                     "preferredmanagementsystem"))
        if self.deletepreferredmanagementcopy and not self.noreplicationpolicy:
            self.module.fail_json(msg='These parameters must be passed together: {0}, {1}'.format(
                                  "deletepreferredmanagementcopy", "noreplicationpolicy"))

        # Mapping the parameters with the existing data for comparision
        params_mapping = (
            ('replicationpolicy', data.get('replication_policy_name', '')),
            ('preferredmanagementsystem', data.get('preferred_management_system_name', '')),
            ('noreplicationpolicy', not bool(data.get('replication_policy_name', '')))
        )

        props = dict((k, getattr(self, k)) for k, v in params_mapping if getattr(self, k) and getattr(self, k) != v)

        if self.noreplicationpolicy in props:
            if self.deletepreferredmanagementcopy:
                props['deletepreferredmanagementcopy'] = True

        if data.get('draft', '') == 'yes' and self.draft is False:
            props['draft'] = True

        self.log("Storage Partition props = %s", props)

        return props

    def update_storage_partition(self, updates):
        if self.module.check_mode:
            self.changed = True
            return

        # draft=False directly implies, that user wants to publish the partition

        cmd = 'chpartition'
        cmdopts = dict((k, getattr(self, k)) for k in updates)
        cmdargs = [self.name]

        # If existing partition's data indicates, that partition is already published, then nothing to do.
        # If not, then insert publish=true in API
        if 'draft' in cmdopts:
            cmdopts.pop('draft')
            cmdopts['publish'] = True

        self.restapi.svc_run_command(cmd, cmdopts=cmdopts, cmdargs=cmdargs)
        self.changed = True

    def delete_storage_partition(self):
        if self.module.check_mode:
            self.changed = True
            return

        cmd = 'rmpartition'
        cmdopts = {}
        if self.deletenonpreferredmanagementobjects:
            cmdopts['deletenonpreferredmanagementobjects'] = self.deletenonpreferredmanagementobjects
        if self.deletepreferredmanagementobjects:
            cmdopts['deletepreferredmanagementobjects'] = self.deletepreferredmanagementobjects

        self.restapi.svc_run_command(cmd, cmdopts=cmdopts, cmdargs=[self.name])
        self.changed = True

    def merge_partitions(self):
        '''
        This funcion merges partititon_to_merge into target partition.
        '''
        if self.module.check_mode:
            self.changed = True
            return

        # Get source partition 'partition_to_merge' details. If it is absent, it is either already merged, or does not
        # exist. In both such cases, ansible won't return error.
        source_partition_data = self.get_storage_partition_details(self.partition_to_merge)
        if not source_partition_data:
            self.msg = 'Partition ({0}) does not exist or is already merged.'.format(self.partition_to_merge)
            self.changed = False
            return

        cmd = 'mergepartition'
        cmdopts = {}
        cmdopts['targetpartition'] = self.name
        self.restapi.svc_run_command(cmd, cmdopts=cmdopts, cmdargs=[self.partition_to_merge])
        self.msg = "Partition ({0}) was successfully merged into partition ({1}).".format(self.partition_to_merge,
                                                                                          self.name)
        self.changed = True

    def apply(self):
        data = self.get_storage_partition_details(self.name)

        if data:
            if self.state == 'present':
                if self.partition_to_merge:
                    self.merge_partitions()
                else:
                    modifications = self.partition_probe(data)
                    if modifications:
                        self.update_storage_partition(modifications)
                        self.msg = 'Storage Partition ({0}) updated'.format(self.name)
                    else:
                        self.msg = 'Storage Partition ({0}) already exists. No modifications done.'.format(self.name)
            else:
                self.delete_storage_partition()
                self.msg = 'Storage Partition ({0}) deleted.'.format(self.name)
        else:
            if self.state == 'absent':
                self.msg = 'Storage Partition ({0}) does not exist'.format(self.name)
            elif self.partition_to_merge:
                self.module.fail_json(msg="Target Partition ({0}) does not exist. Merge failed.".format(self.name))
            else:
                self.create_storage_partition()
                self.msg = 'Storage Partition ({0}) created.'.format(self.name)

        if self.module.check_mode:
            self.msg = 'skipping changes due to check mode.'

        self.module.exit_json(
            changed=self.changed,
            msg=self.msg
        )


def main():
    v = IBMSVStoragePartition()
    try:
        v.apply()
    except Exception as e:
        v.log('Exception in apply(): \n%s', format_exc())
        v.module.fail_json(msg='Module failed. Error [%s].' % to_native(e))


if __name__ == '__main__':
    main()
