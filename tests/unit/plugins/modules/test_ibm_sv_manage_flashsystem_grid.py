# Copyright (C) 2025 IBM CORPORATION
# Author(s): Sumit Kumar Gupta <sumit.gupta16@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Storage Virtualize Ansible module: ibm_sv_manage_flashsystem_grid """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.storage_virtualize.plugins.modules.ibm_sv_manage_flashsystem_grid import IBMSVFlashsystemGridMgmt


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


class TestIBMSVFlashsystemGridMgmt(unittest.TestCase):
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

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    def test_create_flashsystem_grid(self,
                                     svc_run_command_mock,
                                     svc_authorize_mock,
                                     svc_obj_info_mock):
        '''
        Create a flashsystem grid on a cluster which is not part of flashsystem grid
        '''

        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'fg0',
            'state': 'present'
        })

        svc_obj_info_mock.return_value = ""
        svc_run_command_mock.return_value = ""

        fg = IBMSVFlashsystemGridMgmt()
        with pytest.raises(AnsibleExitJson) as exc:
            fg.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_flashsystem_grid_idempotency(self,
                                                 svc_authorize_mock,
                                                 svc_obj_info_mock):
        '''
        Create a flashsystem grid on a cluster which has flashsystem grid with same name
        and is coordinator.
        '''
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'fg0',
            'state': 'present'
        })

        svc_obj_info_mock.side_effect = [
            # For lsflashgridmembers
            [
                {"id": "0", "member_address": "", "role": "coordinator"},
                {"id": "1", "member_address": "1.2.3.5", "role": "member"},
                {"id": "2", "member_address": "1.2.3.6", "role": "member"}
            ],
            {"flash_grid_name": 'fg0'}  # For lsflashgrid, to get flash_grid_name
        ]

        fg = IBMSVFlashsystemGridMgmt()
        with pytest.raises(AnsibleExitJson) as exc:
            fg.apply()

        self.assertFalse(exc.value.args[0]['changed'])
        self.assertEqual(exc.value.args[0]['msg'], "Flashsystem grid (fg0) already exists.")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_create_flashsystem_grid_on_existing_fg_coordinator(self, svc_authorize_mock, svc_obj_info_mock):
        '''
        Test failure if user tries to create another flashsystem grid on a flashsystem grid coordinator
        '''
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'fg0',
            'state': 'present'
        })

        svc_obj_info_mock.side_effect = [
            # For lsflashgridmembers
            [
                {"id": "0", "member_address": "", "role": "coordinator"},
                {"id": "1", "member_address": "1.2.3.5", "role": "member"},
                {"id": "2", "member_address": "1.2.3.6", "role": "member"}
            ],
            {"flash_grid_name": 'fg1'}  # For lsflashgrid, to get flash_grid_name
        ]

        fg = IBMSVFlashsystemGridMgmt()
        with pytest.raises(AnsibleFailJson) as exc:
            fg.apply()

        self.assertTrue(exc.value.args[0]['failed'])
        self.assertEqual(exc.value.args[0]['msg'],
                         "CMMVC1265E The command failed as this system is already a member of a Flash Grid.")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_create_flashsystem_grid_on_existing_fg_member(self,
                                                                   svc_authorize_mock,
                                                                   svc_obj_info_mock):
        '''
        Test failure if user tries to create another flashsystem grid on a flashsystem grid member
        '''
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'fg0',
            'state': 'present'
        })

        svc_obj_info_mock.side_effect = [
            [
                {"id": "0", "member_address": "", "role": "member"},
                {"id": "1", "member_address": "1.2.3.5", "role": "coordinator."},
                {"id": "2", "member_address": "1.2.3.6", "role": "member"}
            ],
            {"flash_grid_name": 'fg1'}  # For lsflashgrid, to get flash_grid_name
        ]

        fg = IBMSVFlashsystemGridMgmt()
        with pytest.raises(AnsibleFailJson) as exc:
            fg.apply()

        self.assertTrue(exc.value.args[0]['failed'])
        self.assertEqual(exc.value.args[0]['msg'],
                         "CMMVC1265E The command failed as this system is already a member of a Flash Grid.")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    def test_delete_flashsystem_grid(self,
                                     svc_run_command_mock,
                                     svc_authorize_mock,
                                     svc_obj_info_mock):
        '''
        Delete a flashsystem grid from coordinator
        '''

        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'absent'
        })

        svc_obj_info_mock.return_value = [
            # lsflashgridmembers output
            [{"id": "0", "member_address": "", "role": "coordinator"}]
        ]
        svc_run_command_mock.return_value = ""

        fg = IBMSVFlashsystemGridMgmt()
        with pytest.raises(AnsibleExitJson) as exc:
            fg.apply()

        self.assertTrue(exc.value.args[0]['changed'])
        self.assertEqual(exc.value.args[0]['msg'], "Deleted flashsystem-grid successfully")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_flashsystem_grid_idempotency(self,
                                                 svc_authorize_mock,
                                                 svc_obj_info_mock):
        '''
        Test deleting a non-existent flashsystem grid from a cluster
        '''
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'absent'
        })

        svc_obj_info_mock.return_value = ""

        fg = IBMSVFlashsystemGridMgmt()
        with pytest.raises(AnsibleExitJson) as exc:
            fg.apply()

        self.assertFalse(exc.value.args[0]['changed'])
        self.assertEqual(exc.value.args[0]['msg'], "Flashsystem grid does not exist.")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    def test_join_flashsystem_grid(self,
                                   svc_run_command_mock,
                                   svc_authorize_mock,
                                   svc_obj_info_mock):
        '''
        Test joining a flashsystem grid from a new cluster
        '''
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'target_cluster_name': '1.2.3.4',
            'truststore': 'ts0',
            'action': 'join',
            'state': 'present'
        })

        svc_obj_info_mock.return_value = ""
        svc_run_command_mock.return_value = ""

        fg = IBMSVFlashsystemGridMgmt()
        with pytest.raises(AnsibleExitJson) as exc:
            fg.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_flashsystem_grid.IBMSVFlashsystemGridMgmt.get_cluster_role')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_join_flashsystem_grid_idempotency(self,
                                               svc_authorize_mock,
                                               svc_obj_info_mock,
                                               get_cluster_role_mock):
        '''
        Test joining same flashsystem grid again which is already joined (idempotency)
        '''
        set_module_args({
            'clustername': '1.2.3.4',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'target_cluster_name': '1.2.3.5',
            'truststore': 'ts0',
            'action': 'join',
            'state': 'present'
        })

        svc_obj_info_mock.return_value = [
            {"id": "0", "member_address": "", "role": "member"},
            {"id": "1", "member_address": "1.2.3.5", "role": "coordinator"},
            {"id": "2", "member_address": "1.2.3.6", "role": "member"}
        ]

        get_cluster_role_mock.side_effect = ["member", "coordinator"]

        fg = IBMSVFlashsystemGridMgmt()
        with pytest.raises(AnsibleExitJson) as exc:
            fg.apply()
        self.assertFalse(exc.value.args[0]['changed'])
        self.assertEqual(exc.value.args[0]['msg'],
                         "(1.2.3.4) is already member of flashsystem grid with coordinator (1.2.3.5)")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_flashsystem_grid.IBMSVFlashsystemGridMgmt.get_cluster_role')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_coordinator_joining_flashsystem_grid(self,
                                                          svc_authorize_mock,
                                                          svc_obj_info_mock,
                                                          get_cluster_role_mock):
        '''
        Test joining same flashsystem grid again which is already joined (idempotency)
        '''
        set_module_args({
            'clustername': '1.2.3.4',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'target_cluster_name': '1.2.3.10',
            'truststore': 'ts0',
            'action': 'join',
            'state': 'present'
        })

        svc_obj_info_mock.return_value = [
            {"id": "0", "member_address": "", "role": "coordinator"},
            {"id": "1", "member_address": "1.2.3.5", "role": "member"},
            {"id": "2", "member_address": "1.2.3.6", "role": "member"}
        ]

        get_cluster_role_mock.side_effect = ["coordinator", None]

        fg = IBMSVFlashsystemGridMgmt()
        with pytest.raises(AnsibleFailJson) as exc:
            fg.apply()
        self.assertTrue(exc.value.args[0]['failed'])
        self.assertEqual(exc.value.args[0]['msg'],
                         "CMMVC6036E This system is flashsystem grid coordinator")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_flashsystem_grid.IBMSVFlashsystemGridMgmt.get_cluster_role')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    def test_accept_member_into_flashsystem_grid(self,
                                                 svc_run_command_mock,
                                                 svc_authorize_mock,
                                                 svc_obj_info_mock,
                                                 get_cluster_role_mock):
        '''
        Test joining a flashsystem grid from a new cluster
        '''
        set_module_args({
            'clustername': '1.2.3.4',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'target_cluster_name': '1.2.3.10',
            'truststore': 'ts0',
            'action': 'accept',
            'state': 'present'
        })

        svc_obj_info_mock.return_value = [
            {"id": "0", "member_address": "", "role": "coordinator"},
            {"id": "1", "member_address": "1.2.3.5", "role": "member"},
            {"id": "2", "member_address": "1.2.3.6", "role": "member"}
        ]
        svc_run_command_mock.return_value = ""
        get_cluster_role_mock.return_value = ["coordinator", None]

        fg = IBMSVFlashsystemGridMgmt()
        with pytest.raises(AnsibleExitJson) as exc:
            fg.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_flashsystem_grid.IBMSVFlashsystemGridMgmt.get_cluster_role')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_accept_member_into_flashsystem_grid_idempotency(self,
                                                             svc_authorize_mock,
                                                             svc_obj_info_mock,
                                                             get_cluster_role_mock):
        '''
        Test joining same flashsystem grid again which is already joined (idempotency)
        '''
        set_module_args({
            'clustername': '1.2.3.4',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'target_cluster_name': '1.2.3.5',
            'truststore': 'ts0',
            'action': 'accept',
            'state': 'present'
        })

        svc_obj_info_mock.return_value = [
            {"id": "0", "member_address": "", "role": "coordinator"},
            {"id": "1", "member_address": "1.2.3.5", "role": "member"},
            {"id": "2", "member_address": "1.2.3.6", "role": "member"}
        ]

        get_cluster_role_mock.side_effect = ["coordinator", "member"]

        fg = IBMSVFlashsystemGridMgmt()
        with pytest.raises(AnsibleExitJson) as exc:
            fg.apply()
        self.assertFalse(exc.value.args[0]['changed'])
        self.assertEqual(exc.value.args[0]['msg'],
                         "(1.2.3.5) is already member of flashsystem grid with coordinator (1.2.3.4)")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_flashsystem_grid.IBMSVFlashsystemGridMgmt.get_cluster_role')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    def test_remove_member_from_flashsystem_grid(self,
                                                 svc_run_command_mock,
                                                 svc_authorize_mock,
                                                 svc_obj_info_mock,
                                                 get_cluster_role_mock):
        '''
        Test removing a flashsystem member
        '''
        set_module_args({
            'clustername': '1.2.3.4',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'target_cluster_name': '1.2.3.5',
            'action': 'remove',
            'state': 'present'
        })

        svc_obj_info_mock.return_value = [
            {"id": "0", "member_address": "", "role": "coordinator"},
            {"id": "1", "member_address": "1.2.3.5", "role": "member"},
            {"id": "2", "member_address": "1.2.3.6", "role": "member"}
        ]
        svc_run_command_mock.return_value = ""
        get_cluster_role_mock.side_effect = ["coordinator", "member"]

        fg = IBMSVFlashsystemGridMgmt()
        with pytest.raises(AnsibleExitJson) as exc:
            fg.apply()
        self.assertTrue(exc.value.args[0]['changed'])
        self.assertEqual(exc.value.args[0]['msg'],
                         "Removed flashsystem-grid member (1.2.3.5) successfully")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_flashsystem_grid.IBMSVFlashsystemGridMgmt.get_cluster_role')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_member_from_flashsystem_grid_idempotency(self,
                                                             svc_authorize_mock,
                                                             svc_obj_info_mock,
                                                             get_cluster_role_mock):
        '''
        Test removing a non-existing member from flashsystem grid
        '''
        set_module_args({
            'clustername': '1.2.3.4',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'target_cluster_name': '1.2.3.10',
            'action': 'remove',
            'state': 'present'
        })

        svc_obj_info_mock.return_value = [
            {"id": "0", "member_address": "", "role": "coordinator"},
            {"id": "1", "member_address": "1.2.3.5", "role": "member"},
            {"id": "2", "member_address": "1.2.3.6", "role": "member"}
        ]

        get_cluster_role_mock.side_effect = ["coordinator", None]

        fg = IBMSVFlashsystemGridMgmt()
        with pytest.raises(AnsibleExitJson) as exc:
            fg.apply()
        self.assertFalse(exc.value.args[0]['changed'])
        self.assertEqual(exc.value.args[0]['msg'],
                         "(1.2.3.10) is not a flashsystem grid member.")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_mutually_exclusive_params(self, svc_authorize_mock):
        '''
        Test mutually exclusive parameters name and target_cluster_name during create operation
        '''
        set_module_args({
            'clustername': '1.2.3.4',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'fg0',
            'target_cluster_name': '1.2.3.10',
            'state': 'present'
        })

        with pytest.raises(AnsibleFailJson) as exc:
            fg = IBMSVFlashsystemGridMgmt()
            fg.apply()
        self.assertTrue(exc.value.args[0]['failed'])
        self.assertEqual(exc.value.args[0]['msg'],
                         'Parameter name is mutually exclusive with action and target_cluster_name')

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_missing_dependent_params_1(self, svc_authorize_mock):
        '''
        Test failure due to missing dependent parameter target_cluster_name
        to be used with action during join action
        '''
        set_module_args({
            'clustername': '1.2.3.4',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'action': 'join',
            'truststore': 'ts0',
            'state': 'present'
        })

        with pytest.raises(AnsibleFailJson) as exc:
            fg = IBMSVFlashsystemGridMgmt()
            fg.apply()
        self.assertTrue(exc.value.args[0]['failed'])
        self.assertEqual(exc.value.args[0]['msg'],
                         'action and target_cluster_name must be provided together')

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_missing_dependent_params_2(self, svc_authorize_mock):
        '''
        Test failure due to missing dependent parameter truststore
        to be used with action during join action
        '''
        set_module_args({
            'clustername': '1.2.3.4',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'action': 'join',
            'target_cluster_name': '1.2.3.5',
            'state': 'present'
        })

        with pytest.raises(AnsibleFailJson) as exc:
            fg = IBMSVFlashsystemGridMgmt()
            fg.apply()
        self.assertTrue(exc.value.args[0]['failed'])
        self.assertEqual(exc.value.args[0]['msg'],
                         'action (join) must be provided with truststore.')

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_invalid_params_during_fg_delete(self,
                                                     svc_authorize_mock):
        '''
        Test failure due to presence of invalid parameters target_cluster_name
        to be used with action during join action
        '''
        set_module_args({
            'clustername': '1.2.3.4',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'target_cluster_name': '1.2.3.5',
            'truststore': 'ts0',
            'state': 'absent'
        })

        with pytest.raises(AnsibleFailJson) as exc:
            fg = IBMSVFlashsystemGridMgmt()
            fg.apply()
        self.assertTrue(exc.value.args[0]['failed'])
        self.assertEqual(exc.value.args[0]['msg'],
                         'Invalid parameter(s) for state=absent: target_cluster_name, truststore')


if __name__ == '__main__':
    unittest.main()
