# Copyright (C) 2020 IBM CORPORATION
# Author(s): Shilpi Jain <shilpi.jain1@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Storage Virtualize Ansible module: ibm_svc_hostcluster """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.storage_virtualize.plugins.modules.ibm_svc_hostcluster import IBMSVChostcluster
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


def fail_json(*args, **kwargs):  # pylint: disable=unused-argument
    """function to patch over fail_json; package return data into an
    exception """
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


class TestIBMSVChostcluster(unittest.TestCase):
    """ a group of related Unit Tests"""

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

    def set_default_args(self):
        return dict({
            'name': 'test',
            'state': 'present'
        })

    def test_failure_module(self):
        """
        Test module with required parameters are missing.
        """
        with set_module_args({}):
            with pytest.raises(AnsibleFailJson) as exc:
                IBMSVChostcluster()
            print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_hostcluster(self, svc_authorize_mock, svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_hostcluster',
        }):
            hostcluster_ret = {
                "id": "1", "name": "ansible_hostcluster", "port_count": "1", "mapping_count": "4", "status": "offline", "host_count": "1", "protocol": "nvme",
                "owner_id": "", "owner_name": ""
            }
            svc_obj_info_mock.return_value = hostcluster_ret
            host = IBMSVChostcluster().get_existing_hostcluster()
            self.assertEqual('ansible_hostcluster', host['name'])
            self.assertEqual('1', host['id'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_hostcluster.IBMSVChostcluster.get_existing_hostcluster')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_hostcluster_create_get_existing_hostcluster_called(self, svc_authorize_mock,
                                                                get_existing_hostcluster_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_host',
        }):
            hostcluster_created = IBMSVChostcluster()
            with pytest.raises(AnsibleExitJson) as exc:
                hostcluster_created.apply()
            self.assertFalse(exc.value.args[0]['changed'])
            get_existing_hostcluster_mock.assert_called_with()

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_hostcluster.IBMSVChostcluster.get_existing_hostcluster')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_hostcluster_but_hostcluster_exist(self, svc_authorize_mock,
                                                      get_existing_hostcluster_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'hostcluster0',
        }):
            hostcluster_ret = {
                "id": "0",
                "name": "hostcluster0",
                "status": "online",
                "host_count": "1",
                "mapping_count": "0",
                "port_count": "1",
                "protocol": "scsi",
                "owner_id": "0",
                "owner_name": "group5"
            }
            get_existing_hostcluster_mock.return_value = hostcluster_ret
            hostcluster_created = IBMSVChostcluster()
            with pytest.raises(AnsibleExitJson) as exc:
                hostcluster_created.apply()
            self.assertFalse(exc.value.args[0]['changed'])
            get_existing_hostcluster_mock.assert_called_with()

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_hostcluster.IBMSVChostcluster.get_existing_hostcluster')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_hostcluster.IBMSVChostcluster.hostcluster_create')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_hostcluster_successfully(self, svc_authorize_mock,
                                             hostcluster_create_mock,
                                             get_existing_hostcluster_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_hostcluster'
        }):
            host = {u'message': u'Host cluster, id [14], '
                                u'successfully created', u'id': u'14'}
            hostcluster_create_mock.return_value = host
            get_existing_hostcluster_mock.return_value = []
            hostcluster_created = IBMSVChostcluster()
            with pytest.raises(AnsibleExitJson) as exc:
                hostcluster_created.apply()
            self.assertTrue(exc.value.args[0]['changed'])
            get_existing_hostcluster_mock.assert_called_with()

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_hostcluster.IBMSVChostcluster.get_existing_hostcluster')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_create_hostcluster(self, svc_authorize_mock, get_existing_hostcluster_mock):
        '''
        Test to create to host cluster without required parameter
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_hostcluster'
        }):
            get_existing_hostcluster_mock.return_value = []
            hostcluster_created = IBMSVChostcluster()
            with pytest.raises(AnsibleFailJson) as exc:
                hostcluster_created.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            get_existing_hostcluster_mock.assert_called_with()

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_hostcluster.IBMSVChostcluster.get_existing_hostcluster')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_hostcluster_but_hostcluster_not_exist(self, svc_authorize_mock,
                                                          get_existing_hostcluster_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_hostcluster',
        }):
            get_existing_hostcluster_mock.return_value = []
            hostcluster_deleted = IBMSVChostcluster()
            with pytest.raises(AnsibleExitJson) as exc:
                hostcluster_deleted.apply()
            self.assertFalse(exc.value.args[0]['changed'])
            get_existing_hostcluster_mock.assert_called_with()

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_ownershipgroup(self, auth, cmd1):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_hostcluster',
            'ownershipgroup': 'new'
        }):
            modify = [
                'ownershipgroup'
            ]
            cmd1.return_value = None
            h = IBMSVChostcluster()
            h.hostcluster_update(modify)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_remove_hostcluster(self, auth, cmd1, cmd2):
        '''
        Test to delete hostcluster with invalid parameter
        Invalid parameters while deleting hostcluster: ['ownershipgroup', 'noownershipgroup', 'site', 'partition']
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'hostcluster0',
            'ownershipgroup': 'group1'
        }):
            cmd1.return_value = {
                "id": "0",
                "name": "hostcluster0",
                "status": "online",
                "host_count": "1",
                "mapping_count": "0",
                "port_count": "1",
                "protocol": "scsi",
                "owner_id": "0",
                "owner_name": "group5"
            }
            cmd2.return_value = None
            with pytest.raises(AnsibleFailJson) as exc:
                h = IBMSVChostcluster()
                h.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'], "Parameters [ownershipgroup] not supported while deleting a hostcluster")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_site(self, svc_authorize_mock, svc_obj_info_mock, svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'state': 'present',
            'name': 'test_hostcluster_0',
            'site': 'site1',
        }):
            svc_obj_info_mock.side_effect = [
                {
                    "id": "0", "name": "test_hostcluster_0", "status": "online", "host_count": "2", "mapping_count": "0",
                    "port_count": "2", "protocol": "scsi", "owner_id": "", "owner_name": ""
                },
                [
                    {
                        "id": "0", "name": "test_host_0", "port_count": "1", "iogrp_count": "2", "status": "online", "site_id": "", "site_name": "",
                        "host_cluster_id": "0", "host_cluster_name": "test_hostcluster_0", "protocol": "scsi", "owner_id": "", "owner_name": "",
                        "portset_id": "0", "portset_name": "portset0", "partition_id": "", "partition_name": "", "draft_partition_id": "",
                        "draft_partition_name": "", "ungrouped_volume_mapping": "no", "location_system_name": ""
                    },
                    {
                        "id": "1", "name": "test_host_1", "port_count": "1", "iogrp_count": "2", "status": "online", "site_id": "", "site_name": "",
                        "host_cluster_id": "0", "host_cluster_name": "test_hostcluster_0", "protocol": "scsi", "owner_id": "", "owner_name": "",
                        "portset_id": "0", "portset_name": "portset0", "partition_id": "", "partition_name": "", "draft_partition_id": "",
                        "draft_partition_name": "", "ungrouped_volume_mapping": "no", "location_system_name": ""
                    }
                ]
            ]
            hostcluster_update = IBMSVChostcluster()
            with pytest.raises(AnsibleExitJson) as exc:
                hostcluster_update.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_update_site(self, svc_authorize_mock, svc_obj_info_mock, svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'state': 'present',
            'name': 'test_hostcluster_0',
            'site': 'site2',
        }):
            svc_obj_info_mock.side_effect = [
                {
                    "id": "0", "name": "test_hostcluster_0", "status": "online", "host_count": "2", "mapping_count": "0",
                    "port_count": "2", "protocol": "scsi", "owner_id": "", "owner_name": ""
                },
                [
                    {
                        "id": "0", "name": "test_host_0", "port_count": "1", "iogrp_count": "2", "status": "online", "site_id": "", "site_name": "",
                        "host_cluster_id": "0", "host_cluster_name": "test_hostcluster_0", "protocol": "scsi", "owner_id": "", "owner_name": "",
                        "portset_id": "0", "portset_name": "portset0", "partition_id": "", "partition_name": "", "draft_partition_id": "",
                        "draft_partition_name": "", "ungrouped_volume_mapping": "no", "location_system_name": ""
                    },
                    {
                        "id": "1", "name": "test_host_1", "port_count": "1", "iogrp_count": "2", "status": "online", "site_id": "1", "site_name": "site1",
                        "host_cluster_id": "0", "host_cluster_name": "test_hostcluster_0", "protocol": "scsi", "owner_id": "", "owner_name": "",
                        "portset_id": "0", "portset_name": "portset0", "partition_id": "", "partition_name": "", "draft_partition_id": "",
                        "draft_partition_name": "", "ungrouped_volume_mapping": "no", "location_system_name": ""
                    }
                ]
            ]
            hostcluster_update = IBMSVChostcluster()
            with pytest.raises(AnsibleFailJson) as exc:
                hostcluster_update.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'],
                             "Cannot update host cluster site to [site2]. The following hosts already have a different site: test_host_1 (Current site: site1)"
                             )

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_hostcluster_with_partition(self, svc_authorize_mock, svc_obj_info_mock, svc_run_command_mock):
        '''
        Test to create hostcluster with published partition
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_hostcluster',
            'partition': 'partition1'
        }):
            svc_obj_info_mock.side_effect = [
                {},
                {
                    'id': '0',
                    'name': 'partition1',
                    'draft': "no"
                }
            ]
            hostcluster_created = IBMSVChostcluster()
            with pytest.raises(AnsibleExitJson) as exc:
                hostcluster_created.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_hostcluster_with_partition_idempotency(self, svc_authorize_mock, svc_obj_info_mock):
        '''
        Test to create or update hostcluster with published partition to check for idempotency
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_hostcluster',
            'partition': 'partition1'
        }):
            svc_obj_info_mock.side_effect = [
                {
                    "id": "0",
                    "name": "ansible_hostcluster",
                    "partition_id": "0",
                    "partition_name": "partition1",
                    "draft_partition_id": "",
                    "draft_partition_name": ""
                },
                {
                    'id': '0',
                    'name': 'partition1',
                    'draft': "no"
                }
            ]
            hostcluster = IBMSVChostcluster()
            with pytest.raises(AnsibleExitJson) as exc:
                hostcluster.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_partition(self, svc_authorize_mock, svc_obj_info_mock, svc_run_command_mock):
        '''
        Test to update hostcluster with draft partition
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_hostcluster',
            'partition': "draftptn0"
        }):
            svc_obj_info_mock.side_effect = [
                {
                    "id": "0",
                    "name": "ansible_hostcluster",
                    "partition_id": "",
                    "partition_name": "",
                    "draft_partition_id": "",
                    "draft_partition_name": ""
                },
                {
                    'id': '0',
                    'name': 'draftptn0',
                    'draft': "yes"
                }
            ]
            hostcluster = IBMSVChostcluster()
            with pytest.raises(AnsibleExitJson) as exc:
                hostcluster.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_update_partition_1(self, svc_authorize_mock, svc_obj_info_mock, svc_run_command_mock):
        '''
        Test to update hostcluster with published partition
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_hostcluster',
            'partition': "partition1"
        }):
            svc_obj_info_mock.side_effect = [
                {
                    "id": "0",
                    "name": "ansible_hostcluster",
                    "partition_id": "",
                    "partition_name": "",
                    "draft_partition_id": "",
                    "draft_partition_name": ""
                },
                {
                    'id': '0',
                    'name': 'partition1',
                    'draft': "no"
                }
            ]
            hostcluster = IBMSVChostcluster()
            with pytest.raises(AnsibleFailJson) as exc:
                hostcluster.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'], "Published partition is not supported while updating host cluster")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_update_partition_2(self, svc_authorize_mock, svc_obj_info_mock, svc_run_command_mock):
        '''
        Test to update hostcluster with non-existent partition, similar for creation also
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_hostcluster',
            'partition': "partition1234"
        }):
            svc_obj_info_mock.side_effect = [
                {
                    "id": "0",
                    "name": "ansible_hostcluster",
                    "partition_id": "",
                    "partition_name": "",
                    "draft_partition_id": "",
                    "draft_partition_name": ""
                },
                {}
            ]
            hostcluster = IBMSVChostcluster()
            with pytest.raises(AnsibleFailJson) as exc:
                hostcluster.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'], "Partition [partition1234] does not exist")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_update_partition_3(self, svc_authorize_mock, svc_obj_info_mock):
        '''
        Test to update hostcluster with draft partition
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_hostcluster',
            'partition': "partition2"
        }):
            svc_obj_info_mock.side_effect = [
                {
                    "id": "0",
                    "name": "ansible_hostcluster",
                    "partition_id": "0",
                    "partition_name": "partition1",
                    "draft_partition_id": "",
                    "draft_partition_name": ""
                },
                {
                    'id': '0',
                    'name': 'partition2',
                    'draft': "yes"
                }
            ]
            hostcluster = IBMSVChostcluster()
            with pytest.raises(AnsibleFailJson) as exc:
                hostcluster.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'], "Hostcluster is already associated with a partition.")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_mutually_exclusive_params(self, svc_authorize_mock):
        '''
        Failure test for mutually exclusive parameteres: removeallhosts and removemappings
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_hostcluster',
            'state': 'absent',
            'removeallhosts': True,
            'removemappings': True,
        }):
            hostcluster = IBMSVChostcluster()
            with pytest.raises(AnsibleFailJson) as exc:
                hostcluster.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'], "Mutually exclusive parameters: [removeallhosts, removemappings]")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_hostcluster_1(self, svc_authorize_mock, svc_obj_info_mock, svc_run_command_mock):
        '''
        Test to remove hostcluster without passing: removeallhosts and removemappings
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_hostcluster',
            'state': 'absent',
        }):
            svc_obj_info_mock.return_value = {
                "id": "0",
                "name": "ansible_hostcluster",
                "status": "offline",
                "host_count": "2",
                "mapping_count": "2",
                "port_count": "2",
                "protocol": "scsi",
                "owner_id": "",
                "owner_name": "",
                "partition_id": "",
                "partition_name": "",
                "draft_partition_id": "",
                "draft_partition_name": ""
            }
            hostcluster = IBMSVChostcluster()
            with pytest.raises(AnsibleExitJson) as exc:
                hostcluster.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_hostcluster_2(self, svc_authorize_mock, svc_obj_info_mock, svc_run_command_mock):
        '''
        Test to remove hostcluster with passing removemappings
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_hostcluster',
            'state': 'absent',
            'removemappings': True,
        }):
            svc_obj_info_mock.return_value = {
                "id": "0",
                "name": "ansible_hostcluster",
                "status": "offline",
                "host_count": "2",
                "mapping_count": "2",
                "port_count": "2",
                "protocol": "scsi",
                "owner_id": "",
                "owner_name": "",
                "partition_id": "",
                "partition_name": "",
                "draft_partition_id": "",
                "draft_partition_name": ""
            }
            hostcluster = IBMSVChostcluster()
            with pytest.raises(AnsibleExitJson) as exc:
                hostcluster.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_hostcluster_3(self, svc_authorize_mock, svc_obj_info_mock, svc_run_command_mock):
        '''
        Test to remove hostcluster with passing removeallhosts
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_hostcluster',
            'state': 'absent',
            'removeallhosts': True,
        }):
            svc_obj_info_mock.return_value = {
                "id": "0",
                "name": "ansible_hostcluster",
                "status": "offline",
                "host_count": "2",
                "mapping_count": "2",
                "port_count": "2",
                "protocol": "scsi",
                "owner_id": "",
                "owner_name": "",
                "partition_id": "",
                "partition_name": "",
                "draft_partition_id": "",
                "draft_partition_name": ""
            }
            hostcluster = IBMSVChostcluster()
            with pytest.raises(AnsibleExitJson) as exc:
                hostcluster.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_hostcluster_4(self, svc_authorize_mock, svc_obj_info_mock, svc_run_command_mock):
        '''
        Test to remove hostcluster without passing removeallhosts, removemappings and hostcluster associated with storage partition
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_hostcluster',
            'state': 'absent',
        }):
            svc_obj_info_mock.return_value = {
                "id": "0",
                "name": "ansible_hostcluster",
                "status": "offline",
                "host_count": "2",
                "mapping_count": "2",
                "port_count": "2",
                "protocol": "scsi",
                "owner_id": "",
                "owner_name": "",
                "partition_id": "",
                "partition_name": "",
                "draft_partition_id": "0",
                "draft_partition_name": "ab_test"
            }
            hostcluster = IBMSVChostcluster()
            with pytest.raises(AnsibleExitJson) as exc:
                hostcluster.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_remove_hostcluster_5(self, svc_authorize_mock, svc_obj_info_mock, svc_run_command_mock):
        '''
        Test to remove hostcluster with passing removemappings and hostcluster associated with storage partition
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_hostcluster',
            'state': 'absent',
            'removemappings': True,
        }):
            svc_obj_info_mock.return_value = {
                "id": "0",
                "name": "ansible_hostcluster",
                "status": "offline",
                "host_count": "2",
                "mapping_count": "2",
                "port_count": "2",
                "protocol": "scsi",
                "owner_id": "",
                "owner_name": "",
                "partition_id": "",
                "partition_name": "",
                "draft_partition_id": "0",
                "draft_partition_name": "ab_test"
            }
            hostcluster = IBMSVChostcluster()
            with pytest.raises(AnsibleFailJson) as exc:
                hostcluster.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(
                exc.value.args[0]['msg'],
                "Cannot remove host cluster [ansible_hostcluster] as it is associated with a partition. "
                "Use removemappings=false to delete the host cluster to keep host to volume mappings."
            )


if __name__ == '__main__':
    unittest.main()
