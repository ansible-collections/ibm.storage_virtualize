# Copyright (C) 2022 IBM CORPORATION
# Author(s): Shilpi Jain<shilpi.jain1@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Storage Virtualize Ansible module: ibm_sv_manage_syslog_server """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.storage_virtualize.plugins.modules.ibm_sv_manage_syslog_server import IBMSVSyslogserver


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


class TestIBMSVSyslogserver(unittest.TestCase):
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
            IBMSVSyslogserver()
        self.assertTrue(exc.value.args[0]['failed'])

    def test_mutually_exclusive_case_1(self):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'server1',
            'cadf': 'on',
            'facility': 1,
            'state': 'present'
        })

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVSyslogserver()
        self.assertTrue(exc.value.args[0]['failed'])

    def test_mutually_exclusive_case_2(self):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'server1',
            'port': '1010',
            'state': 'present'
        })

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVSyslogserver()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_syslog_server.IBMSVSyslogserver.get_syslog_server_details')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_syslog_server_success(self,
                                          svc_authorize_mock,
                                          svc_run_command_mock,
                                          server_exist_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'server0',
            'ip': '1.1.1.1',
            'state': 'present'
        })

        server_exist_mock.return_value = {}
        p = IBMSVSyslogserver()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_syslog_server.IBMSVSyslogserver.get_syslog_server_details')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_syslog_server_with_optional_params(self,
                                                       svc_authorize_mock,
                                                       svc_run_command_mock,
                                                       server_exist_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'server',
            'state': 'present',
            'ip': '1.1.1.1',
            'info': 'off',
            'warning': 'off'
        })

        server_exist_mock.return_value = {}
        p = IBMSVSyslogserver()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_syslog_server_idempotency(self,
                                              svc_authorize_mock,
                                              svc_run_command_mock,
                                              svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'server0',
            'state': 'present'
        })

        svc_obj_info_mock.return_value = {
            "id": "1",
            "name": "server0",
            "IP_address": "1.1.1.1",
            "error": "on",
            "warning": "on",
            "info": "on",
            "cadf": "off",
            "audit": "off",
            "login": "off",
            "facility": "0",
            "protocol": "udp",
            "port": "514"
        }
        p = IBMSVSyslogserver()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_syslog_server(self,
                                  svc_authorize_mock,
                                  svc_run_command_mock,
                                  svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'server0',
            'ip': '1.1.1.1',
            'info': 'off',
            'state': 'present'
        })

        svc_obj_info_mock.return_value = {
            "id": "1",
            "name": "server0",
            "IP_address": "1.1.1.1",
            "error": "on",
            "warning": "on",
            "info": "on",
            "cadf": "off",
            "audit": "off",
            "login": "off",
            "facility": "0",
            "protocol": "udp",
            "port": "514"
        }
        p = IBMSVSyslogserver()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_rename_syslog_server(self, svc_authorize_mock,
                                  svc_run_command_mock,
                                  svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'new_server0',
            'old_name': 'server0',
            'state': 'present'
        })
        svc_obj_info_mock.return_value = {
            "id": "1",
            "name": "server0",
            "IP_address": "1.1.1.1",
            "error": "on",
            "warning": "on",
            "info": "on",
            "cadf": "off",
            "audit": "off",
            "login": "off",
            "facility": "0",
            "protocol": "udp",
            "port": "514"
        }

        arg_data = []
        v = IBMSVSyslogserver()
        data = v.rename_server(arg_data)
        self.assertEqual(data, 'Syslog server [server0] has been successfully rename to [new_server0].')

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_syslog_server.IBMSVSyslogserver.get_syslog_server_details')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_syslog_server_with_invalid_param(self,
                                                     svc_authorize_mock,
                                                     svc_run_command_mock,
                                                     server_exist_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'server0',
            'ip': '1.1.1.1',
            'error': 'off',
            'state': 'absent'
        })

        server_exist_mock.return_value = {
            "id": "1",
            "name": "server0",
            "IP_address": "1.1.1.1",
            "error": "on",
            "warning": "on",
            "info": "on",
            "cadf": "off",
            "audit": "off",
            "login": "off",
            "facility": "0",
            "protocol": "udp",
            "port": "514"
        }

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVSyslogserver()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_syslog_server.IBMSVSyslogserver.get_syslog_server_details')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_syslog_server(self, svc_authorize_mock,
                                  svc_run_command_mock,
                                  server_exist_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'server0',
            'state': 'absent'
        })

        server_exist_mock.return_value = {
            "id": "1",
            "name": "server0",
            "IP_address": "1.1.1.1",
            "error": "on",
            "warning": "on",
            "info": "on",
            "cadf": "off",
            "audit": "off",
            "login": "off",
            "facility": "0",
            "protocol": "udp",
            "port": "514"
        }
        p = IBMSVSyslogserver()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_syslog_server.IBMSVSyslogserver.get_syslog_server_details')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_syslog_server_idempotency(self, svc_authorize_mock,
                                              svc_run_command_mock,
                                              server_exist_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'server0',
            'state': 'absent'
        })

        server_exist_mock.return_value = {}
        p = IBMSVSyslogserver()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_syslog_server.IBMSVSyslogserver.get_syslog_server_details')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_syslog_server_with_tls(self,
                                           svc_authorize_mock,
                                           svc_run_command_mock,
                                           server_exist_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'server1',
            'ip': '1.1.1.1',
            'state': 'present',
            'protocol': 'tls'
        })

        server_exist_mock.return_value = {}
        p = IBMSVSyslogserver()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_protocol_syslog_server(self,
                                           svc_authorize_mock,
                                           svc_run_command_mock,
                                           svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'server1',
            'ip': '1.1.1.1',
            'state': 'present',
            'protocol': 'tls'
        })

        svc_obj_info_mock.return_value = {
            "id": "1",
            "name": "server1",
            "IP_address": "1.1.1.1",
            "error": "on",
            "warning": "on",
            "info": "on",
            "cadf": "off",
            "audit": "off",
            "login": "off",
            "facility": "0",
            "protocol": "udp",
            "port": "514"
        }
        p = IBMSVSyslogserver()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_protocol_syslog_server_to_tls(self,
                                                  svc_authorize_mock,
                                                  svc_run_command_mock,
                                                  svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'server1',
            'ip': '1.1.1.1',
            'state': 'present',
            'protocol': 'tcp'
        })

        svc_obj_info_mock.return_value = {
            "id": "1",
            "name": "server1",
            "IP_address": "1.1.1.1",
            "error": "on",
            "warning": "on",
            "info": "on",
            "cadf": "off",
            "audit": "off",
            "login": "off",
            "facility": "0",
            "protocol": "tls",
            "port": "6514"
        }
        p = IBMSVSyslogserver()

        with pytest.raises(AnsibleExitJson) as exc:
            p.apply()
        self.assertTrue(exc.value.args[0]['changed'])


if __name__ == '__main__':
    unittest.main()
