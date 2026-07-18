#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2021 IBM CORPORATION
# Author(s): Sandip Gulab Rajbanshi <sandip.rajbanshi@ibm.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: ibm_sv_manage_clone
short_description: This module manages clone and thinclone of volume and volumegroup
version_added: '3.2.0'
description:
  - Ansible interface to manage 'mkvolume' and 'mkvolumegroup' clone commands.
options:
    clustername:
        description:
            - The hostname, management IP or partition IP of the Storage Virtualize system.
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
            - Creates (C(present)) or removes (C(absent)) the clone object.
        choices: [ 'absent', 'present' ]
        required: true
        type: str
    name:
        description:
            - Specifies a name for the new clone.
        required: true
        type: str
    pool:
        description:
            - Specifies the name or UUID of the storage pool to use while creating the clone.
            - The parameters I(pool) is mandatory for clone volumes and optional for clone volume groups while
              creating clone.
        type: str
    iogrp:
        description:
            - Specifies the name of the I/O group for the new clone.
        type: str
    volumegroup:
        description:
            - Specifies the name or UUID of the volumegroup to which the clone is to be added.
            - When logging in via partition IP, the I(volumegroup) parameter is required to create a volume clone.
        type: str
    type:
        description:
            - Specifies the type of clone to create. Volume can be thinclone or clone type.
        choices: [ 'clone', 'thinclone' ]
        type: str
    fromsourcevolumes:
        description:
            - Specifies colon-separated list of the parent volumes name or UID.
            - The parameters I(fromsourcevolumes) is mandatory for clone volumes and optional for clone volume groups
              while creating clone.
        type: str
    snapshot:
        description:
            - Specifies the name or UUID of the snapshot that is used to create the clone.
            - The parameters I(fromsourcevolumes) is mandatory for creating clone.
        type: str
    preferrednode:
        description:
            - Specifies the preferred node that is used to access the volume.
        type: str
    partition:
        description:
            - Specifies the name or UUID of the storage partition to associate with the volume group.
        type: str
    draftpartition:
        description:
            - Specifies the name or UUID of the draft partition to be assigned to the volume group.
        type: str
    ownershipgroup:
        description:
            - Specifies the name of the ownership group to which the object is being added.
        type: str
    ignoreuserfcmaps:
        description:
            - Indicates that snapshots can be created with the scheduler or with the addsnapshot command,
              if any volumes in the volume group are used as a source volume in legacy FlashCopy mapping.
        choices: [ 'yes', 'no' ]
        type: str
    validate_certs:
        description:
            - Validates certification.
        default: false
        type: bool
author:
    - Sandip G. Rajbanshi (@Sandip-Rajbanshi)
notes:
    - This module supports C(check_mode).
    - This module currently only supports the creation of clone volume or volumegroup (C(state=present)).
    - Support for updating or removing these clone objects may be added in a future release. For updating (converting
      thinclone to clone) or removing thinclone or clone for volume and volumegroup, use the I(ibm_svc_manage_volume) or
      I(ibm_svc_manage_volumegroup) modules, respectively.
    - This module supports log-in via partition-ip.
'''

EXAMPLES = r'''
- name: Create a clone of a volume from snapshot
  ibm.storage_virtualize.ibm_sv_manage_clone:
    clustername: "{{ clustername }}"
    domain: "{{ domain }}"
    username: "{{ username }}"
    password: "{{ password }}"
    log_path: "{{ log_path }}"
    name: "vol1_clone_1"
    state: "present"
    pool: "pool1"
    type: "clone"
    snapshot: "snapshot1"
    fromsourcevolumes: "vol1"
    iogrp: "io_grp0"
    preferrednode: "node1"
    volumegroup: "Vg1"
- name: Create a clone of a volumegroup from snapshot
  ibm.storage_virtualize.ibm_sv_manage_clone:
    clustername: "{{ clustername }}"
    domain: "{{ domain }}"
    username: "{{ username }}"
    password: "{{ password }}"
    log_path: "{{ log_path }}"
    name: "vg1_clone_1"
    state: "present"
    pool: "pool1"
    type: "clone"
    snapshot: "snapshot1"
    iogrp: "io_grp0"
    partition: "ptn1"
    ownershipgroup: "grp1"
