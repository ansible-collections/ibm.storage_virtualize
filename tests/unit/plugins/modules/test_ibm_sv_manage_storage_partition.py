# Copyright (C) 2022 IBM CORPORATION
# Author(s): Shilpi Jain<shilpi.jain1@ibm.com>
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


if __name__ == '__main__':
    unittest.main()
