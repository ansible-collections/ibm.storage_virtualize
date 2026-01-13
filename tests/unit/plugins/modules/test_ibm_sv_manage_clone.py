# Copyright (C) 2023 IBM CORPORATION
# Author(s):  Sandip Gulab Rajbanshi <sandip.rajbanshi@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Storage Virtualize Ansible module: ibm_sv_manage_clone """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.storage_virtualize.plugins.modules.ibm_sv_manage_clone import IBMSVClone
import contextlib


@contextlib.contextmanager
def set_module_args(args):
    """
    Context manager that sets module arguments for AnsibleModule
    """
    if '_ansible_remote_tmp' not in args:
        args['_ansible_remote_tmp'] = '/tmp'
    if '_ansible_keep_remote_files' not in args:
        args['_ansible_keep_remote_files'] = False

    try:
        from ansible.module_utils.testing import patch_module_args
        with patch_module_args(args):
            yield
    except ImportError:
        from ansible.module_utils import basic
        serialized_args = to_bytes(json.dumps({'ANSIBLE_MODULE_ARGS': args}))
        with patch.object(basic, '_ANSIBLE_ARGS', serialized_args):
            yield


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the
    test case """
    pass


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the
    test case """
    pass


def exit_json(*args, **kwargs):  # pylint: disable=unused-argument
    """function to patch over exit_json; package return data into an
    exception """
    if 'changed' not in kwargs:
        kwargs['changed'] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    """function to patch over fail_json; package return data into an
    exception """
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


