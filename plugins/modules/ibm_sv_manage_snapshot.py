#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2022 IBM CORPORATION
# Author(s): Sanjaikumaar M <sanjaikumaar.m@ibm.com>
#            Sumit Kumar Gupta <sumit.gupta16@ibm.com>
#            Sandip Gulab Rajbanshi <sandip.rajbanshi@ibm.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: ibm_sv_manage_snapshot
short_description: This module manages snapshots (PiT image of a volume) on IBM Storage Virtualize family systems
version_added: '1.9.0'
description:
  - In this implementation, a snapshot is a mutually consistent image of the volumes
    in a volume group or a list of independent volume(s).
  - This Ansible module provides the interface to manage snapshots through 'addsnapshot',
    'chsnapshot' and 'rmsnapshot' Storage Virtualize commands.
options:
    clustername:
        description:
            - The hostname or management IP or Partition IP of the Storage Virtualize system.
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
            - Creates, updates (C(present)), restores from (C(restore)) or deletes (C(absent)) a snapshot.
        choices: [ present, restore, absent ]
        required: true
        type: str
    name:
        description:
            - Specifies the name or UUID of a snapshot.
        type: str
    old_name:
        description:
            - Specifies the old name or UUID of a snapshot.
            - Valid when I(state=present), to rename the existing snapshot.
        type: str
    src_volumegroup_name:
        description:
            - Specifies the name or UUID of the source volume group for which the snapshot is being created.
            - I(src_volumegroup_name) and I(src_volume_names) are mutually exclusive for creating snapshot.
            - Required one of I(src_volumegroup_name) or I(src_volume_names) for creation of snapshot.
        type: str
    src_volume_names:
        description:
            - Specifies the name or UID of the volumes for which the snapshots are to be created.
            - List of volume names can be specified with the delimiter colon.
            - Valid when I(state=present), to create a snapshot.
        type: str
    snapshot_pool:
        description:
            - Specifies the name or UUID of child pool within which the snapshot is being created.
            - This parameter is checked for idempotency ONLY when the snapshot is managed using C(src_volume_names). When C(src_volumegroup_name) is used,
              validation is skipped for existing snapshots due to performance considerations.
        type: str
    ignorelegacy:
        description:
            - Specifies the addition of the volume snapshots although there are already legacy FlashCopy mappings using the volume as a source.
        default: false
        type: bool
    ownershipgroup:
        description:
            - Specifies the name of the ownershipgroup.
            - Valid when I(state=present), to update an existing snapshot.
        type: str
    safeguarded:
        description:
            - Flag to create a safeguarded snapshot.
            - I(safeguarded) and I(retentiondays) are required together.
            - Supported in SV build 8.5.2.0 or later.
        type: bool
        version_added: 1.10.0
    retentiondays:
        description:
            - Specifies the retention period in days.
            - I(safeguarded) and I(retentiondays) are required together.
            - Applies, when I(state=present) to create a safeguarded snapshot.
        type: int
        version_added: 1.10.0
    retentionminutes:
        description:
            - Specifies the retention period in minutes in range 1 - 1440.
            - I(retentionminutes) and I(retentiondays) are mutually exclusive.
            - Applies, when I(state=present) to create a transient snapshot.
        type: int
        version_added: 2.3.0
    validate_certs:
        description:
            - Validates certification.
        default: false
        type: bool
author:
    - Sanjaikumaar M (@sanjaikumaar)
    - Sumit Kumar Gupta (@sumitguptaibm)
    - Sandip Gulab Rajbanshi (@sandip-rajbanshi)
notes:
    - This module supports C(check_mode).
    - This module automates the new Snapshot function, implemented by Storage Virtualize, which is using a
      simplified management model. Any user requiring the flexibility available with legacy
      FlashCopy can continue to use the existing module M(ibm.storage_virtualize.ibm_svc_manage_flashcopy).
    - Snapshots created by this Ansible module are not directly accessible from the hosts.
      To create a new group of host accessible volumes from a snapshot,
      use M(ibm.storage_virtualize.ibm_svc_manage_volumegroup) module.
    - In case of restoring local snapshots present before establishing high availability (HA), HA sync will be stopped till the snapshots gets restored.
    - This module supports logging in via partition IP.
