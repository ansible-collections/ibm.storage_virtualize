# Copyright (C) 2023 IBM CORPORATION
# Author(s): Sudheesh Reddy Satti<Sudheesh.Reddy.Satti@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Storage Virtualize Ansible module: ibm_sv_manage_fcportsetmember """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.storage_virtualize.plugins.modules.ibm_sv_manage_fcportsetmember import \
    IBMSVFCPortsetmember
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


class TestIBMSVFCPortsetmember(unittest.TestCase):
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

    # ------------------------------------------------------------------ #
    #  basic_checks: mandatory parameter validation                        #
    # ------------------------------------------------------------------ #

    def test_missing_name_fails(self):
        """basic_checks: blank name must raise fail_json"""
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': '',
            'fcportid': '1',
            'state': 'present'
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                IBMSVFCPortsetmember()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertIn('name', exc.value.args[0]['msg'])

    def test_missing_fcportid_fails(self):
        """basic_checks: blank fcportid must raise fail_json"""
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'fcportid': '',
            'state': 'present'
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                IBMSVFCPortsetmember()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertIn('fcportid', exc.value.args[0]['msg'])

    # ------------------------------------------------------------------ #
    #  state=present: add member                                           #
    # ------------------------------------------------------------------ #

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_add_fcportsetmember(self,
                                 svc_authorize_mock,
                                 svc_run_command_mock,
                                 svc_obj_info_mock):
        """state=present, capable port, not in portset → 1 addfcportsetmember call, changed=True"""
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'fcportid': '1',
            'state': 'present'
        }):
            svc_obj_info_mock.return_value = {}
            svc_run_command_mock.return_value = None
            with pytest.raises(AnsibleExitJson) as exc:
                p = IBMSVFCPortsetmember()
                p.apply()
            self.assertTrue(exc.value.args[0]['changed'])
            self.assertEqual(svc_run_command_mock.call_count, 1)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_add_fcportsetmember_idempotency(self,
                                             svc_authorize_mock,
                                             svc_obj_info_mock):
        """state=present, port already in portset → no command run, changed=False"""
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'fcportid': '1',
            'state': 'present'
        }):
            svc_obj_info_mock.return_value = {
                "id": "1",
                "portset_id": "0",
                "portset_name": "portset0",
                "fc_io_port_id": "1"
            }
            with pytest.raises(AnsibleExitJson) as exc:
                p = IBMSVFCPortsetmember()
                p.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    # ------------------------------------------------------------------ #
    #  state=present: autozone incapable port                             #
    # ------------------------------------------------------------------ #

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_add_fcportsetmember_autozone_incapable_fails(self,
                                                          svc_authorize_mock,
                                                          svc_run_command_mock,
                                                          svc_obj_info_mock):
        """CMMVC1517E without ignoreautozoneincapable flag → fail_json with message"""
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'fcportid': '2',
            'state': 'present'
        }):
            svc_obj_info_mock.return_value = {}
            svc_run_command_mock.side_effect = Exception(
                'CMMVC1517E The command failed because the Fibre Channel IO port being added is not auto zoning capable'
            )
            with pytest.raises(AnsibleFailJson) as exc:
                p = IBMSVFCPortsetmember()
                p.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertIn('not auto zoning capable', exc.value.args[0]['msg'])
            self.assertEqual(svc_run_command_mock.call_count, 1)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.get_system_code_level')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_add_fcportsetmember_autozone_incapable_with_ignore_flag(self,
                                                                     svc_authorize_mock,
                                                                     svc_run_command_mock,
                                                                     svc_obj_info_mock,
                                                                     get_code_level_mock):
        """CMMVC1517E handled by user setting ignoreautozoneincapable=True"""
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'fcportid': '2',
            'ignoreautozoneincapable': True,
            'state': 'present'
        }):
            svc_obj_info_mock.return_value = {}
            get_code_level_mock.return_value = '9.1.2.0'
            svc_run_command_mock.return_value = None
            with pytest.raises(AnsibleExitJson) as exc:
                p = IBMSVFCPortsetmember()
                p.apply()
            self.assertTrue(exc.value.args[0]['changed'])
            self.assertEqual(svc_run_command_mock.call_count, 1)
            cmdopts = svc_run_command_mock.call_args[0][1]
            self.assertTrue(cmdopts.get('ignoreautozoneincapable'))

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.get_system_code_level')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_add_fcportsetmember_ignore_flag_unsupported_firmware(self,
                                                                  svc_authorize_mock,
                                                                  svc_obj_info_mock,
                                                                  get_code_level_mock):
        """ignoreautozoneincapable flag used on firmware < 9.1.2.0 → fail_json"""
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'fcportid': '2',
            'ignoreautozoneincapable': True,
            'state': 'present'
        }):
            svc_obj_info_mock.return_value = {}
            get_code_level_mock.return_value = '9.1.0.0'
            with pytest.raises(AnsibleFailJson) as exc:
                p = IBMSVFCPortsetmember()
                p.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertIn('9.1.2.0', exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_add_fcportsetmember_other_error_no_retry(self,
                                                      svc_authorize_mock,
                                                      svc_run_command_mock,
                                                      svc_obj_info_mock):
        """Non-CMMVC1517E error → fail_json immediately, no retry, no version check"""
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'fcportid': '3',
            'state': 'present'
        }):
            svc_obj_info_mock.return_value = {}
            svc_run_command_mock.side_effect = Exception('CMMVC5753E The specified object does not exist')
            with pytest.raises(AnsibleFailJson) as exc:
                p = IBMSVFCPortsetmember()
                p.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertIn('CMMVC5753E', exc.value.args[0]['msg'])
            self.assertEqual(svc_run_command_mock.call_count, 1)

    # ------------------------------------------------------------------ #
    #  state=absent: remove member                                         #
    # ------------------------------------------------------------------ #

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_fcportsetmember(self,
                                    svc_authorize_mock,
                                    svc_run_command_mock,
                                    svc_obj_info_mock):
        """state=absent, port in portset → rmfcportsetmember called, changed=True"""
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'fcportid': '1',
            'state': 'absent'
        }):
            svc_obj_info_mock.return_value = {
                "id": "1",
                "portset_id": "0",
                "portset_name": "portset0",
                "fc_io_port_id": "1"
            }
            svc_run_command_mock.return_value = None
            with pytest.raises(AnsibleExitJson) as exc:
                p = IBMSVFCPortsetmember()
                p.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_fcportsetmember_idempotency(self,
                                                svc_authorize_mock,
                                                svc_obj_info_mock):
        """state=absent, port not in portset → no command run, changed=False"""
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'fcportid': '1',
            'state': 'absent'
        }):
            svc_obj_info_mock.return_value = {}
            with pytest.raises(AnsibleExitJson) as exc:
                p = IBMSVFCPortsetmember()
                p.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    # ------------------------------------------------------------------ #
    #  check_mode                                                          #
    # ------------------------------------------------------------------ #

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_add_fcportsetmember_check_mode(self,
                                            svc_authorize_mock,
                                            svc_run_command_mock,
                                            svc_obj_info_mock):
        """check_mode + state=present: svc_run_command never called, msg signals check mode"""
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'fcportid': '1',
            'state': 'present',
            '_ansible_check_mode': True
        }):
            svc_obj_info_mock.return_value = {}
            with pytest.raises(AnsibleExitJson) as exc:
                p = IBMSVFCPortsetmember()
                p.apply()
            svc_run_command_mock.assert_not_called()
            self.assertIn('check mode', exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_fcportsetmember_check_mode(self,
                                               svc_authorize_mock,
                                               svc_run_command_mock,
                                               svc_obj_info_mock):
        """check_mode + state=absent: svc_run_command never called, msg signals check mode"""
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'fcportid': '1',
            'state': 'absent',
            '_ansible_check_mode': True
        }):
            svc_obj_info_mock.return_value = {
                "id": "1",
                "portset_id": "0",
                "portset_name": "portset0",
                "fc_io_port_id": "1"
            }
            with pytest.raises(AnsibleExitJson) as exc:
                p = IBMSVFCPortsetmember()
                p.apply()
            svc_run_command_mock.assert_not_called()
            self.assertIn('check mode', exc.value.args[0]['msg'])


if __name__ == '__main__':
    unittest.main()
