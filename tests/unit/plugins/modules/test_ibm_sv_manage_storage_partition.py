# Copyright (C) 2022 IBM CORPORATION
# Author(s): Shilpi Jain<shilpi.jain1@ibm.com>
#            Sandip Gulab Rajbanshi <sandip.rajbanshi@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Storage Virtualize Ansible module: ibm_sv_manage_storage_partition """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.storage_virtualize.plugins.modules.ibm_sv_manage_storage_partition import IBMSVStoragePartition


def set_module_args(args):
    """prepare arguments so that they will be picked up during module
    creation """
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)  # pylint: disable=protected-access


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


class TestIBMSVStoragePartition(unittest.TestCase):
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': '',
            'state': 'present'
        })

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVStoragePartition()
        self.assertTrue(exc.value.args[0]['failed'])

    def test_invalid_params_while_creation(self):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition1',
            'deletenonpreferredmanagementobjects': 'True',
            'deletepreferredmanagementobjects': 'True',
            'state': 'present'
        })

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVStoragePartition()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_storage_partition.IBMSVStoragePartition.get_storage_partition_details')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_storage_partition_success(self,
                                              svc_authorize_mock,
                                              svc_run_command_mock,
                                              server_exist_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition1',
            'state': 'present'
        })

        server_exist_mock.return_value = {}
        p = IBMSVStoragePartition()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_storage_partition.IBMSVStoragePartition.get_storage_partition_details')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_storage_partition_with_optional_params(self,
                                                           svc_authorize_mock,
                                                           svc_run_command_mock,
                                                           server_exist_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition1',
            'state': 'present',
            'replicationpolicy': 'policy0'
        })

        server_exist_mock.return_value = {}
        p = IBMSVStoragePartition()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_storage_partition_idempotency(self,
                                                  svc_authorize_mock,
                                                  svc_run_command_mock,
                                                  svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition1',
            'state': 'present'
        })

        svc_obj_info_mock.return_value = {
            "id": "1",
            "name": "partition1",
            "preferred_management_system_name": "",
            "active_management_system_name": "",
            "replication_policy_name": "",
            "replication_policy_id": "",
            "location1_system_name": "",
            "location1_status": "",
            "location2_system_name": "",
            "location2_status": "",
            "host_count": "0",
            "host_offline_count": "0",
            "volume_group_count": "0",
            "ha_status": "",
            "link_status": ""
        }
        p = IBMSVStoragePartition()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_storage_partition(self,
                                      svc_authorize_mock,
                                      svc_run_command_mock,
                                      svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition1',
            'preferredmanagementsystem': 'system1',
            'state': 'present'
        })

        svc_obj_info_mock.return_value = {
            "id": "1",
            "name": "partition1",
            "preferred_management_system_name": "",
            "active_management_system_name": "",
            "replication_policy_name": "",
            "replication_policy_id": "",
            "location1_system_name": "",
            "location1_status": "",
            "location2_system_name": "",
            "location2_status": "",
            "host_count": "0",
            "host_offline_count": "0",
            "volume_group_count": "0",
            "ha_status": "",
            "link_status": ""
        }
        p = IBMSVStoragePartition()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_replication_policy_storage_partition(self,
                                                         svc_authorize_mock,
                                                         svc_run_command_mock,
                                                         svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition1',
            'noreplicationpolicy': 'True',
            'state': 'present'
        })

        svc_obj_info_mock.return_value = {
            "id": "1",
            "name": "partition1",
            "preferred_management_system_name": "",
            "active_management_system_name": "",
            "replication_policy_name": "policy0",
            "location1_system_name": "",
            "location1_status": "",
            "location2_system_name": "",
            "location2_status": "",
            "host_count": "0",
            "host_offline_count": "0",
            "volume_group_count": "0",
            "ha_status": "",
            "link_status": ""
        }
        p = IBMSVStoragePartition()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_storage_partition.IBMSVStoragePartition.get_storage_partition_details')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_storage_partition_with_invalid_param(self,
                                                         svc_authorize_mock,
                                                         svc_run_command_mock,
                                                         server_exist_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition1',
            'replicationpolicy': 'policy1',
            'state': 'absent'
        })

        server_exist_mock.return_value = {
            "id": "1",
            "name": "partition1",
            "preferred_management_system_name": "",
            "active_management_system_name": "",
            "replication_policy_name": "",
            "replication_policy_id": "",
            "location1_system_name": "",
            "location1_status": "",
            "location2_system_name": "",
            "location2_status": "",
            "host_count": "0",
            "host_offline_count": "0",
            "volume_group_count": "0",
            "ha_status": "",
            "link_status": ""
        }

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVStoragePartition()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_storage_partition.IBMSVStoragePartition.get_storage_partition_details')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_storage_partition(self, svc_authorize_mock,
                                      svc_run_command_mock,
                                      server_exist_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition1',
            'state': 'absent'
        })

        server_exist_mock.return_value = {
            "id": "1",
            "name": "partition1",
            "preferred_management_system_name": "",
            "active_management_system_name": "",
            "replication_policy_name": "",
            "replication_policy_id": "",
            "location1_system_name": "",
            "location1_status": "",
            "location2_system_name": "",
            "location2_status": "",
            "host_count": "0",
            "host_offline_count": "0",
            "volume_group_count": "0",
            "ha_status": "",
            "link_status": ""
        }
        p = IBMSVStoragePartition()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_storage_partition.IBMSVStoragePartition.get_storage_partition_details')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_storage_partition_idempotency(self, svc_authorize_mock,
                                                  svc_run_command_mock,
                                                  server_exist_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition1',
            'state': 'absent'
        })

        server_exist_mock.return_value = {}
        p = IBMSVStoragePartition()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_storage_partition.IBMSVStoragePartition.get_storage_partition_details')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_merge_storage_partitions(self, svc_authorize_mock,
                                      svc_run_command_mock,
                                      partition_exists_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition0',
            'state': 'present',
            'partition_to_merge': 'partition1'
        })

        partition_exists_mock.side_effect = iter([
            {'id': '0', 'name': 'partition0'},
            {'id': '1', 'name': 'partition1'}
        ])

        p = IBMSVStoragePartition()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_storage_partition.IBMSVStoragePartition.get_storage_partition_details')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_merge_storage_partitions_idempotency(self, svc_authorize_mock,
                                                  svc_run_command_mock,
                                                  partition_exists_mock):
        '''
        Test what happens when partition1 is either already merged or does not exist.
        '''
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition0',
            'state': 'present',
            'partition_to_merge': 'partition1'
        })

        partition_exists_mock.side_effect = iter([
            {'id': '0', 'name': 'partition0'},
            {}
        ])
        p = IBMSVStoragePartition()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertEqual(exc.value.args[0]['msg'], 'Partition (partition1) does not exist or is already merged.')
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_storage_partition.IBMSVStoragePartition.get_storage_partition_details')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_merge_with_invalid_storage_partition(self, svc_authorize_mock,
                                                          svc_run_command_mock,
                                                          partition_exists_mock):
        '''
        Try to merge an existing partition into a non-existing partition; should fail
        '''
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition0',
            'state': 'present',
            'partition_to_merge': 'partition1'
        })

        partition_exists_mock.return_value = {}

        with pytest.raises(AnsibleFailJson) as exc:
            p = IBMSVStoragePartition()
            p.apply()
        self.assertEqual(exc.value.args[0]['msg'], 'Target Partition (partition0) does not exist. Merge failed.')
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_storage_partition.IBMSVStoragePartition.get_storage_partition_details')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_draft_storage_partition(self,
                                            svc_authorize_mock,
                                            svc_run_command_mock,
                                            partition_exists_mock):
        '''
        Create a new partition in draft state
        '''
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition1',
            'state': 'present',
            'draft': 'True'
        })

        partition_exists_mock.return_value = {}
        p = IBMSVStoragePartition()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_storage_partition.IBMSVStoragePartition.get_storage_partition_details')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_draft_storage_partition_idempotency(self,
                                                        svc_authorize_mock,
                                                        svc_run_command_mock,
                                                        partition_exists_mock):
        '''
        Try to create partition0 which already exists and is in draft state
        '''
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition0',
            'state': 'present',
            'draft': 'True'
        })

        partition_exists_mock.return_value = {
            'id': '0',
            'name': 'partition0',
            'draft': 'yes'
        }

        with pytest.raises(AnsibleExitJson) as exc:
            p = IBMSVStoragePartition()
            p.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_storage_partition.IBMSVStoragePartition.get_storage_partition_details')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_validate_create_modify_published_storage_partition_to_draft(self,
                                                                         svc_authorize_mock,
                                                                         svc_run_command_mock,
                                                                         partition_exists_mock):
        '''
        Try to create draft partition or move published partition (partition0) in draft state; no-op; should pass
        '''
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition0',
            'state': 'present',
            'draft': 'True'
        })

        partition_exists_mock.return_value = {
            'id': '0',
            'name': 'partition0',
            'draft': 'no'
        }

        with pytest.raises(AnsibleExitJson) as exc:
            p = IBMSVStoragePartition()
            p.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_storage_partition.IBMSVStoragePartition.get_storage_partition_details')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_publish_storage_partition(self,
                                       svc_authorize_mock,
                                       svc_run_command_mock,
                                       partition_exists_mock):
        '''
        Publish a draft partition (partition0)
        '''
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition0',
            'state': 'present',
            'draft': 'False'
        })

        partition_exists_mock.return_value = {
            'id': '0',
            'name': 'partition0',
            'draft': 'yes'
        }

        with pytest.raises(AnsibleExitJson) as exc:
            p = IBMSVStoragePartition()
            p.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_storage_partition.IBMSVStoragePartition.get_storage_partition_details')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_validate_mutually_exclusive_params_with_draft(self,
                                                                   svc_authorize_mock,
                                                                   svc_run_command_mock,
                                                                   partition_exists_mock):
        '''
        Publish a draft partition (partition0)
        '''
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition0',
            'state': 'present',
            'draft': 'True',
            'replicationpolicy': "2-site-ha-0"
        })

        partition_exists_mock.return_value = {}

        with pytest.raises(AnsibleFailJson) as exc:
            p = IBMSVStoragePartition()
            p.apply()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_add_dr_link_to_storage_partition(self,
                                              svc_authorize_mock,
                                              svc_run_command_mock,
                                              svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition1',
            'state': 'present',
            'drlink_partition_uuid': '4D837492-8C69-5BEA-9147-F5C937D38028',
            'remotesystem': 'svc_fs_1'
        })

        svc_obj_info_mock.return_value = {
            "active_management_system_id": "000002042E",
            "active_management_system_name": "fs9110shared1-cl",
            "dr_link_direction": "",
            "dr_link_status": "",
            "dr_linked_partition_name": "",
            "dr_linked_partition_uuid": "",
            "dr_linked_remote_system_1_id": "",
            "dr_linked_remote_system_1_name": "",
            "dr_linked_remote_system_2_id": "",
            "dr_linked_remote_system_2_name": "",
            "id": "0",
            "link_status": "synchronized",
            "local_location": "",
            "location1_status": "healthy",
            "location1_system_id": "000002042E",
            "location1_system_name": "fs9110shared1-cl",
            "location1_total_object_count": "4",
            "location2_status": "healthy",
            "location2_system_id": "00000204AE",
            "location2_system_name": "fs9110shared3-cl",
            "name": "partition1",
            "preferred_management_system_id": "000002042E",
            "preferred_management_system_name": "fs9110shared1-cl",
            "volume_group_count": "1",
            "volume_group_stopped_count": "0",
            "volume_group_synchronized_count": "1",
            "volume_group_synchronizing_count": "0"
        }
        p = IBMSVStoragePartition()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_add_dr_link_to_storage_partition_idempotency(self,
                                                          svc_authorize_mock,
                                                          svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition1',
            'state': 'present',
            'drlink_partition_uuid': '4D837492-8C69-5BEA-9147-F5C937D38028',
            'remotesystem': 'svc_fs_1'
        })

        svc_obj_info_mock.return_value = {
            "active_management_system_id": "000002042E",
            "active_management_system_name": "fs9110shared1-cl",
            "dr_link_direction": "upper_to_lower",
            "dr_link_status": "healthy",
            "dr_linked_partition_name": "sgr_ansible_ptn",
            "dr_linked_partition_uuid": "4D837492-8C69-5BEA-9147-F5C937D38028",
            "dr_linked_remote_system_1_id": "000002035AE",
            "dr_linked_remote_system_1_name": "svc_fs_1",
            "dr_linked_remote_system_2_id": "",
            "dr_linked_remote_system_2_name": "",
            "id": "0",
            "link_status": "synchronized",
            "local_location": "",
            "location1_status": "healthy",
            "location1_system_id": "000002042E",
            "location1_system_name": "fs9110shared1-cl",
            "location1_total_object_count": "4",
            "location2_status": "healthy",
            "location2_system_id": "00000204AE",
            "location2_system_name": "fs9110shared3-cl",
            "name": "partition1",
            "preferred_management_system_id": "000002042E",
            "preferred_management_system_name": "fs9110shared1-cl",
            "volume_group_count": "1",
            "volume_group_stopped_count": "0",
            "volume_group_synchronized_count": "1",
            "volume_group_synchronizing_count": "0"
        }
        p = IBMSVStoragePartition()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_replace_drlink(self,
                                    svc_authorize_mock,
                                    svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition1',
            'state': 'present',
            'drlink_partition_uuid': '4D837492-8C69-5BEA-9147-F5C937D38028',
            'remotesystem': 'svc_fs_1'
        })

        svc_obj_info_mock.return_value = {
            "active_management_system_id": "000002042E",
            "active_management_system_name": "fs9110shared1-cl",
            "dr_link_direction": "upper_to_lower",
            "dr_link_status": "healthy",
            "dr_linked_partition_name": "sgr_ansible_ptn_2",
            "dr_linked_partition_uuid": "8BA692A5-F33F-5731-9CF0-E50669EB2FE1",
            "dr_linked_remote_system_1_id": "000002067AE",
            "dr_linked_remote_system_1_name": "svc_fs_2",
            "dr_linked_remote_system_2_id": "",
            "dr_linked_remote_system_2_name": "",
            "id": "0",
            "link_status": "synchronized",
            "local_location": "",
            "location1_status": "healthy",
            "location1_system_id": "000002042E",
            "location1_system_name": "fs9110shared1-cl",
            "location1_total_object_count": "4",
            "location2_status": "healthy",
            "location2_system_id": "00000204AE",
            "location2_system_name": "fs9110shared3-cl",
            "name": "partition1",
            "preferred_management_system_id": "000002042E",
            "preferred_management_system_name": "fs9110shared1-cl",
            "volume_group_count": "1",
            "volume_group_stopped_count": "0",
            "volume_group_synchronized_count": "1",
            "volume_group_synchronizing_count": "0"
        }
        p = IBMSVStoragePartition()

        with pytest.raises(AnsibleFailJson) as exc:
            p.apply()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_add_drlink_without_remotesystem(self,
                                                     svc_authorize_mock,
                                                     svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition1',
            'state': 'present',
            'drlink_partition_uuid': '4D837492-8C69-5BEA-9147-F5C937D38028',
        })

        svc_obj_info_mock.return_value = {
            "active_management_system_id": "000002042E",
            "active_management_system_name": "fs9110shared1-cl",
            "dr_link_direction": "",
            "dr_link_status": "",
            "dr_linked_partition_name": "",
            "dr_linked_partition_uuid": "",
            "dr_linked_remote_system_1_id": "",
            "dr_linked_remote_system_1_name": "",
            "dr_linked_remote_system_2_id": "",
            "dr_linked_remote_system_2_name": "",
            "id": "0",
            "link_status": "synchronized",
            "local_location": "",
            "location1_status": "healthy",
            "location1_system_id": "000002042E",
            "location1_system_name": "fs9110shared1-cl",
            "location1_total_object_count": "4",
            "location2_status": "healthy",
            "location2_system_id": "00000204AE",
            "location2_system_name": "fs9110shared3-cl",
            "name": "partition1",
            "preferred_management_system_id": "000002042E",
            "preferred_management_system_name": "fs9110shared1-cl",
            "volume_group_count": "1",
            "volume_group_stopped_count": "0",
            "volume_group_synchronized_count": "1",
            "volume_group_synchronizing_count": "0"
        }

        with pytest.raises(AnsibleFailJson) as exc:
            p = IBMSVStoragePartition()
            p.apply()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_drlink_partition(self,
                                     svc_authorize_mock,
                                     svc_obj_info_mock,
                                     svc_run_comand_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition1',
            'state': 'present',
            'removedrlink': True
        })

        svc_obj_info_mock.return_value = {
            "active_management_system_id": "000002042E",
            "active_management_system_name": "fs9110shared1-cl",
            "dr_link_direction": "upper_to_lower",
            "dr_link_status": "healthy",
            "dr_linked_partition_name": "sgr_ansible_ptn_2",
            "dr_linked_partition_uuid": "8BA692A5-F33F-5731-9CF0-E50669EB2FE1",
            "dr_linked_remote_system_1_id": "000002067AE",
            "dr_linked_remote_system_1_name": "svc_fs_2",
            "dr_linked_remote_system_2_id": "",
            "dr_linked_remote_system_2_name": "",
            "id": "0",
            "link_status": "synchronized",
            "local_location": "",
            "location1_status": "healthy",
            "location1_system_id": "000002042E",
            "location1_system_name": "fs9110shared1-cl",
            "location1_total_object_count": "4",
            "location2_status": "healthy",
            "location2_system_id": "00000204AE",
            "location2_system_name": "fs9110shared3-cl",
            "name": "partition1",
            "preferred_management_system_id": "000002042E",
            "preferred_management_system_name": "fs9110shared1-cl",
            "volume_group_count": "1",
            "volume_group_stopped_count": "0",
            "volume_group_synchronized_count": "1",
            "volume_group_synchronizing_count": "0"
        }
        svc_run_comand_mock.return_value = {"success"}

        with pytest.raises(AnsibleExitJson) as exc:
            p = IBMSVStoragePartition()
            p.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_drlink_partition_idempotency(self,
                                                 svc_authorize_mock,
                                                 svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition1',
            'state': 'present',
            'removedrlink': True
        })

        svc_obj_info_mock.return_value = {
            "active_management_system_id": "000002042E",
            "active_management_system_name": "fs9110shared1-cl",
            "dr_link_direction": "",
            "dr_link_status": "",
            "dr_linked_partition_name": "",
            "dr_linked_partition_uuid": "",
            "dr_linked_remote_system_1_id": "",
            "dr_linked_remote_system_1_name": "",
            "dr_linked_remote_system_2_id": "",
            "dr_linked_remote_system_2_name": "",
            "id": "0",
            "link_status": "synchronized",
            "local_location": "",
            "location1_status": "healthy",
            "location1_system_id": "000002042E",
            "location1_system_name": "fs9110shared1-cl",
            "location1_total_object_count": "4",
            "location2_status": "healthy",
            "location2_system_id": "00000204AE",
            "location2_system_name": "fs9110shared3-cl",
            "name": "partition1",
            "preferred_management_system_id": "000002042E",
            "preferred_management_system_name": "fs9110shared1-cl",
            "volume_group_count": "1",
            "volume_group_stopped_count": "0",
            "volume_group_synchronized_count": "1",
            "volume_group_synchronizing_count": "0"
        }

        with pytest.raises(AnsibleExitJson) as exc:
            p = IBMSVStoragePartition()
            p.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_invalid_parameters(self,
                                        svc_authorize_mock,
                                        svc_obj_info_mock):
        '''
        Parameter 'removedrlink', 'drlink_partition_uuid' are mutually exclusive parameters
        '''
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition1',
            'state': 'present',
            'removedrlink': True,
            'drlink_partition_uuid': '4D837492-8C69-5BEA-9147-F5C937D38028',
            'remotesystem': "svc_fs_1"
        })

        svc_obj_info_mock.return_value = {
            "active_management_system_id": "000002042E",
            "active_management_system_name": "fs9110shared1-cl",
            "dr_link_direction": "upper_to_lower",
            "dr_link_status": "healthy",
            "dr_linked_partition_name": "sgr_ansible_ptn_2",
            "dr_linked_partition_uuid": "8BA692A5-F33F-5731-9CF0-E50669EB2FE1",
            "dr_linked_remote_system_1_id": "000002067AE",
            "dr_linked_remote_system_1_name": "svc_fs_2",
            "dr_linked_remote_system_2_id": "",
            "dr_linked_remote_system_2_name": "",
            "id": "0",
            "link_status": "synchronized",
            "local_location": "",
            "location1_status": "healthy",
            "location1_system_id": "000002042E",
            "location1_system_name": "fs9110shared1-cl",
            "location1_total_object_count": "4",
            "location2_status": "healthy",
            "location2_system_id": "00000204AE",
            "location2_system_name": "fs9110shared3-cl",
            "name": "partition1",
            "preferred_management_system_id": "000002042E",
            "preferred_management_system_name": "fs9110shared1-cl",
            "volume_group_count": "1",
            "volume_group_stopped_count": "0",
            "volume_group_synchronized_count": "1",
            "volume_group_synchronizing_count": "0"
        }

        with pytest.raises(AnsibleFailJson) as exc:
            p = IBMSVStoragePartition()
            p.apply()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_storage_partition.IBMSVStoragePartition.get_storage_partition_details')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_chg_partition_location(self,
                                    svc_authorize_mock,
                                    svc_run_command_mock,
                                    partition_exists_mock):
        '''
        Migration test: Source-side validation
        Try changing partition location when partition is present
        on the source system, and no migration is going on.
        '''
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition0',
            'state': 'present',
            'location': 'target_cluster_fqdn_name'
        })

        partition_exists_mock.side_effect = iter([
            {'id': '0',
             'name': 'partition0',
             'desired_location_system_name': '',
             'migration_status': ''
             }
        ])

        p = IBMSVStoragePartition()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_storage_partition.IBMSVStoragePartition.get_storage_partition_details')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_chg_partition_location_while_migr_in_progress(self,
                                                           svc_authorize_mock,
                                                           partition_exists_mock):
        '''
        Migration test: Source-side validation
        Idempotency case 1:
        Try changing partition location when migration is in progress,
        Partition is present on the source system, with migration_state = 'in_progress'
        and desired_location_system_name = target_cluster_fqdn_name.
        It should pass without making any change.
        '''
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition0',
            'state': 'present',
            'location': 'target_cluster_fqdn_name'
        })

        partition_exists_mock.side_effect = iter([
            {'id': '0',
             'name': 'partition0',
             'desired_location_system_name': 'target_cluster_fqdn_name',
             'migration_status': 'in_progress'
             }
        ])

        p = IBMSVStoragePartition()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertFalse(exc.value.args[0]['changed'])
        self.assertEqual(exc.value.args[0]['msg'], "A partition migration is already"
                         " in progress with target cluster target_cluster_fqdn_name.")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_storage_partition.IBMSVStoragePartition.get_storage_partition_details')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_chg_partition_location_after_migr_completion(self,
                                                          svc_authorize_mock,
                                                          partition_exists_mock):
        '''
        Migration test: Source-side validation
        Idempotency case 2:
        Try changing partition location when partition does not exist on source
        cluster. Most likely, partition is already migrated so test should pass
        without making any change.
        '''
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition0',
            'state': 'present',
            'location': 'target_cluster_fqdn_name'
        })

        partition_exists_mock.return_value = {}
        p = IBMSVStoragePartition()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_storage_partition.IBMSVStoragePartition.get_storage_partition_details')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_running_partition_migrationaction_after_dmp(self,
                                                         svc_authorize_mock,
                                                         svc_run_command_mock,
                                                         partition_exists_mock):
        '''
        Migration test: Target-side validation
        Try initiating migrationaction = fixeventwithchecks after location change
        is triggered and dmp is fixed.
        This test cannot check for dmp as it is manual step.
        '''
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition0',
            'state': 'present',
            'migrationaction': 'fixeventwithchecks'
        })

        partition_exists_mock.side_effect = iter([
            {'id': '0',
             'name': 'partition0',
             'desired_location_system_name': 'target_cluster_fqdn_name',
             'migration_status': 'awaiting_user_input'
             }
        ])

        p = IBMSVStoragePartition()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_storage_partition.IBMSVStoragePartition.get_storage_partition_details')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_partition_migrationaction_idempotency_1(self,
                                                     svc_authorize_mock,
                                                     partition_exists_mock):
        '''
        Migration test: Target-side validation
        Try initiating migrationaction = fixeventwithchecks after location change
        was triggered and still migration_status = in_progress on target system.
        Don't run anything, just return success.
        '''
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition0',
            'state': 'present',
            'migrationaction': 'fixeventwithchecks'
        })

        partition_exists_mock.side_effect = iter([
            {'id': '0',
             'name': 'partition0',
             'desired_location_system_name': 'target_cluster_fqdn_name',
             'migration_status': 'in_progress'
             }
        ])

        p = IBMSVStoragePartition()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_storage_partition.IBMSVStoragePartition.get_storage_partition_details')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_partition_migrationaction_idempotency_2(self,
                                                     svc_authorize_mock,
                                                     partition_exists_mock):
        '''
        Migration test: Target-side validation
        Try initiating migrationaction = fixeventwithchecks after migration was
        already completed. At this time, migration_status = '' on target system.
        Don't run anything, just return success.
        '''
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'partition0',
            'state': 'present',
            'migrationaction': 'fixeventwithchecks'
        })

        partition_exists_mock.side_effect = iter([
            {'id': '0',
             'name': 'partition0',
             'desired_location_system_name': '',
             'migration_status': ''
             }
        ])

        p = IBMSVStoragePartition()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertFalse(exc.value.args[0]['changed'])


if __name__ == '__main__':
    unittest.main()