'''

EXAMPLES = '''
- name: Create volumegroup snapshot
  ibm.storage_virtualize.ibm_sv_manage_snapshot:
   clustername: '{{ clustername }}'
   username: '{{ username }}'
   password: '{{ password }}'
   name: ansible_1
   src_volumegroup_name: volumegroup1
   snapshot_pool: Pool0Childpool0
   state: present
- name: Create volumes snapshot
  ibm.storage_virtualize.ibm_sv_manage_snapshot:
   clustername: '{{ clustername }}'
   username: '{{ username }}'
   password: '{{ password }}'
   name: ansible_2
   src_volume_names: vdisk0:vdisk1
   snapshot_pool: Pool0Childpool0
   state: present
- name: Create safeguarded snapshot
  ibm.storage_virtualize.ibm_sv_manage_snapshot:
   clustername: '{{ clustername }}'
   username: '{{ username }}'
   password: '{{ password }}'
   name: ansible_2
   src_volume_names: vdisk0:vdisk1
   safeguarded: true
   retentiondays: 1
   snapshot_pool: Pool0Childpool0
   state: present
- name: Update snapshot ansible_2
  ibm.storage_virtualize.ibm_sv_manage_snapshot:
   clustername: '{{ clustername }}'
   username: '{{ username }}'
   password: '{{ password }}'
   name: ansible_new
   old_name: ansible_2
   ownershipgroup: ownershipgroup0
   state: present
- name: Restore all volumes of a volumegroup from a snapshot
  ibm.storage_virtualize.ibm_sv_manage_snapshot:
   clustername: '{{ clustername }}'
   username: '{{ username }}'
   password: '{{ password }}'
   name: snapshot0
   src_volumegroup_name: volumegroup1
   state: restore
- name: Restore subset of volumes of a volumegroup from snapshot
  ibm.storage_virtualize.ibm_sv_manage_snapshot:
   clustername: '{{ clustername }}'
   username: '{{ username }}'
   password: '{{ password }}'
   name: snapshot0
   src_volumegroup_name: volumegroup1
   src_volume_names: vdisk0:vdisk1
   state: restore
- name: Create transient snapshot
  ibm.storage_virtualize.ibm_sv_manage_snapshot:
   clustername: '{{ clustername }}'
   username: '{{ username }}'
   password: '{{ password }}'
   name: snapshot0
   src_volume_names: vdisk0:vdisk1
   safeguarded: true
   retentionminutes: 5
   snapshot_pool: Pool0Childpool0
   state: present
- name: Delete volumegroup snapshot
  ibm.storage_virtualize.ibm_sv_manage_snapshot:
   clustername: '{{ clustername }}'
   username: '{{ username }}'
   password: '{{ password }}'
   name: ansible_1
   src_volumegroup_name: volumegroup1
   state: absent
- name: Delete volume snapshot
  ibm.storage_virtualize.ibm_sv_manage_snapshot:
   clustername: '{{ clustername }}'
   username: '{{ username }}'
   password: '{{ password }}'
   name: ansible_new
   state: absent
- name: Create volumegroup snapshot using UUID for source volumegroup
  ibm.storage_virtualize.ibm_sv_manage_snapshot:
   clustername: '{{ clustername }}'
   username: '{{ username }}'
   password: '{{ password }}'
   name: test_snapshot_uuid
   src_volumegroup_name: 66197B52-9707-548D-8C42-E91A7D35F6B8
   snapshot_pool: 252FB6EB-46EB-5B18-8C42-E91A7D35F6B8
   state: present
- name: Create volumegroup snapshot using UIDs from list of volumes
  ibm.storage_virtualize.ibm_sv_manage_snapshot:
   clustername: '{{ clustername }}'
   username: '{{ username }}'
   password: '{{ password }}'
   name: test_snapshot_uuid
   src_volume_names: 6005076400810261F80000000000027E:6005076400810261F80000000000027D
   snapshot_pool: 252FB6EB-46EB-5B18-8C42-E91A7D35F6B8
   state: present
