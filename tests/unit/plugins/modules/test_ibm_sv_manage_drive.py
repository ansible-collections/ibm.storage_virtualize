# Copyright (C) 2023 IBM CORPORATION
# Author(s): Sumit Kumar Gupta <sumit.gupta16@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Storage Virtualize Ansible module: ibm_sv_manage_drive """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.storage_virtualize.plugins.modules.ibm_sv_manage_drive import IBMSVDriveMgmt


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


class TestIBMSVDriveMgmt(unittest.TestCase):
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
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    def test_change_drive_state(self,
                                svc_run_command_mock,
                                svc_authorize_mock):
        '''
        Test drive state change to a permissible state (e.g. candidate, unused)
        '''

        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'drive_state': 'candidate',
            'drive_id': 10
        })

        rp = IBMSVDriveMgmt()
        svc_run_command_mock.return_value = ""

        with pytest.raises(AnsibleExitJson) as exc:
            rp.apply()
            print(exc.value.args[0])
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    def test_perform_drive_task(self,
                                lsdriveprogress_mock,
                                svc_run_command_mock,
                                svc_authorize_mock):
        '''
        Perform a drive task (e.g. format, erase)
        '''

        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'task': 'format',
            'drive_id': 10
        })

        lsdriveprogress_mock.return_value = ""
        rp = IBMSVDriveMgmt()
        svc_run_command_mock.return_value = ""

        with pytest.raises(AnsibleExitJson) as exc:
            rp.apply()
            print(exc.value.args[0])
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    def test_trigger_dump_on_drive(self,
                                   svc_run_command_mock,
                                   svc_authorize_mock):
        '''
        Test performing a drive task (e.g. format, erase) when another task is in progress; should fail
        '''

        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'task': 'triggerdump',
            'drive_id': 10
        })

        rp = IBMSVDriveMgmt()
        svc_run_command_mock.return_value = ""

        with pytest.raises(AnsibleExitJson) as exc:
            rp.apply()
            print(exc.value.args[0])
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    def test_repeat_ongoing_task_on_drive(self,
                                          svc_run_command_mock,
                                          svc_authorize_mock,
                                          svc_obj_info_mock):
        '''
        Test performing a drive task (e.g. format, erase) when same task is in progress
        Test for idempotency of drive task
        '''

        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'task': 'erase',
            'drive_id': 10
        })

        svc_obj_info_mock.return_value = {
            "id": "10",
            "task": "erase",
            "progress": "25",
            "estimated_completion_time": "240603112838"
        }
        rp = IBMSVDriveMgmt()
        svc_run_command_mock.return_value = ""

        with pytest.raises(AnsibleExitJson) as exc:
            rp.apply()
            print(exc.value.args[0])
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_perform_different_task_than_ongoing_task_on_drive(self,
                                                                       svc_authorize_mock,
                                                                       lsdriveprogress_mock):
        '''
        Test performing a drive task (e.g. format, erase)
        when a different task is in progress; should fail
        '''

        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'task': 'erase',
            'drive_id': 10
        })

        lsdriveprogress_mock.return_value = {
            "id": "10",
            "task": "format",
            "progress": "25",
            "estimated_completion_time": "240603112838"
        }
        rp = IBMSVDriveMgmt()

        with pytest.raises(AnsibleFailJson) as exc:
            rp.apply()
            print(exc.value.args[0])

        self.assertIn("CMMVC6625E", exc.value.args[0]['msg'])
        print(exc.value.args[0])
        self.assertTrue(exc.value.args[0]['failed'])


if __name__ == '__main__':
    unittest.main()