- name: Create a clone of a volumegroup from snapshot inside partition
  ibm.storage_virtualize.ibm_sv_manage_clone:
    clustername: "{{ clustername }}"
    domain: "{{ domain }}"
    username: "{{ username }}"
    password: "{{ password }}"
    log_path: "{{ log_path }}"
    name: "vg1_clone_uuid_1"
    state: "present"
    pool: "pool1"
    type: "clone"
    snapshot: "snapshot1"
    iogrp: "io_grp0"
    partition: "123e4567-e89b-12d3-a456-426614174000"
    ownershipgroup: "grp1"
- name: Create a volume clone using volumegroup
  ibm.storage_virtualize.ibm_sv_manage_clone:
    clustername: "{{ clustername }}"
    domain: "{{ domain }}"
    username: "{{ username }}"
    password: "{{ password }}"
    log_path: "{{ log_path }}"
    name: "vol1_clone_uuid_1"
    state: "present"
    pool: "pool1"
    type: "clone"
    snapshot: "snapshot1"
    fromsourcevolumes: "vol1"
    iogrp: "io_grp0"
    preferrednode: "node1"
    volumegroup: "550e8400-e29b-41d4-a716-446655440000"
- name: Create a clone of volume vector from snapshot
  ibm.storage_virtualize.ibm_sv_manage_clone:
    clustername: "{{ clustername }}"
    domain: "{{ domain }}"
    username: "{{ username }}"
    password: "{{ password }}"
    log_path: "{{ log_path }}"
    name: "vg1_clone_1"
    state: "present"
    fromsourcevolumes: "vol1:vol2:vol3"
    pool: "pool1"
    type: "clone"
    snapshot: "snapshot1"
    iogrp: "io_grp0"
    partition: "ptn1"
    ownershipgroup: "grp1"
- name: Create a clone of a volume with pool UUID
  ibm.storage_virtualize.ibm_sv_manage_clone:
    clustername: "{{ clustername }}"
    username: "{{ username }}"
    password: "{{ password }}"
    log_path: "{{ log_path }}"
    name: "vol1_clone_pool_uuid"
    state: "present"
    pool: "66197B52-9707-548D-8C42-E91A7D35F6B8"
    type: "clone"
    snapshot: "snapshot1"
    fromsourcevolumes: "vol1"
- name: Create a clone of a volume with snapshot UUID
  ibm.storage_virtualize.ibm_sv_manage_clone:
    clustername: "{{ clustername }}"
    username: "{{ username }}"
    password: "{{ password }}"
    log_path: "{{ log_path }}"
    name: "vol1_clone_snap_uuid"
    state: "present"
    pool: "pool1"
    type: "clone"
    snapshot: 66197B52-9707-548D-8C42-E91A7D35F6B8
    fromsourcevolumes: "vol1"
- name: Create a clone from source volumes using UIDs
  ibm.storage_virtualize.ibm_sv_manage_clone:
    clustername: "{{ clustername }}"
    username: "{{ username }}"
    password: "{{ password }}"
    log_path: "{{ log_path }}"
    name: "vg1_clone_from_uuid_vols"
    state: "present"
    fromsourcevolumes: 6005076400810261F80000000000027E:6005076400810261F80000000000027D
    pool: "pool1"
    type: "clone"
    snapshot: "snapshot1"
- name: Create a clone with volumegroup UUID
  ibm.storage_virtualize.ibm_sv_manage_clone:
    clustername: "{{ clustername }}"
    username: "{{ username }}"
    password: "{{ password }}"
    log_path: "{{ log_path }}"
    name: "vol1_clone_vg_uuid"
    state: "present"
    pool: "pool1"
    type: "clone"
    snapshot: "snapshot1"
    fromsourcevolumes: "vol1"
    volumegroup: 66197B52-9707-548D-8C42-E91A7D35F6B8
- name: Create a clone with partition UUID
  ibm.storage_virtualize.ibm_sv_manage_clone:
    clustername: "{{ clustername }}"
    username: "{{ username }}"
    password: "{{ password }}"
    log_path: "{{ log_path }}"
    name: "vg1_clone_partition_uuid"
    state: "present"
    pool: "pool1"
    type: "clone"
    snapshot: "snapshot1"
    partition: 66197B52-9707-548D-8C42-E91A7D35F6B8
- name: Create a clone with draft partition UUID
  ibm.storage_virtualize.ibm_sv_manage_clone:
    clustername: "{{ clustername }}"
    username: "{{ username }}"
    password: "{{ password }}"
    log_path: "{{ log_path }}"
    name: "vg1_clone_draft_partition_uuid"
    state: "present"
    pool: "pool1"
    type: "clone"
    snapshot: "snapshot1"
    draftpartition: 66197B52-9707-548D-8C42-E91A7D35F6B8
