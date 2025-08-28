# Copyright (C) 2020 IBM CORPORATION
# Author(s): Shilpi Jain <shilpi.jain1@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Storage Virtualize Ansible module: ibm_svcinfo_command """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils.compat.paramiko import paramiko
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.storage_virtualize.plugins.modules.ibm_svcinfo_command import IBMSVCsshClient
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


class TestIBMSVCsshClient(unittest.TestCase):

    def setUp(self):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    def set_default_args(self):
        return dict({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'command': 'svcinfo lsuser',
        })

    def test_ssh_connect_with_missing_username(self):
        with set_module_args({
            'clustername': 'clustername',
            'password': 'password',
            'command': 'svcinfo lsuser',
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                IBMSVCsshClient()
                print('Info: %s' % exc.value.args[0]['msg'])
                self.assertFalse(exc.value.args[0]['changed'])

    def test_ssh_connect_with_missing_password(self):
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'command': 'svcinfo lsuser',
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                IBMSVCsshClient()
                print('Info: %s' % exc.value.args[0]['msg'])
                self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_ssh_connect_with_password(self, connect_mock):
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'command': 'svcinfo cli_command',
        }):
            if paramiko is None:
                print("paramiko is not installed")

            patch.object(paramiko.SSHClient, 'exec_command')
            conn = IBMSVCsshClient()
            with pytest.raises(Exception) as exc:
                conn.send_svcinfo_command()
                print('Info: %s' % exc.value.args[0])
                self.assertTrue(conn.ssh_client.is_client_connected)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_ssh_connect_with_key(self, connect_mock):
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': '',
            'usesshkey': 'yes',
            'command': 'svcinfo lsuser',
        }):
            if paramiko is None:
                print("paramiko is not installed")

            patch.object(paramiko.SSHClient, 'exec_command')
            conn = IBMSVCsshClient()
            with pytest.raises(Exception) as exc:
                conn.send_svcinfo_command()
            print('Info: %s' % exc.value.args[0])
            self.assertTrue(conn.ssh_client.is_client_connected)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_ssh.IBMSVCssh._svc_connect')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_ssh.IBMSVCssh._svc_disconnect')
    def test_ssh_disconnect(self, connect_mock, disconnect_mock):
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'command': 'svcinfo lsuser',
        }):
            conn = IBMSVCsshClient()
            conn.is_client_connected = True
            conn.ssh_client._svc_disconnect()
            self.assertTrue(conn.ssh_client.is_client_connected)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_ssh_disconnect_failed(self, connect_mock):
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'command': 'svcinfo lsuser',
        }):
            conn = IBMSVCsshClient()
            conn.ssh_client._svc_disconnect()
            self.assertFalse(conn.ssh_client.is_client_connected)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_ssh_modify_command(self, connect_mock):
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'command': 'svcinfo lsuser',
        }):
            conn = IBMSVCsshClient()
            new_command = conn.modify_command("svcinfo lsuser user1")
            self.assertEqual(new_command, "svcinfo lsuser -json user1")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_ssh_modify_command_when_object_also_startswith_ls(self, connect_mock):
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'command': 'svcinfo lsuser lson',
        }):
            conn = IBMSVCsshClient()
            new_command = conn.modify_command("svcinfo lsuser lson")
            self.assertEqual(new_command, "svcinfo lsuser -json lson")


if __name__ == '__main__':
    unittest.main()