class TestIBMSVClone(unittest.TestCase):
    """ Test class for ibm_sv_manage_drive module """
    """
    Group of related Unit Tests
    """

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def setUp(self, connect):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)
        self.restapi = IBMSVCRestApi(self.mock_module_helper, '1.2.3.4',
                                     'domain.ibm.com', 'username', 'password',
                                     False, 'test.log', '')

    def test_module_with_blank_values(self):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': ''
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                IBMSVClone()
            self.assertTrue(exc.value.args[0]['failed'])

    def test_module_with_invalid_params_1(self):
        '''
        partition, ownershipgroup, ignoreuserfcmaps parameters are invalid in case of volume clone
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'clone_name_01',
            'state': 'present',
            'type': 'clone',
            'snapshot': 'snapshot_id_1234',
            'pool': 'pool1',
            'fromsourcevolumes': "test_vol_3",
            'partition': 'partition1',
            'ownershipgroup': 'group1',
            'ignoreuserfcmaps': 'yes'
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                clone = IBMSVClone()
                clone.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'],
                             "Volume clone operation does not support the parameter(s): partition, "
                             "ownershipgroup, ignoreuserfcmaps")

    def test_module_with_invalid_params_2(self):
        '''
        volumegroup, preferrednode parameters are invalid in case of volumegroup clone
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'clone_name_01',
            'state': 'present',
            'type': 'clone',
            'snapshot': 'snapshot_id_1234',
            'pool': 'pool1',
            'volumegroup': 'vg1',
            'preferrednode': "node1"
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                clone = IBMSVClone()
                clone.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'],
                             "Volumegroup clone operation does not support the parameter(s): volumegroup, preferrednode")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_clone.IBMSVClone.get_parent_uid_or_source_grp_from_snapshot')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_clone.IBMSVClone.get_existing_clone')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_clone_volume(self, svc_authorize_mock,
                                 get_existing_clone_mock,
                                 get_parent_uid_or_source_grp_from_snapshot_mock,
                                 svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'clone_name_01',
            'state': 'present',
            'type': 'clone',
            'snapshot': 'snapshot_id_1234',
            'pool': 'pool1',
            'fromsourcevolumes': "test_vol_3"
        }):
            get_existing_clone_mock.return_value = {}
            get_parent_uid_or_source_grp_from_snapshot_mock.return_value = (None, "111")
            svc_run_command_mock.return_value = ""
            clone = IBMSVClone()
            with pytest.raises(AnsibleExitJson) as exc:
                clone.apply()
            self.assertTrue(exc.value.args[0]['changed'])
            args, kwargs = svc_run_command_mock.call_args
            self.assertEqual(args[0], 'mkvolume')

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_clone.IBMSVClone.get_existing_clone')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_clone_volume_idempotency(self, svc_authorize_mock,
                                             get_existing_clone_mock):
        get_existing_clone_mock.return_value = {
            "id": "61", "name": "clone_name_01", "IO_group_id": "0",
            "IO_group_name": "io_grp0", "status": "online", "mdisk_grp_id": "0",
            "mdisk_grp_name": "pool1", "capacity": "1.00GB", "type": "striped",
            "vdisk_UID": "6005076812B7018CB0000000000001B9", "fc_map_count": "0",
            "sync_rate": "50", "copy_count": "1", "se_copy_count": "0", "preferred_node_id": "1",
            "fast_write_state": "empty", "cache": "readwrite", "udid": "",
            "parent_mdisk_grp_id": "0", "parent_mdisk_grp_name": "pool1",
            "owner_type": "none", "owner_id": "", "owner_name": "", "encrypt": "no",
            "volume_id": "61", "volume_name": "nclone_name_01", "function": "",
            "preferred_node_name": "node1", "safeguarded_expiration_time": "",
            "safeguarded_backup_count": "0", "is_snapshot": "no", "snapshot_count": "0",
            "volume_type": "clone", "source_volume_id": "15", "source_volume_name": "test_vol_3",
            "source_snapshot": "snapshot_id_1234", "source_snapshot_timestamp": "",
            "protection_provisioned_capacity": "0.00MB"}

        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'clone_name_01',
            'state': 'present',
            'type': 'clone',
            'snapshot': 'snapshot_id_1234',
            'pool': 'pool1',
            'fromsourcevolumes': "test_vol_3"
        }):
            with pytest.raises(AnsibleExitJson) as exc:
                clone = IBMSVClone()
                clone.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_clone.IBMSVClone.get_existing_clone')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_unsupported_remove_clone(self, svc_authorize_mock,
                                      get_existing_clone_mock):
        get_existing_clone_mock.return_value = {
            "id": "61", "name": "clone_name_01", "IO_group_id": "0",
            "IO_group_name": "io_grp0", "status": "online", "mdisk_grp_id": "0",
            "mdisk_grp_name": "pool1", "capacity": "1.00GB", "type": "striped",
            "vdisk_UID": "6005076812B7018CB0000000000001B9", "fc_map_count": "0",
            "sync_rate": "50", "copy_count": "1", "se_copy_count": "0", "preferred_node_id": "1",
            "fast_write_state": "empty", "cache": "readwrite", "udid": "",
            "parent_mdisk_grp_id": "0", "parent_mdisk_grp_name": "pool1",
            "owner_type": "none", "owner_id": "", "owner_name": "", "encrypt": "no",
            "volume_id": "61", "volume_name": "nclone_name_01", "function": "",
            "preferred_node_name": "node1", "safeguarded_expiration_time": "",
            "safeguarded_backup_count": "0", "is_snapshot": "no", "snapshot_count": "0",
            "volume_type": "clone", "source_volume_id": "15", "source_volume_name": "test_vol_3",
            "source_snapshot": "snapshot_id_1234", "source_snapshot_timestamp": "",
            "protection_provisioned_capacity": "0.00MB"}

        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'clone_name_01',
            'state': 'absent',
            'type': 'clone',
            'snapshot': 'snapshot_id_1234',
            'pool': 'pool1'
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                clone = IBMSVClone()
                clone.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'],
                             "Removal of clone is not supported via this module. Please use ibm_svc_manage_volume or "
                             "ibm_svc_manage_volumegroup for removing volume or volumegroup clone/thinclone respectively.")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_clone.IBMSVClone.get_existing_clone')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_unsupported_update_volume_thinclone_to_clone(self, svc_authorize_mock,
                                                          get_existing_clone_mock):
        get_existing_clone_mock.return_value = {
            "id": "61", "name": "clone_name_01", "IO_group_id": "0",
            "IO_group_name": "io_grp0", "status": "online", "mdisk_grp_id": "0",
            "mdisk_grp_name": "site1pool1", "capacity": "1.00GB", "type": "striped",
            "vdisk_UID": "6005076812B7018CB0000000000001B9", "fc_map_count": "0",
            "sync_rate": "50", "copy_count": "1", "se_copy_count": "0", "preferred_node_id": "1",
            "fast_write_state": "empty", "cache": "readwrite", "udid": "",
            "parent_mdisk_grp_id": "0", "parent_mdisk_grp_name": "site1pool1",
            "owner_type": "none", "owner_id": "", "owner_name": "", "encrypt": "no",
            "volume_id": "61", "volume_name": "nclone_name_01", "function": "",
            "preferred_node_name": "node1", "safeguarded_expiration_time": "",
            "safeguarded_backup_count": "0", "is_snapshot": "no", "snapshot_count": "0",
            "volume_type": "thinclone", "source_volume_id": "15", "source_volume_name": "test_vol_1",
            "source_snapshot": "snapshot_id_1234", "source_snapshot_timestamp": "",
            "protection_provisioned_capacity": "0.00MB"}

        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'clone_name_01',
            'state': 'present',
            'type': 'clone',
            'snapshot': 'snapshot_id_1234',
            'fromsourcevolumes': "test_vol_1"
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                clone = IBMSVClone()
                clone.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'],
                             "Modifications of clone is not supported via this module, Please use ibm_svc_manage_volume or "
                             "ibm_svc_manage_volumegroup for modifying volume or volumegroup clone/thinclone respectively.")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_clone.IBMSVClone.get_existing_clone')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_unsupported_update_volume_source_snapshot(self, svc_authorize_mock,
                                                       get_existing_clone_mock):
        get_existing_clone_mock.return_value = {
            "id": "61", "name": "clone_name_01", "IO_group_id": "0",
            "IO_group_name": "io_grp0", "status": "online", "mdisk_grp_id": "0",
            "mdisk_grp_name": "site1pool1", "capacity": "1.00GB", "type": "striped",
            "vdisk_UID": "6005076812B7018CB0000000000001B9", "fc_map_count": "0",
            "sync_rate": "50", "copy_count": "1", "se_copy_count": "0", "preferred_node_id": "1",
            "fast_write_state": "empty", "cache": "readwrite", "udid": "",
            "parent_mdisk_grp_id": "0", "parent_mdisk_grp_name": "site1pool1",
            "owner_type": "none", "owner_id": "", "owner_name": "", "encrypt": "no",
            "volume_id": "61", "volume_name": "nclone_name_01", "function": "",
            "preferred_node_name": "node1", "safeguarded_expiration_time": "",
            "safeguarded_backup_count": "0", "is_snapshot": "no", "snapshot_count": "0",
            "volume_type": "thinclone", "source_volume_id": "15", "source_volume_name": "test_vol_1",
            "source_snapshot": "snapshot_id_1235", "source_snapshot_timestamp": "",
            "protection_provisioned_capacity": "0.00MB"}

        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'clone_name_01',
            'state': 'present',
            'type': 'thinclone',
            'snapshot': 'snapshot_id_1234',
            'fromsourcevolumes': "test_vol_1"
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                clone = IBMSVClone()
                clone.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'],
                             "Modifications of clone is not supported via this module, Please use ibm_svc_manage_volume or "
                             "ibm_svc_manage_volumegroup for modifying volume or volumegroup clone/thinclone respectively.")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_clone.IBMSVClone.get_parent_uid_or_source_grp_from_snapshot')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_clone.IBMSVClone.get_existing_clone')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_clone_volumegroup(self, svc_authorize_mock,
                                      get_existing_clone_mock,
                                      get_parent_uid_or_source_grp_from_snapshot_mock,
                                      svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'clone_name_01',
            'state': 'present',
            'type': 'clone',
            'snapshot': 'snapshot_id_1234',
            'pool': 'pool1'
        }):
            get_existing_clone_mock.return_value = {}
            get_parent_uid_or_source_grp_from_snapshot_mock.return_value = ('vg1', None)
            svc_run_command_mock.return_value = ""
            clone = IBMSVClone()
            with pytest.raises(AnsibleExitJson) as exc:
                clone.apply()
            self.assertTrue(exc.value.args[0]['changed'])
            args, kwargs = svc_run_command_mock.call_args
            self.assertEqual(args[0], 'mkvolumegroup')

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_clone.IBMSVClone.check_volumes_in_pool')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_clone.IBMSVClone.get_existing_clone')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_clone_volumegroup_idempotency(self, svc_authorize_mock,
                                                  get_existing_clone_mock,
                                                  check_volumes_in_pool_mock):
        get_existing_clone_mock.return_value = {
            "id": "1", "name": "clone_name_01", "volume_count": "4",
            "backup_status": "off", "last_backup_time": "", "owner_id": "",
            "owner_name": "", "safeguarded_policy_id": "", "safeguarded_policy_name": "",
            "safeguarded_policy_start_time": "", "replication_policy_id": "",
            "replication_policy_name": "", "ha_replication_policy_id": "0",
            "ha_replication_policy_name": "ha-policy-0", "volume_group_type": "clone",
            "uid": "99", "source_volume_group_id": "", "source_volume_group_name": "",
            "parent_uid": "", "source_snapshot_id": "", "source_snapshot": "snapshot_id_1234",
            "snapshot_count": "0", "protection_provisioned_capacity": "4.00GB",
            "protection_written_capacity": "3.00MB", "snapshot_policy_id": "",
            "snapshot_policy_name": "", "snapshot_policy_uuid": "26CDECD0-5625-0000-5002-000000000000",
            "safeguarded_snapshot_count": "0", "ignore_user_flash_copy_maps": "no",
            "partition_id": "0", "partition_name": "ptn_test", "restore_in_progress": "no",
            "owner_type": "none", "draft_partition_id": "", "draft_partition_name": "",
            "last_restore_time": "", "dr_replicated": "no", "partition_default": "no",
            "host_provisioned_capacity": "4.00GB", "anomaly_sequence_number": "",
            "uuid": "9C16DE02-1F11-528A-B978-805E906C5B3B"}

        volume_list = [
            {"id": "61", "name": "clone_vol_01", "IO_group_id": "0",
             "IO_group_name": "io_grp0", "status": "online", "mdisk_grp_id": "0",
             "mdisk_grp_name": "pool1", "capacity": "1.00GB", "type": "striped",
             "volume_type": "clone", "source_volume_id": "15", "source_volume_name": "test_vol_1",
             "source_snapshot": "snapshot_id_1234"},
            {"id": "62", "name": "clone_vol_02", "IO_group_id": "0",
             "IO_group_name": "io_grp0", "status": "online", "mdisk_grp_id": "0",
             "mdisk_grp_name": "pool1", "capacity": "1.00GB", "type": "striped",
             "volume_type": "clone", "source_volume_id": "15", "source_volume_name": "test_vol_2",
             "source_snapshot": "snapshot_id_1234"},
            {"id": "63", "name": "clone_vol_03", "IO_group_id": "0",
             "IO_group_name": "io_grp0", "status": "online", "mdisk_grp_id": "0",
             "mdisk_grp_name": "pool1", "capacity": "1.00GB", "type": "striped",
             "volume_type": "clone", "source_volume_id": "15", "source_volume_name": "test_vol_3",
             "source_snapshot": "snapshot_id_1234"},
            {"id": "64", "name": "clone_vol_04", "IO_group_id": "0",
             "IO_group_name": "io_grp0", "status": "online", "mdisk_grp_id": "0",
             "mdisk_grp_name": "pool1", "capacity": "1.00GB", "type": "striped",
             "volume_type": "clone", "source_volume_id": "15", "source_volume_name": "test_vol_4",
             "source_snapshot": "snapshot_id_1234"}]

        check_volumes_in_pool_mock.return_value = volume_list

        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'clone_name_01',
            'state': 'present',
            'type': 'clone',
            'snapshot': 'snapshot_id_1234',
            'pool': 'pool1'
        }):
            with pytest.raises(AnsibleExitJson) as exc:
                clone = IBMSVClone()
                clone.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_clone.IBMSVClone.get_parent_uid_or_source_grp_from_snapshot')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_clone.IBMSVClone.get_existing_clone')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_clone_volume_vector(self, svc_authorize_mock,
                                        get_existing_clone_mock,
                                        get_parent_uid_or_source_grp_from_snapshot_mock,
                                        svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'clone_name_01',
            'state': 'present',
            'type': 'clone',
            'snapshot': 'snapshot_id_1234',
            'pool': 'pool1',
            'fromsourcevolumes': "test_vol_1:test_vol_2"
        }):
            get_existing_clone_mock.return_value = {}
            get_parent_uid_or_source_grp_from_snapshot_mock.return_value = ('vg1', None)
            svc_run_command_mock.return_value = ""
            clone = IBMSVClone()
            with pytest.raises(AnsibleExitJson) as exc:
                clone.apply()
            self.assertTrue(exc.value.args[0]['changed'])
            args, kwargs = svc_run_command_mock.call_args
            self.assertEqual(args[0], 'mkvolumegroup')

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_clone.IBMSVClone.get_existing_clone')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_clone_volume_vector_idempotency(self, svc_authorize_mock,
                                                    get_existing_clone_mock):
        get_existing_clone_mock.return_value = {
            "id": "1", "name": "clone_name_01", "volume_count": "2",
            "backup_status": "off", "last_backup_time": "", "owner_id": "",
            "owner_name": "", "safeguarded_policy_id": "", "safeguarded_policy_name": "",
            "safeguarded_policy_start_time": "", "replication_policy_id": "",
            "replication_policy_name": "", "ha_replication_policy_id": "0",
            "ha_replication_policy_name": "ha-policy-0", "volume_group_type": "clone",
            "uid": "99", "source_volume_group_id": "", "source_volume_group_name": "",
            "parent_uid": "", "source_snapshot_id": "", "source_snapshot": "snapshot_id_1234",
            "snapshot_count": "0", "protection_provisioned_capacity": "4.00GB",
            "protection_written_capacity": "3.00MB", "snapshot_policy_id": "",
            "snapshot_policy_name": "", "snapshot_policy_uuid": "26CDECD0-5625-0000-5002-000000000000",
            "safeguarded_snapshot_count": "0", "ignore_user_flash_copy_maps": "no",
            "partition_id": "0", "partition_name": "ptn_test", "restore_in_progress": "no",
            "owner_type": "none", "draft_partition_id": "", "draft_partition_name": "",
            "last_restore_time": "", "dr_replicated": "no", "partition_default": "no",
            "host_provisioned_capacity": "4.00GB", "anomaly_sequence_number": "",
            "uuid": "9C16DE02-1F11-528A-B978-805E906C5B3B"}

        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'clone_name_01',
            'state': 'present',
            'type': 'clone',
            'snapshot': 'snapshot_id_1234',
            'fromsourcevolumes': "test_vol_1:test_vol_2"
        }):
            with pytest.raises(AnsibleExitJson) as exc:
                clone = IBMSVClone()
                clone.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_clone.IBMSVClone.get_existing_clone')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_unsupported_update_volumegroup_thinclone_to_clone(self, svc_authorize_mock,
                                                               get_existing_clone_mock):
        get_existing_clone_mock.return_value = {
            "id": "1", "name": "clone_name_01", "volume_count": "2",
            "backup_status": "off", "last_backup_time": "", "owner_id": "",
            "owner_name": "", "safeguarded_policy_id": "", "safeguarded_policy_name": "",
            "safeguarded_policy_start_time": "", "replication_policy_id": "",
            "replication_policy_name": "", "ha_replication_policy_id": "0",
            "ha_replication_policy_name": "ha-policy-0", "volume_group_type": "thinclone",
            "uid": "99", "source_volume_group_id": "", "source_volume_group_name": "",
            "parent_uid": "", "source_snapshot_id": "", "source_snapshot": "snapshot_id_1234",
            "snapshot_count": "0", "protection_provisioned_capacity": "4.00GB",
            "protection_written_capacity": "3.00MB", "snapshot_policy_id": "",
            "snapshot_policy_name": "", "snapshot_policy_uuid": "26CDECD0-5625-0000-5002-000000000000",
            "safeguarded_snapshot_count": "0", "ignore_user_flash_copy_maps": "no",
            "partition_id": "0", "partition_name": "ptn_test", "restore_in_progress": "no",
            "owner_type": "none", "draft_partition_id": "", "draft_partition_name": "",
            "last_restore_time": "", "dr_replicated": "no", "partition_default": "no",
            "host_provisioned_capacity": "4.00GB", "anomaly_sequence_number": "",
            "uuid": "9C16DE02-1F11-528A-B978-805E906C5B3B"}

        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'clone_name_01',
            'state': 'present',
            'type': 'clone',
            'snapshot': 'snapshot_id_1234',
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                clone = IBMSVClone()
                clone.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'],
                             "Modifications of clone is not supported via this module, Please use ibm_svc_manage_volume or "
                             "ibm_svc_manage_volumegroup for modifying volume or volumegroup clone/thinclone respectively.")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_clone.IBMSVClone.get_existing_clone')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_unsupported_update_volumegroup_pool(self, svc_authorize_mock,
                                                 get_existing_clone_mock,
                                                 svc_obj_info_mock):
        get_existing_clone_mock.return_value = {
            "id": "1", "name": "clone_name_01", "volume_count": "2",
            "backup_status": "off", "last_backup_time": "", "owner_id": "",
            "owner_name": "", "safeguarded_policy_id": "", "safeguarded_policy_name": "",
            "safeguarded_policy_start_time": "", "replication_policy_id": "",
            "replication_policy_name": "", "ha_replication_policy_id": "0",
            "ha_replication_policy_name": "ha-policy-0", "volume_group_type": "thinclone",
            "uid": "99", "source_volume_group_id": "", "source_volume_group_name": "",
            "parent_uid": "", "source_snapshot_id": "", "source_snapshot": "snapshot_id_1234",
            "snapshot_count": "0", "protection_provisioned_capacity": "4.00GB",
            "protection_written_capacity": "3.00MB", "snapshot_policy_id": "",
            "snapshot_policy_name": "", "snapshot_policy_uuid": "26CDECD0-5625-0000-5002-000000000000",
            "safeguarded_snapshot_count": "0", "ignore_user_flash_copy_maps": "no",
            "partition_id": "0", "partition_name": "ptn_test", "restore_in_progress": "no",
            "owner_type": "none", "draft_partition_id": "", "draft_partition_name": "",
            "last_restore_time": "", "dr_replicated": "no", "partition_default": "no",
            "host_provisioned_capacity": "4.00GB", "anomaly_sequence_number": "",
            "uuid": "9C16DE02-1F11-528A-B978-805E906C5B3B"}

        volume_list = [
            {"id": "61", "name": "clone_vol_01", "IO_group_id": "0",
             "IO_group_name": "io_grp0", "status": "online", "mdisk_grp_id": "0",
             "mdisk_grp_name": "pool1", "capacity": "1.00GB", "type": "striped",
             "volume_type": "clone", "source_volume_id": "15", "source_volume_name": "test_vol_1",
             "source_snapshot": "snapshot_id_1234"},
            {"id": "62", "name": "clone_vol_02", "IO_group_id": "0",
             "IO_group_name": "io_grp0", "status": "online", "mdisk_grp_id": "0",
             "mdisk_grp_name": "pool1", "capacity": "1.00GB", "type": "striped",
             "volume_type": "clone", "source_volume_id": "15", "source_volume_name": "test_vol_2",
             "source_snapshot": "snapshot_id_1234"},
            {"id": "63", "name": "clone_vol_03", "IO_group_id": "0",
             "IO_group_name": "io_grp0", "status": "online", "mdisk_grp_id": "0",
             "mdisk_grp_name": "pool1", "capacity": "1.00GB", "type": "striped",
             "volume_type": "clone", "source_volume_id": "15", "source_volume_name": "test_vol_3",
             "source_snapshot": "snapshot_id_1234"},
            {"id": "64", "name": "clone_vol_04", "IO_group_id": "0",
             "IO_group_name": "io_grp0", "status": "online", "mdisk_grp_id": "0",
             "mdisk_grp_name": "pool1", "capacity": "1.00GB", "type": "striped",
             "volume_type": "clone", "source_volume_id": "15", "source_volume_name": "test_vol_4",
             "source_snapshot": "snapshot_id_1234"}]

        svc_obj_info_mock.return_value = volume_list

        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'clone_name_01',
            'state': 'present',
            'snapshot': 'snapshot_id_1234',
            'pool': 'new_pool1'
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                clone = IBMSVClone()
                clone.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'],
                             "Modifications of clone is not supported via this module, Please use ibm_svc_manage_volume or "
                             "ibm_svc_manage_volumegroup for modifying volume or volumegroup clone/thinclone respectively.")