'''

RETURN = '''#'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils import (
    IBMSVCRestApi,
    svc_argument_spec,
    get_logger,
    is_uuid
)
from ansible.module_utils._text import to_native

UUID = 'uuid'


class IBMSVClone(object):
    def __init__(self):
        argument_spec = svc_argument_spec()

        argument_spec.update(
            dict(
                name=dict(type='str', required=True),
                state=dict(type='str', required=True, choices=['absent', 'present']),
                pool=dict(type='str', required=False),
                iogrp=dict(type='str', required=False),
                volumegroup=dict(type='str', required=False),
                type=dict(type='str', required=False, choices=['clone', 'thinclone']),
                fromsourcevolumes=dict(type='str', required=False),
                log_path=dict(type='str', required=False),
                snapshot=dict(type='str', required=False),
                preferrednode=dict(type='str', required=False),
                partition=dict(type='str', required=False),
                ownershipgroup=dict(type='str', required=False),
                ignoreuserfcmaps=dict(type='str', required=False, choices=['yes', 'no']),
                draftpartition=dict(type='str', required=False)
            )
        )

        self.module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

        # logging setup
        log_path = self.module.params['log_path']
        log = get_logger(self.__class__.__name__, log_path)
        self.log = log.info

        # Required Parameters
        self.name = self.module.params['name']
        self.state = self.module.params['state']

        # Optional Parameters
        self.pool = self.module.params.get('pool', "")
        self.iogrp = self.module.params.get('iogrp', "")
        self.volumegroup = self.module.params.get('volumegroup', "")
        self.type = self.module.params.get('type', "")
        self.fromsourcevolumes = self.module.params.get('fromsourcevolumes', "")
        self.fromsourcevolumes_list = self.fromsourcevolumes.split(':') if self.fromsourcevolumes else []
        self.snapshot = self.module.params.get('snapshot', "")
        self.preferrednode = self.module.params.get('preferrednode', "")
        self.partition = self.module.params.get('partition', "")
        self.ownershipgroup = self.module.params.get('ownershipgroup', "")
        self.ignoreuserfcmaps = self.module.params.get('ignoreuserfcmaps', "")
        self.draftpartition = self.module.params.get('draftpartition', "")

        # internal variable
        self.changed = False
        self.msg = ""
        self.OBJECT_TYPE = None

        self.basic_checks()

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
        if len(self.fromsourcevolumes_list) == 1:
            self.OBJECT_TYPE = 'volume'
        else:
            self.OBJECT_TYPE = 'volumegroup'
        if self.state == 'present':
            if self.OBJECT_TYPE == 'volume':
                invalids = ('partition', 'ownershipgroup', 'ignoreuserfcmaps', 'draftpartition')
                invalid_exists = ', '.join((var for var in invalids if not getattr(self, var) in {'', None}))
                if invalid_exists:
                    self.module.fail_json(
                        msg='Volume clone operation does not support the parameter(s): {0}'.format(invalid_exists)
                    )
            else:
                invalids = ('volumegroup', 'preferrednode')
                invalid_exists = ', '.join((var for var in invalids if not getattr(self, var) in {'', None}))
                if invalid_exists:
                    self.module.fail_json(
                        msg='Volumegroup clone operation does not support the parameter(s): {0}'.format(invalid_exists)
                    )
        else:
            self.module.fail_json(
                msg="Removal of clone is not supported via this module. Please use ibm_svc_manage_volume or"
                " ibm_svc_manage_volumegroup for removing volume or volumegroup clone/thinclone respectively.")

    def get_existing_clone(self):
        merged_result = {}
        cmd = "lsvdisk" if self.OBJECT_TYPE == "volume" else "lsvolumegroup"
        data = self.restapi.svc_obj_info(cmd, {"bytes": True}, [self.name])

        if isinstance(data, list):
            for d in data:
                merged_result.update(d)
        else:
            merged_result = data
        return merged_result

    # Funciton to check whether all volumes inside the volumegroup belonging to the same pool
    def check_volumes_in_pool(self, vg_name, pool):
        vol_list = self.restapi.svc_obj_info("lsvdisk", {"filtervalue" : "volume_group_name=%s" % vg_name}, [])
        for vol in vol_list:
            if self.fromsourcevolumes_list and vol.get("name") not in self.fromsourcevolumes_list:
                continue
            if pool != vol.get("mdisk_grp_name"):
                if is_uuid(pool):
                    vol_pool_uuid = self.restapi.svc_obj_info('lsmdiskgrp', cmdopts=None, cmdargs=[vol.get("mdisk_grp_name")]).get(UUID, '')
                    if pool != vol_pool_uuid:
                        self.log("One or more volumes belonging to volumegroup (%s) are in different pool", vg_name)
                        return False
                else:
                    vol_pool_name = vol.get("mdisk_grp_name")
                    if pool != vol_pool_name:
                        self.log("One or more volumes belonging to volumegroup (%s) are in different pool", vg_name)
                        return False
        return True

    def get_parent_uid_or_source_grp_from_snapshot(self):
        parent_uid = None
        source_grp_name = None
        if self.OBJECT_TYPE == "volume":
            snapshot_data = self.restapi.svc_obj_info(
                'lsvolumesnapshot', {'filtervalue': "snapshot_name=%s" % self.snapshot}, []
            )
            if snapshot_data:
                source_grp_name = snapshot_data[0].get('volume_group_name')
                parent_uid = snapshot_data[0].get('parent_uid')
        else:
            snapshot_data = self.restapi.svc_obj_info(
                'lsvolumegroupsnapshot', {}, []
            )
            for snapshot in snapshot_data:
                if snapshot.get('name') == self.snapshot:
                    source_grp_name = snapshot.get('volume_group_name')
                    parent_uid = snapshot.get('parent_uid')
                    break
        if not parent_uid:
            self.module.fail_json(
                msg="Snapshot %s does not exist." % self.snapshot
            )
        if source_grp_name:
            return (source_grp_name, None)
        return (None, parent_uid)

    def create_validation(self):
        required_params = {
            "snapshot": self.snapshot,
            "type": self.type
        }
        if self.OBJECT_TYPE == 'volume':
            required_params["pool"] = self.pool

        missing = [k for k, v in required_params.items() if not v]

        if missing:
            self.module.fail_json(
                msg="Following parameters are required while creating clone: {}".format(
                    ", ".join(missing)
                )
            )

    def create_clone(self):
        self.create_validation()
        cmdopts = {
            'name': self.name,
            'type': self.type,
        }
        if is_uuid(self.snapshot):
            cmdopts['fromsnapshotid'] = self.snapshot
        else:
            source_grp_name, parent_uid = self.get_parent_uid_or_source_grp_from_snapshot()
            cmdopts['snapshot'] = self.snapshot
            if source_grp_name:
                cmdopts['fromsourcegroup'] = source_grp_name
            elif parent_uid:
                cmdopts['fromsourceuid'] = parent_uid

        if self.OBJECT_TYPE == 'volume':
            cmd = 'mkvolume'
            cmdopts['fromsourcevolume'] = self.fromsourcevolumes
            if self.iogrp:
                cmdopts['iogrp'] = self.iogrp
        else:
            cmd = 'mkvolumegroup'
            if self.fromsourcevolumes:
                cmdopts['fromsourcevolumes'] = self.fromsourcevolumes
            if self.iogrp:
                cmdopts['iogroup'] = self.iogrp

        # Optional fields (add only if defined)
        optional_fields = {
            'pool': self.pool,
            'volumegroup': self.volumegroup,
            'preferrednode': self.preferrednode,
            'partition': self.partition,
            'ownershipgroup': self.ownershipgroup,
            'ignoreuserfcmaps': self.ignoreuserfcmaps,
            'draftpartition': self.draftpartition
        }

        for key, value in optional_fields.items():
            if value:
                cmdopts[key] = value

        # Execute the command
        self.restapi.svc_run_command(cmd, cmdopts, cmdargs=None)
        self.log('Clone (%s) created successfully.', self.name)
        self.changed = True

    def probe(self, clone_data):
        params_mapping = (
            ('ownershipgroup', clone_data.get('owner_name', '')),
            ('ignoreuserfcmaps', clone_data.get('ignore_user_fc_maps', '')),
            ('volumegroup', clone_data.get('volume_group_name', '')),
            ('iogrp', clone_data.get('IO_group_name', '')),
            ('partition', clone_data.get('partition_name', '')),
            ('preferrednode', clone_data.get('preferred_node_name', '')),
            ('pool', clone_data.get('mdisk_grp_name', '')),
            ('snapshot', clone_data.get('source_snapshot', '')),
            ('draftpartition', clone_data.get('draft_partition_name', ''))
        )

        props = dict((k, getattr(self, k)) for k, v in params_mapping if getattr(self, k) and getattr(self, k) != v)
        # Check for type changes if volume is present but type is different
        if self.OBJECT_TYPE == 'volume':
            # Handle fromsourcevolumes UUID comparison
            if is_uuid(self.fromsourcevolumes):
                source_vol_name = clone_data.get('source_volume_name', '')
                if source_vol_name:
                    source_vol_uuid = self.restapi.svc_obj_info('lsvdisk', cmdopts=None, cmdargs=[source_vol_name]).get('volume_UID', '')
                    if source_vol_uuid != self.fromsourcevolumes:
                        self.module.fail_json(
                            msg="Specified fromsourcevolumes does not match with existing clone's source volume."
                        )
            elif clone_data.get('source_volume_name') != self.fromsourcevolumes:
                self.module.fail_json(
                    msg="Specified fromsourcevolumes does not match with existing clone's source volume."
                )
            if is_uuid(self.pool) and 'pool' in props:
                pool_uuid = self.restapi.svc_obj_info('lsmdiskgrp', cmdopts=None, cmdargs=[clone_data.get('mdisk_grp_name', '')]).get(UUID, '')
                if pool_uuid == self.pool:
                    del props['pool']

            if is_uuid(self.volumegroup) and 'volumegroup' in props:
                vg_uuid = self.restapi.svc_obj_info('lsvolumegroup', cmdopts=None, cmdargs=[clone_data.get('volume_group_name', '')]).get(UUID, '')
                if vg_uuid == self.volumegroup:
                    del props['volumegroup']

        else:
            if 'pool' in props:
                # volumegroup's pool cannot be changed after creation
                if self.check_volumes_in_pool(self.name, self.pool):
                    del props['pool']

            if is_uuid(self.partition) and 'partition' in props:
                ptn_uuid = self.restapi.svc_obj_info('lspartition', cmdopts=None, cmdargs=[clone_data.get('partition_name', '')]).get(UUID, '')
                if ptn_uuid == self.partition:
                    del props['partition']

            if is_uuid(self.draftpartition) and 'draftpartition' in props and clone_data.get('draft_partition_name'):
                ptn_uuid = self.restapi.svc_obj_info('lspartition', cmdopts=None, cmdargs=[clone_data.get('draft_partition_name', '')]).get(UUID, '')
                if ptn_uuid == self.draftpartition:
                    del props['draftpartition']

        vol_type = clone_data.get('volume_type')
        vg_type = clone_data.get('volume_group_type')
        source_type = vol_type if vol_type is not None else vg_type

        # Normalize empty ⇒ treat as "clone"
        if source_type in ("", None):
            source_type = "clone"

        # Both conditions assign props['type'] = self.type
        if (source_type == "clone" and self.type == "thinclone") or \
           (source_type == "thinclone" and self.type == "clone"):
            props["type"] = self.type
        # If source type is clone, source_snapshot is not identifiable
        if source_type == "clone":
            if "snapshot" in props:
                del props["snapshot"]
        else:
            if is_uuid(self.snapshot) and 'snapshot' in props:
                source_snap = clone_data.get('source_snapshot', '')
                if source_snap:
                    if self.OBJECT_TYPE == 'volume':
                        snap_uuid = self.restapi.svc_obj_info('lsvolumesnapshot', cmdopts=None, cmdargs=[source_snap]).get(UUID, '')
                    else:
                        snap_uuid = self.restapi.svc_obj_info('lsvolumegroupsnapshot', cmdopts=None, cmdargs=[source_snap]).get(UUID, '')
                    if snap_uuid == self.snapshot:
                        del props['snapshot']

        return props

    def apply(self):
        clone_data = self.get_existing_clone()
        if clone_data:
            self.log("Existing clone data: %s", clone_data)
            # Volume already exists
            if self.state == 'present':
                modifications = self.probe(clone_data)
                if modifications:
                    self.log("Modifications detected: %s", modifications)
                    self.module.fail_json(
                        msg="Modifications of clone is not supported via this module, Please use ibm_svc_manage_volume or"
                            " ibm_svc_manage_volumegroup for modifying volume or volumegroup clone/thinclone respectively.")
                else:
                    self.msg = "Clone %s already exists, no modification required." % self.name
        else:
            self.create_clone()
            self.changed = True
            self.msg = "Clone %s created." % self.name
        self.module.exit_json(msg=self.msg, changed=self.changed)


def main():
    v = IBMSVClone()
    try:
        v.apply()
    except Exception as e:
        v.log("Exception in apply(): \n%s", format_exc())
        v.module.fail_json(msg="Module failed. Error [%s]." % to_native(e))


if __name__ == '__main__':
    main()
