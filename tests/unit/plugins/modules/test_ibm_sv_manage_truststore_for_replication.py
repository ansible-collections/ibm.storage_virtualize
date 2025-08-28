# Copyright (C) 2020 IBM CORPORATION
# Author(s): Sanjaikumaar M <sanjaikumaar.m@ibm.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Storage Virtualize Ansible module: ibm_sv_manage_truststore_for_replication """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch, Mock
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.storage_virtualize.plugins.modules.ibm_sv_manage_truststore_for_replication import (
    IBMSVTrustStore
)
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


class TestIBMSVTrustStore(unittest.TestCase):

    def setUp(self):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    def test_missing_mandatory_parameter_name(self):
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'state': 'present'
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                IBMSVTrustStore()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible.module_utils.compat.paramiko.paramiko.SSHClient')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.'
           'module_utils.ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_create_truststore(self, svc_connect_mock, ssh_mock):
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'truststore1',
            'remote_clustername': 'x.x.x.x',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password',
            'state': 'present'
        }):
            con_mock = Mock()
            svc_connect_mock.return_value = True
            ssh_mock.return_value = con_mock
            stdin = Mock()
            stdout = Mock()
            stderr = Mock()
            con_mock.exec_command.return_value = (stdin, stdout, stderr)
            stdout.read.side_effect = iter([br'{}', b'', b''])
            stdout.channel.recv_exit_status.return_value = 0

            ts = IBMSVTrustStore()

            with pytest.raises(AnsibleExitJson) as exc:
                ts.apply()

            self.assertTrue(exc.value.args[0]['changed'])
            self.assertTrue('truststore1' in exc.value.args[0]['msg'])

    @patch('ansible.module_utils.compat.paramiko.paramiko.SSHClient')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.'
           'module_utils.ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_create_truststore_idempotency(self, svc_connect_mock, ssh_mock):
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'truststore1',
            'remote_clustername': 'x.x.x.x',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password',
            'state': 'present'
        }):
            con_mock = Mock()
            svc_connect_mock.return_value = True
            ssh_mock.return_value = con_mock
            stdin = Mock()
            stdout = Mock()
            stderr = Mock()
            con_mock.exec_command.return_value = (stdin, stdout, stderr)
            stdout.read.side_effect = iter([br'{"name":"truststore1"}', b'', b''])
            stdout.channel.recv_exit_status.return_value = 0

            ts = IBMSVTrustStore()

            with pytest.raises(AnsibleExitJson) as exc:
                ts.apply()

            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible.module_utils.compat.paramiko.paramiko.SSHClient')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.'
           'module_utils.ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_delete_truststore(self, svc_connect_mock, ssh_mock):
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'truststore1',
            'state': 'absent'
        }):
            con_mock = Mock()
            svc_connect_mock.return_value = True
            ssh_mock.return_value = con_mock
            stdin = Mock()
            stdout = Mock()
            stderr = Mock()
            con_mock.exec_command.return_value = (stdin, stdout, stderr)
            stdout.read.side_effect = iter([br'{"name": "truststore1"}', b'', b''])
            stdout.channel.recv_exit_status.return_value = 0

            ts = IBMSVTrustStore()

            with pytest.raises(AnsibleExitJson) as exc:
                ts.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible.module_utils.compat.paramiko.paramiko.SSHClient')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.'
           'module_utils.ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_delete_truststore_idempotency(self, svc_connect_mock, ssh_mock):
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'truststore1',
            'state': 'absent'
        }):
            con_mock = Mock()
            svc_connect_mock.return_value = True
            ssh_mock.return_value = con_mock
            stdin = Mock()
            stdout = Mock()
            stderr = Mock()
            con_mock.exec_command.return_value = (stdin, stdout, stderr)
            stdout.read.side_effect = iter([br'{}', b'', b''])
            stdout.channel.recv_exit_status.return_value = 0

            ts = IBMSVTrustStore()

            with pytest.raises(AnsibleExitJson) as exc:
                ts.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible.module_utils.compat.paramiko.paramiko.SSHClient')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.'
           'module_utils.ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_create_truststore_with_syslog_and_restapi_on(self, svc_connect_mock, ssh_mock):
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'truststore1',
            'remote_clustername': 'x.x.x.x',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password',
            'state': 'present',
            'syslog': 'on',
            'restapi': 'on'
        }):
            con_mock = Mock()
            svc_connect_mock.return_value = True
            ssh_mock.return_value = con_mock
            stdin = Mock()
            stdout = Mock()
            stderr = Mock()
            con_mock.exec_command.return_value = (stdin, stdout, stderr)
            stdout.read.side_effect = iter([br'{}', b'', b''])
            stdout.channel.recv_exit_status.return_value = 0

            ts = IBMSVTrustStore()

            with pytest.raises(AnsibleExitJson) as exc:
                ts.apply()

            self.assertTrue(exc.value.args[0]['changed'])
            self.assertTrue('truststore1' in exc.value.args[0]['msg'])

    @patch('ansible.module_utils.compat.paramiko.paramiko.SSHClient')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.'
           'module_utils.ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_create_truststore_with_ipsec_and_vasa(self, svc_connect_mock, ssh_mock):
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'truststore1',
            'remote_clustername': 'x.x.x.x',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password',
            'state': 'present',
            'ipsec': 'on',
            'vasa': 'on'
        }):
            con_mock = Mock()
            svc_connect_mock.return_value = True
            ssh_mock.return_value = con_mock
            stdin = Mock()
            stdout = Mock()
            stderr = Mock()
            con_mock.exec_command.return_value = (stdin, stdout, stderr)
            stdout.read.side_effect = iter([br'{}', b'', b''])
            stdout.channel.recv_exit_status.return_value = 0

            ts = IBMSVTrustStore()

            with pytest.raises(AnsibleExitJson) as exc:
                ts.apply()

            self.assertTrue(exc.value.args[0]['changed'])
            self.assertTrue('truststore1' in exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_truststore_for_replication.IBMSVTrustStore.is_truststore_present')
    @patch('ansible.module_utils.compat.paramiko.paramiko.SSHClient')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.'
           'module_utils.ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_update_truststore_props_ipsec_and_vasa(self,
                                                    svc_connect_mock,
                                                    ssh_mock,
                                                    is_truststore_present_mock):
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'truststore1',
            'state': 'present',
            'ipsec': 'on',
            'syslog': 'on',
            'snmp': 'on'
        }):
            is_truststore_present_mock.return_value = {
                "name": "truststore1",
                "ipsec": "off",
                "syslog": "off",
                "snmp": "on"
            }

            con_mock = Mock()
            svc_connect_mock.return_value = True
            ssh_mock.return_value = con_mock
            stdin = Mock()
            stdout = Mock()
            stderr = Mock()
            con_mock.exec_command.return_value = (stdin, stdout, stderr)
            stdout.read.side_effect = iter([br'{}', b'', b''])
            stdout.channel.recv_exit_status.return_value = 0

            ts = IBMSVTrustStore()

            with pytest.raises(AnsibleExitJson) as exc:
                ts.apply()

            self.assertTrue(exc.value.args[0]['changed'])
            self.assertTrue('truststore1' in exc.value.args[0]['msg'])

    @patch('ansible.module_utils.compat.paramiko.paramiko.SSHClient')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.'
           'module_utils.ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_create_truststore_for_flashsystem_grid(self, svc_connect_mock, ssh_mock):
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'truststore1',
            'remote_clustername': 'x.x.x.x',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password',
            'state': 'present',
            'grid': 'on'
        }):
            con_mock = Mock()
            svc_connect_mock.return_value = True
            ssh_mock.return_value = con_mock
            stdin = Mock()
            stdout = Mock()
            stderr = Mock()
            con_mock.exec_command.return_value = (stdin, stdout, stderr)
            stdout.read.side_effect = iter([br'{}', b'', b''])
            stdout.channel.recv_exit_status.return_value = 0

            ts = IBMSVTrustStore()

            with pytest.raises(AnsibleExitJson) as exc:
                ts.apply()

            self.assertTrue(exc.value.args[0]['changed'])
            self.assertTrue('truststore1' in exc.value.args[0]['msg'])

    @patch('ansible.module_utils.compat.paramiko.paramiko.SSHClient')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.'
           'module_utils.ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_create_truststore_for_flashsystem_grid_idempotency(self, svc_connect_mock, ssh_mock):
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'truststore1',
            'remote_clustername': 'x.x.x.x',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password',
            'state': 'present',
            'grid': 'on'
        }):
            con_mock = Mock()
            svc_connect_mock.return_value = True
            ssh_mock.return_value = con_mock
            stdin = Mock()
            stdout = Mock()
            stderr = Mock()
            con_mock.exec_command.return_value = (stdin, stdout, stderr)
            stdout.read.side_effect = iter([br'{"name": "truststore1", "grid_references": "0"}', b'', b''])
            stdout.channel.recv_exit_status.return_value = 0

            ts = IBMSVTrustStore()

            with pytest.raises(AnsibleExitJson) as exc:
                ts.apply()

            self.assertFalse(exc.value.args[0]['changed'])
            self.assertTrue('truststore1' in exc.value.args[0]['msg'])

    @patch('ansible.module_utils.compat.paramiko.paramiko.SSHClient')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.'
           'module_utils.ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_failure_update_existing_truststore_for_flashsystem_grid(self, svc_connect_mock, ssh_mock):
        '''
        Test failure while trying to update a truststore that was created for flashsystem grid.
        '''
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'truststore1',
            'remote_clustername': 'x.x.x.x',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password',
            'state': 'present',
            'email': 'on'
        }):
            con_mock = Mock()
            svc_connect_mock.return_value = True
            ssh_mock.return_value = con_mock
            stdin = Mock()
            stdout = Mock()
            stderr = Mock()
            con_mock.exec_command.return_value = (stdin, stdout, stderr)
            stdout.read.side_effect = iter([br'{"name": "truststore1", "grid_references": "0"}', b''])
            stdout.channel.recv_exit_status.side_effect = iter([0, 1])
            stderr.read.return_value = br'CMMVC1274E The command failed as the trust store entry is being used for another member of the grid.'

            ts = IBMSVTrustStore()

            with pytest.raises(AnsibleFailJson) as exc:
                ts.apply()

            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'],
                             'CMMVC1274E The command failed as the trust store entry is being used for another member of the grid.')

    @patch('ansible.module_utils.compat.paramiko.paramiko.SSHClient')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.'
           'module_utils.ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_failure_update_truststore_grid_attr(self, svc_connect_mock, ssh_mock):
        '''
        Test failure while trying to update a truststore attribute grid=on.
        '''
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'truststore1',
            'remote_clustername': 'x.x.x.x',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password',
            'state': 'present',
            'grid': 'on'
        }):
            con_mock = Mock()
            svc_connect_mock.return_value = True
            ssh_mock.return_value = con_mock
            stdin = Mock()
            stdout = Mock()
            stderr = Mock()
            con_mock.exec_command.return_value = (stdin, stdout, stderr)
            stdout.read.side_effect = iter([br'{"name": "truststore1", "grid_references": ""}', b'', b''])
            stdout.channel.recv_exit_status.return_value = 0

            ts = IBMSVTrustStore()

            with pytest.raises(AnsibleFailJson) as exc:
                ts.apply()

            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'],
                             'Invalid parameter for update: (grid)')


if __name__ == '__main__':
    unittest.main()