- name: Rename snapshot using old_name UUID
  ibm.storage_virtualize.ibm_sv_manage_snapshot:
   clustername: '{{ clustername }}'
   username: '{{ username }}'
   password: '{{ password }}'
   name: test_snapshot_renamed
   old_name: C2A27DD7-C5DA-5078-A7E3-5CB912F84D60
   src_volumegroup_name: 66197B52-9707-548D-8C42-E91A7D35F6B8
   state: present
- name: Delete snapshot using UUID
  ibm.storage_virtualize.ibm_sv_manage_snapshot:
   clustername: '{{ clustername }}'
   username: '{{ username }}'
   password: '{{ password }}'
   name: C2A27DD7-C5DA-5078-A7E3-5CB912F84D60
   src_volumegroup_name: 66197B52-9707-548D-8C42-E91A7D35F6B8
   state: absent
'''

RETURN = '''#'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils import (
    IBMSVCRestApi,
    svc_argument_spec,
    strtobool,
    get_logger,
    is_uuid
)
from ansible.module_utils._text import to_native

MIN_SNAPSHOT_RETENTION_MINUTES = 1
MAX_SNAPSHOT_RETENTION_MINUTES = 1440


class IBMSVSnapshot:

    def __init__(self):
        argument_spec = svc_argument_spec()
        argument_spec.update(
            dict(
                state=dict(
                    type='str',
                    required=True,
                    choices=['present', 'restore', 'absent']
                ),
                name=dict(
                    type='str',
                ),
                old_name=dict(
                    type='str'
                ),
                snapshot_pool=dict(
                    type='str',
                ),
                src_volumegroup_name=dict(
                    type='str',
                ),
                src_volume_names=dict(
                    type='str',
                ),
                ignorelegacy=dict(
                    type='bool',
                    default=False
                ),
                ownershipgroup=dict(
                    type='str',
                ),
                safeguarded=dict(
                    type='bool'
                ),
                retentiondays=dict(
                    type='int',
                ),
                retentionminutes=dict(
                    type='int'
                )
            )
        )

        self.module = AnsibleModule(argument_spec=argument_spec,
                                    supports_check_mode=True)

        # Required parameters
        self.name = self.module.params['name']
        self.state = self.module.params['state']

        # Default parameters
        self.ignorelegacy = self.module.params['ignorelegacy']

        # Optional parameters
        self.old_name = self.module.params.get('old_name', '')
        self.ownershipgroup = self.module.params.get('ownershipgroup', '')
        self.snapshot_pool = self.module.params.get('snapshot_pool', '')
        self.volumegroup = self.module.params.get('src_volumegroup_name', '')
        self.volumes = self.module.params.get('src_volume_names', '')
        self.safeguarded = self.module.params.get('safeguarded', False)
        self.retentiondays = self.module.params.get('retentiondays')
        self.retentionminutes = self.module.params.get('retentionminutes')

        self.basic_checks()

        # logging setup
        self.log_path = self.module.params['log_path']
        log = get_logger(self.__class__.__name__, self.log_path)
        self.log = log.info

        # Dynamic variables
        self.changed = False
        self.msg = ''
        self.parentuid = None
        self.lsvg_data = {}
        self.lsv_data = {}

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

        if not self.state:
            self.module.fail_json(msg='Missing mandatory parameter: state')

        if self.state == 'present':
            if self.volumegroup and self.volumes:
                self.module.fail_json(
                    msg='Mutually exclusive parameters: src_volumegroup_name, src_volume_names'
                )
            if self.retentionminutes is not None:
                if (self.retentionminutes < MIN_SNAPSHOT_RETENTION_MINUTES or
                        self.retentionminutes > MAX_SNAPSHOT_RETENTION_MINUTES):
                    self.module.fail_json(
                        msg='Invalid value for retentionminutes parameter. Valid range 1-1440.'
                    )

        elif self.state == 'restore':
            # Check mandatory parameter src_volumegroup_name
            if not self.volumegroup:
                self.module.fail_json(
                    msg='Missing mandatory parameter src_volumegroup_name'
                )
            invalids = ('snapshot_pool', 'ignorelegacy', 'ownershipgroup',
                        'old_name', 'safeguarded', 'retentiondays', 'retentionminutes')
            invalid_exists = ', '.join((var for var in invalids if getattr(self, var)))
            if invalid_exists:
                self.module.fail_json(
                    msg='Invalid parameters for state=restore: {0}'.format(invalid_exists)
                )

        elif self.state == 'absent':
            invalids = ('snapshot_pool', 'ignorelegacy', 'ownershipgroup',
                        'old_name', 'safeguarded', 'retentiondays', 'retentionminutes')
            invalid_exists = ', '.join((var for var in invalids if getattr(self, var)))

            if self.volumes:
                invalid_exists = 'src_volume_names, {0}'.format(invalid_exists)

            if invalid_exists:
                self.module.fail_json(
                    msg='Invalid parameters for state=absent: {0}'.format(invalid_exists)
                )
        else:
            self.module.fail_json(msg='State should be one of present,restore or absent')

    def create_validation(self):
        if self.old_name:
            self.rename_validation([])

        if is_uuid(self.name):
            self.module.fail_json(
                msg='Snapshot cannot be created with UUID. Please specify '
                    'user-defined snapshot name to create snapshot.'
            )

        if not self.volumegroup and not self.volumes:
            self.module.fail_json(
                msg='Either src_volumegroup_name or src_volume_names should be passed during snapshot creation.'
            )

        if self.ownershipgroup:
            self.module.fail_json(
                msg='`ownershipgroup` parameter is not supported during snapshot creation'
            )

    def rename_validation(self, updates):
        if self.old_name and self.name:

            if self.name == self.old_name:
                self.module.fail_json(msg='New name and old name should be different.')

            new = self.is_snapshot_exists()
            existing = self.is_snapshot_exists(old_name=self.old_name)

            if existing:
                if new:
                    self.module.fail_json(
                        msg='Snapshot ({0}) already exists for the given new name.'.format(self.name)
                    )
                else:
                    updates.append('name')
            else:
                if not new:
                    self.module.fail_json(
                        msg='Snapshot ({0}) does not exists for the given old name.'.format(self.old_name)
                    )
                else:
                    self.module.exit_json(
                        msg='Snapshot ({0}) already renamed. No modifications done.'.format(self.name)
                    )

    def is_snapshot_exists(self, old_name=None, force=False):
        old_name = old_name if old_name else self.name
        if self.volumegroup:
            data = self.lsvolumegroupsnapshot(old_name=old_name, force=force)
            self.parentuid = data.get('parent_uid')
        else:
            if self.lsv_data.get('snapshot_name') == old_name and not force:
                return self.lsv_data
            if is_uuid(old_name):
                cmdopts = {
                    "filtervalue": "snapshot_id={0}".format(old_name)
                }
            else:
                cmdopts = {
                    "filtervalue": "snapshot_name={0}".format(old_name)
                }
            result = self.restapi.svc_obj_info(
                cmd='lsvolumesnapshot',
                cmdopts=cmdopts,
                cmdargs=['-gui']
            )
            try:
                data = next(
                    filter(
                        lambda x: x['volume_group_name'] == '',
                        result
                    )
                )
            except StopIteration:
                return {}
            else:
                self.lsv_data = data
                self.parentuid = data.get('parent_uid')

        return data

    def lsvolumegroupsnapshot(self, force=False, old_name=None, parentuid=None):
        old_name = old_name if old_name else self.name
        if self.lsvg_data.get('name') == old_name and not force:
            return self.lsvg_data

        cmdopts = {
            'snapshot': old_name
        }
        cmdargs = None
        if is_uuid(old_name):
            cmdopts.pop('snapshot')
            cmdargs = [old_name]
        elif parentuid:
            cmdopts['parentuid'] = self.parentuid
        else:
            if is_uuid(self.volumegroup):
                vg_info = self.restapi.svc_obj_info(
                    'lsvolumegroup',
                    None,
                    [self.volumegroup])
                vg_name = vg_info.get("name", None)
                if vg_name:
                    self.volumegroup = vg_name
            cmdopts['volumegroup'] = self.volumegroup

        data = {}
        result = self.restapi.svc_obj_info(
            cmd='lsvolumegroupsnapshot',
            cmdopts=cmdopts,
            cmdargs=cmdargs
        )

        if isinstance(result, list):
            for res in result:
                data = res
        else:
            data = result

        self.lsvg_data = data

        return data

    def create_snapshot(self):
        self.create_validation()
        if self.module.check_mode:
            self.changed = True
            return

        cmd = 'addsnapshot'
        cmdopts = {
            'name': self.name
        }

        if self.snapshot_pool:
            cmdopts['pool'] = self.snapshot_pool
        if self.ignorelegacy:
            cmdopts['ignorelegacy'] = self.ignorelegacy
        if self.retentiondays:
            cmdopts['retentiondays'] = self.retentiondays
        if self.retentionminutes:
            cmdopts['retentionminutes'] = self.retentionminutes
        if self.safeguarded:
            cmdopts['safeguarded'] = self.safeguarded

        if self.volumegroup:
            cmdopts['volumegroup'] = self.volumegroup
        else:
            cmdopts['volumes'] = self.volumes

        self.restapi.svc_run_command(cmd, cmdopts, cmdargs=None)
        self.log('Snapshot (%s) created', self.name)
        self.changed = True

    def restore_from_snapshot(self, snapshot_data):
        if self.module.check_mode:
            self.changed = True
            return

        cmd = 'restorefromsnapshot'
        cmdopts = {
            'snapshot': self.name
        }
        if is_uuid(self.name):
            cmdopts.pop('snapshot')
            cmdopts['snapshotid'] = self.name
        elif self.volumegroup:
            cmdopts['volumegroup'] = self.volumegroup
        if self.volumes:
            if snapshot_data.get("ha_state") == "highly_available":
                vol_list = self.volumes.split(":")
                if len(vol_list) > 1:
                    self.module.fail_json(
                        msg="CMMVC1301E The command failed because highly available snapshot restore is"
                            " only permitted on the whole snapshot or specifying a single volume"
                    )
            cmdopts['volumes'] = self.volumes
        if snapshot_data.get("ha_state") == "local":
            cmdopts['resyncrestoredvolumes'] = True

        self.restapi.svc_run_command(cmd, cmdopts, cmdargs=None)
        self.changed = True

    def snapshot_probe(self):
        updates = []
        self.rename_validation(updates)
        kwargs = dict((k, getattr(self, k)) for k in ['old_name', 'parentuid'] if getattr(self, k))
        ls_data = self.lsvolumegroupsnapshot(**kwargs)

        if self.ownershipgroup and ls_data['owner_name'] != self.ownershipgroup:
            updates.append('ownershipgroup')

        if self.safeguarded in {True, False} and self.safeguarded != strtobool(ls_data.get('safeguarded', 0)):
            self.module.fail_json(
                msg='Following parameter not applicable for update operation: safeguarded'
            )

        if self.snapshot_pool and not self.volumegroup and self.lsv_data:
            self.log('Performing snapshot_pool validation for volume snapshot %s.', self.name)
            expected_pool = self.snapshot_pool
            if is_uuid(self.snapshot_pool):
                try:
                    self.log('snapshot_pool provided as UUID. Fetching pool details for %s.', self.snapshot_pool)
                    pool_info = self.restapi.svc_obj_info('lsmdiskgrp', None, [self.snapshot_pool])
                    if isinstance(pool_info, dict) and 'name' in pool_info:
                        expected_pool = pool_info['name']
                        self.log('Resolved snapshot_pool UUID to pool name: %s', expected_pool)
                    elif isinstance(pool_info, list) and pool_info and 'name' in pool_info[0]:
                        expected_pool = pool_info[0]['name']
                        self.log('Resolved snapshot_pool UUID to pool name: %s', expected_pool)
                    else:
                        self.log('Could not resolve UUID %s to a pool name. Using UUID for validation.', self.snapshot_pool)
                except Exception as e:
                    self.log('Failed to fetch pool details for UUID %s: %s. Using UUID for validation.', self.snapshot_pool, to_native(e))

            pool_id = self.lsv_data.get('pool_1_id')
            pool_name = self.lsv_data.get('pool_1_name')
            self.log('Snapshot is currently in pool_id: %s, pool_name: %s. Expected pool: %s', pool_id, pool_name, expected_pool)

            if pool_name and expected_pool not in (pool_id, pool_name):
                self.log('Snapshot pool validation failed: existing pool %s does not match expected %s', pool_name, expected_pool)
                self.module.fail_json(
                    msg='Snapshot ({0}) already exists in a different pool ({1}). Cannot change pool of an existing snapshot.'.format(
                        self.name, pool_name
                    )
                )
            else:
                self.log('Snapshot pool validation passed.')

        self.log('Snapshot probe result: %s', updates)
        return updates

    def update_snapshot(self, updates):
        if self.module.check_mode:
            self.changed = True
            return

        old_name = self.old_name if self.old_name else self.name
        cmd = 'chsnapshot'
        cmdopts = dict((k, getattr(self, k)) for k in updates)

        # Handle UUID for old_name/snapshot parameter
        if is_uuid(old_name):
            cmdopts['snapshotid'] = old_name
        else:
            cmdopts['snapshot'] = old_name

            if self.volumegroup:
                cmdopts['volumegroup'] = self.volumegroup
            else:
                cmdopts['parentuid'] = self.parentuid
        self.restapi.svc_run_command(cmd, cmdopts=cmdopts, cmdargs=None)
        self.changed = True

    def delete_snapshot(self):
        if self.module.check_mode:
            self.changed = True
            return

        cmd = 'rmsnapshot'
        cmdopts = {
            'snapshot': self.name
        }
        cmdargs = None
        if is_uuid(self.name):
            cmdopts.pop('snapshot')
            cmdopts['snapshotid'] = self.name
        elif self.volumegroup:
            cmdopts['volumegroup'] = self.volumegroup
        else:
            cmdopts['parentuid'] = self.parentuid

        self.restapi.svc_run_command(cmd, cmdopts=cmdopts, cmdargs=cmdargs)
        self.changed = True

        still_exists = self.is_snapshot_exists(force=True)
        if still_exists:
            self.msg = 'Snapshot ({0}) will be in the dependent_deleting '\
                       'state until those dependencies are removed'.format(self.name)
        else:
            self.msg = 'Snapshot ({0}) deleted.'.format(self.name)

    def apply(self):
        snapshot_data = self.is_snapshot_exists(old_name=self.old_name)
        if snapshot_data:
            if self.state == 'present':
                modifications = self.snapshot_probe()
                if any(modifications):
                    if self.retentionminutes is not None:
                        self.module.fail_json(msg='Invalid parameter retentionminutes for update operation')
                    self.update_snapshot(modifications)
                    self.msg = 'Snapshot ({0}) updated.'.format(self.name)
                else:
                    self.msg = 'Snapshot ({0}) already exists. No modifications done.'.format(self.name)
            elif self.state == 'restore':
                self.restore_from_snapshot(snapshot_data)
                if self.volumes:
                    self.msg = 'Volumes ({0}) of Volumegroup ({1}) restored from Snapshot ({2}).'.\
                        format(self.volumes, self.volumegroup, self.name)
                else:
                    self.msg = 'Volumegroup ({0}) restored from Snapshot ({1}).'.format(self.volumegroup, self.name)
            else:
                self.delete_snapshot()
        else:
            if self.state == 'absent':
                self.msg = 'Snapshot ({0}) does not exist.'.format(self.name)
            elif self.state == 'restore':
                self.module.fail_json(
                    msg='Either snapshot ({0}) does not exist, or snapshot ({0}) is not related to the volumegroup ({1}).'.format(self.name, self.volumegroup)
                )
            else:
                self.create_snapshot()
                self.msg = 'Snapshot ({0}) created.'.format(self.name)

        if self.module.check_mode:
            self.msg = 'skipping changes due to check mode.'

        self.module.exit_json(
            changed=self.changed,
            msg=self.msg
        )


def main():
    v = IBMSVSnapshot()
    try:
        v.apply()
    except Exception as e:
        v.log('Exception in apply(): \n%s', format_exc())
        v.module.fail_json(msg='Module failed. Error [%s].' % to_native(e))


if __name__ == '__main__':
    main()
