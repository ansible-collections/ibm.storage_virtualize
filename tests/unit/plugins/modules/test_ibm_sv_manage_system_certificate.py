# Copyright (C) 2020 IBM CORPORATION
# Author(s): Sandip Gulab Rajbanshi <sandip.rajbanshi@ibm.com>

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
from ansible_collections.ibm.storage_virtualize.plugins.modules.ibm_sv_manage_system_certificate import (
    IBMSVManageSystemCert
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


class TestIBMSVManageSystemCert(unittest.TestCase):

    def setUp(self):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    def test_missing_mandatory_parameter(self):
        '''
        ##################################################################################
        Case 1
        Parameter: remote_truststore_name, remote_clustername,
        remote_username, and remote_password are missing when state is 'present'.
        ##################################################################################
        '''
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'state': 'present',
            'primary_truststore_name': 'Truststore1',
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                IBMSVManageSystemCert()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'],
                             "state is present but all of the following are missing: remote_clustername, "
                             "remote_username, remote_password, remote_truststore_name")

        '''
        ##################################################################################
        Case 2
        Parameter primary_trustsore_name is missing when state is 'absent'.
        ##################################################################################
        '''
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'state': 'absent'
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                IBMSVManageSystemCert()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'],
                             "missing required arguments: primary_truststore_name")

    @patch('ansible.module_utils.compat.paramiko.paramiko.SSHClient')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.'
           'module_utils.ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_create_truststore(self,
                               svc_connect_mock,
                               ssh_mock):
        '''
        ##################################################################################
        Case 1: Create truststore on both clusters when it does not exist.
        ##################################################################################
        '''
        with set_module_args({
            'clustername': 'system1',
            'username': 'username',
            'password': 'password',
            'state': 'present',
            'primary_truststore_name': 'Truststore1',
            'remote_truststore_name': 'Truststore2',
            'remote_clustername': 'system2',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password'
        }):

            with (patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
                        'ibm_sv_manage_system_certificate.IBMSVManageSystemCert._execute_command'
                        ) as mock_execute_command,
                  pytest.raises(AnsibleExitJson) as exc):

                lstruststore_op = None
                system_info_1 = {'id': '000002042E698S',
                                 'name': 'primary',
                                 'code_level': '9.1.0.0'}
                system_info_2 = {'id': '000002042E698R',
                                 'name': 'remote',
                                 'code_level': '9.1.0.0'}
                lssystemcertstore_op = {"id": "3",
                                        "scope": "internal_communication",
                                        "certificate_id": "0x687894bb",
                                        "type": "system_signed"}
                export_cert_op = None
                truststore_create_op = None

                system_mock_info = [lstruststore_op, system_info_1,
                                    system_info_2, lssystemcertstore_op,
                                    export_cert_op, truststore_create_op,
                                    lstruststore_op, lssystemcertstore_op,
                                    export_cert_op, truststore_create_op]

                mock_execute_command.side_effect = system_mock_info

                con_mock = Mock()
                svc_connect_mock.return_value = True
                ssh_mock.return_value = con_mock
                stdin = Mock()
                stdout = Mock()
                stderr = Mock()
                con_mock.exec_command.return_value = (stdin, stdout, stderr)
                stdout.channel.recv_exit_status.return_value = 0
                stdout.read.side_effect = [b'', b'']

                v = IBMSVManageSystemCert()
                v.apply()

            self.assertTrue(exc.value.args[0]['changed'])
            self.assertEqual(exc.value.args[0]['msg'],
                             "Truststore {0} created successfully on cluster {1}. "
                             "Truststore {2} created successfully on cluster {3}. "
                             .format('Truststore2', 'system2', 'Truststore1', 'system1'))
            self.assertEqual(mock_execute_command.call_count, 10)
            mock_execute_command.reset_mock()

        '''
        ##################################################################################
        Case 2: Truststore exist on both clusters. (Itempotency)
        ##################################################################################
        '''
        with set_module_args({
            'clustername': 'system1',
            'username': 'username',
            'password': 'password',
            'state': 'present',
            'primary_truststore_name': 'Truststore1',
            'remote_truststore_name': 'Truststore2',
            'remote_clustername': 'system2',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password'
        }):

            with (patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
                        'ibm_sv_manage_system_certificate.IBMSVManageSystemCert._execute_command'
                        ) as mock_execute_command,
                  pytest.raises(AnsibleExitJson) as exc):

                lstruststore_op_1 = {"name": "Truststore1", "id": "1"}
                lstruststore_op_2 = {"name": "Truststore2", "id": "1"}

                system_mock_info = [lstruststore_op_2, lstruststore_op_1]
                mock_execute_command.side_effect = system_mock_info

                v = IBMSVManageSystemCert()
                v.apply()

            self.assertFalse(exc.value.args[0]['changed'])
            self.assertEqual(exc.value.args[0]['msg'],
                             "Truststore {0} already exists on cluster {1}. "
                             "Truststore {2} already exists on cluster {3}. "
                             .format('Truststore2', 'system2', 'Truststore1', 'system1'))
            self.assertEqual(mock_execute_command.call_count, 2)
            mock_execute_command.reset_mock()

        '''
        ##################################################################################
        Case 3: Truststore exist on primary system but not on remote system.
        ##################################################################################
        '''
        with set_module_args({
            'clustername': 'system1',
            'username': 'username',
            'password': 'password',
            'state': 'present',
            'primary_truststore_name': 'Truststore1',
            'remote_truststore_name': 'Truststore2',
            'remote_clustername': 'system2',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password'
        }):

            with (patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
                        'ibm_sv_manage_system_certificate.IBMSVManageSystemCert._execute_command'
                        ) as mock_execute_command,
                  pytest.raises(AnsibleExitJson) as exc):

                lstruststore_op_1 = {"name": "Truststore1", "id": "1"}
                lstruststore_op_2 = None
                system_info_1 = {'id': '000002042E698S',
                                 'name': 'primary',
                                 'code_level': '9.1.0.0'}
                system_info_2 = {'id': '000002042E698R',
                                 'name': 'remote',
                                 'code_level': '9.1.0.0'}
                lssystemcertstore_op = {"id": "3",
                                        "scope": "internal_communication",
                                        "certificate_id": "0x687894bb",
                                        "type": "system_signed"}
                export_cert_op = None
                truststore_create_op = None

                system_mock_info = [lstruststore_op_2, system_info_1,
                                    system_info_2, lssystemcertstore_op,
                                    export_cert_op, truststore_create_op,
                                    lstruststore_op_1]

                mock_execute_command.side_effect = system_mock_info

                con_mock = Mock()
                svc_connect_mock.return_value = True
                ssh_mock.return_value = con_mock
                stdin = Mock()
                stdout = Mock()
                stderr = Mock()
                con_mock.exec_command.return_value = (stdin, stdout, stderr)
                stdout.channel.recv_exit_status.return_value = 0
                stdout.read.side_effect = [b'']

                v = IBMSVManageSystemCert()
                v.apply()

            self.assertTrue(exc.value.args[0]['changed'])
            self.assertEqual(exc.value.args[0]['msg'],
                             "Truststore {0} created successfully on cluster {1}. "
                             "Truststore {2} already exists on cluster {3}. "
                             .format('Truststore2', 'system2', 'Truststore1', 'system1'))
            self.assertEqual(mock_execute_command.call_count, 7)
            mock_execute_command.reset_mock()

        '''
        ##################################################################################
        Case 4: Create truststore on both clusters when it does not exist, but system are on older build.
        ##################################################################################
        '''
        with set_module_args({
            'clustername': 'system1',
            'username': 'username',
            'password': 'password',
            'state': 'present',
            'primary_truststore_name': 'Truststore1',
            'remote_truststore_name': 'Truststore2',
            'remote_clustername': 'system2',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password'
        }):
            with (patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
                        'ibm_sv_manage_system_certificate.IBMSVManageSystemCert._execute_command'
                        ) as mock_execute_command,
                  pytest.raises(AnsibleExitJson) as exc):

                lstruststore_op = None
                system_info_1 = {'id': '000002042E698S',
                                 'name': 'primary',
                                 'code_level': '8.7.0.0'}
                system_info_2 = {'id': '000002042E698R',
                                 'name': 'remote',
                                 'code_level': '8.7.3.0'}
                export_cert_op = None
                truststore_create_op = None

                system_mock_info = [lstruststore_op, system_info_1, system_info_2,
                                    export_cert_op, truststore_create_op,
                                    lstruststore_op, export_cert_op, truststore_create_op]

                mock_execute_command.side_effect = system_mock_info

                con_mock = Mock()
                svc_connect_mock.return_value = True
                ssh_mock.return_value = con_mock
                stdin = Mock()
                stdout = Mock()
                stderr = Mock()
                con_mock.exec_command.return_value = (stdin, stdout, stderr)
                stdout.channel.recv_exit_status.return_value = 0
                stdout.read.side_effect = [b'', b'']

                v = IBMSVManageSystemCert()
                v.apply()

            self.assertTrue(exc.value.args[0]['changed'])
            self.assertEqual(exc.value.args[0]['msg'],
                             "Truststore {0} created successfully on cluster {1}. "
                             "Truststore {2} created successfully on cluster {3}. "
                             .format('Truststore2', 'system2', 'Truststore1', 'system1'))
            self.assertEqual(mock_execute_command.call_count, 8)
            cmd_args_for_primary = mock_execute_command.call_args_list[3].args[0]
            cmd_args_for_remote = mock_execute_command.call_args_list[6].args[0]
            cmd_args_for_remote_1 = mock_execute_command.call_args_list[7].args[0]

            self.assertTrue('-export' in cmd_args_for_remote)
            self.assertTrue('-exportrootcacert' in cmd_args_for_primary)
            self.assertTrue('/tmp/certificate_system2.pem' in cmd_args_for_remote_1)
            mock_execute_command.reset_mock()

        '''
        ##################################################################################
        Case 5: Create truststore on both clusters when it does not exist, but system1 is older system2 is newer build.
        ##################################################################################
        '''
        with set_module_args({
            'clustername': 'system1',
            'username': 'username',
            'password': 'password',
            'state': 'present',
            'primary_truststore_name': 'Truststore1',
            'remote_truststore_name': 'Truststore2',
            'remote_clustername': 'system2',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password'
        }):
            with (patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
                        'ibm_sv_manage_system_certificate.IBMSVManageSystemCert._execute_command'
                        ) as mock_execute_command,
                  pytest.raises(AnsibleExitJson) as exc):

                lstruststore_op = None
                system_info_1 = {'id': '000002042E698S',
                                 'name': 'primary',
                                 'code_level': '8.7.0.0'}
                system_info_2 = {'id': '000002042E698R',
                                 'name': 'remote',
                                 'code_level': '9.1.0.0'}
                export_cert_op = None
                truststore_create_op = None

                lssystemcertstore_op = {"id": "3",
                                        "scope": "internal_communication",
                                        "certificate_id": "0x687894bb",
                                        "type": "system_signed"}

                system_mock_info = [lstruststore_op, system_info_1, system_info_2,
                                    export_cert_op, truststore_create_op,
                                    lstruststore_op, lssystemcertstore_op, export_cert_op,
                                    truststore_create_op]

                mock_execute_command.side_effect = system_mock_info

                con_mock = Mock()
                svc_connect_mock.return_value = True
                ssh_mock.return_value = con_mock
                stdin = Mock()
                stdout = Mock()
                stderr = Mock()
                con_mock.exec_command.return_value = (stdin, stdout, stderr)
                stdout.channel.recv_exit_status.return_value = 0
                stdout.read.side_effect = [b'', b'']

                v = IBMSVManageSystemCert()
                v.apply()

            self.assertTrue(exc.value.args[0]['changed'])
            self.assertEqual(exc.value.args[0]['msg'],
                             "Truststore {0} created successfully on cluster {1}. "
                             "Truststore {2} created successfully on cluster {3}. "
                             .format('Truststore2', 'system2', 'Truststore1', 'system1'))
            self.assertEqual(mock_execute_command.call_count, 9)

            cmd_args_for_remote = mock_execute_command.call_args_list[4].args[0]
            cmd_args_for_primary = mock_execute_command.call_args_list[8].args[0]

            self.assertTrue('-restapi' in cmd_args_for_remote)
            self.assertTrue('-restapi' in cmd_args_for_primary)
            self.assertTrue('/tmp/certificate_system1.pem' in cmd_args_for_remote)
            mock_execute_command.reset_mock()

    @patch('ansible_collections.ibm.storage_virtualize.plugins.'
           'module_utils.ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_remove_truststore(self,
                               svc_connect_mock):
        '''
        ##################################################################################
        Case 1: Remove truststore on both clusters when exist.
        ##################################################################################
        '''
        with set_module_args({
            'clustername': 'system1',
            'username': 'username',
            'password': 'password',
            'state': 'absent',
            'primary_truststore_name': 'Truststore1',
            'remote_truststore_name': 'Truststore2',
            'remote_clustername': 'system2',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password'
        }):

            with (patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
                        'ibm_sv_manage_system_certificate.IBMSVManageSystemCert._execute_command'
                        ) as mock_execute_command,
                  pytest.raises(AnsibleExitJson) as exc):

                lstruststore_op_1 = {"name": "Truststore1", "id": "1"}
                lstruststore_op_2 = {"name": "Truststore2", "id": "1"}
                removetruststore_op = None

                system_mock_info = [lstruststore_op_1, removetruststore_op,
                                    lstruststore_op_2, removetruststore_op]

                mock_execute_command.side_effect = system_mock_info

                v = IBMSVManageSystemCert()
                v.apply()

            self.assertTrue(exc.value.args[0]['changed'])
            self.assertEqual(exc.value.args[0]['msg'],
                             "Truststore {0} removed successfully from cluster {1}. "
                             "Truststore {2} removed successfully from cluster {3}. "
                             .format('Truststore1', 'system1', 'Truststore2', 'system2'))
            self.assertEqual(mock_execute_command.call_count, 4)
            mock_execute_command.reset_mock()

        '''
        ##################################################################################
        Case 2: Remove truststore on both clusters when does not exist. (Itempotency)
        ##################################################################################
        '''
        with set_module_args({
            'clustername': 'system1',
            'username': 'username',
            'password': 'password',
            'state': 'absent',
            'primary_truststore_name': 'Truststore1',
            'remote_truststore_name': 'Truststore2',
            'remote_clustername': 'system2',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password'
        }):

            with (patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
                        'ibm_sv_manage_system_certificate.IBMSVManageSystemCert._execute_command'
                        ) as mock_execute_command,
                  pytest.raises(AnsibleExitJson) as exc):

                lstruststore_op = {}

                system_mock_info = [lstruststore_op, lstruststore_op]

                mock_execute_command.side_effect = system_mock_info

                v = IBMSVManageSystemCert()
                v.apply()

            self.assertFalse(exc.value.args[0]['changed'])
            self.assertEqual(exc.value.args[0]['msg'],
                             "Truststore {0} does not exist, or already removed from cluster {1}. "
                             "Truststore {2} does not exist, or already removed from cluster {3}. "
                             .format('Truststore1', 'system1', 'Truststore2', 'system2'))
            self.assertEqual(mock_execute_command.call_count, 2)
            mock_execute_command.reset_mock()

        '''
        ##################################################################################
        Case 3: Remove truststore on both clusters when exist primary but not on remote.
        ##################################################################################
        '''
        with set_module_args({
            'clustername': 'system1',
            'username': 'username',
            'password': 'password',
            'state': 'absent',
            'primary_truststore_name': 'Truststore1',
            'remote_truststore_name': 'Truststore2',
            'remote_clustername': 'system2',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password'
        }):

            with (patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
                        'ibm_sv_manage_system_certificate.IBMSVManageSystemCert._execute_command'
                        ) as mock_execute_command,
                  pytest.raises(AnsibleExitJson) as exc):

                lstruststore_op_1 = {"name": "Truststore1", "id": "1"}
                lstruststore_op_2 = {}
                removetruststore_op = None

                system_mock_info = [lstruststore_op_1, removetruststore_op,
                                    lstruststore_op_2]

                mock_execute_command.side_effect = system_mock_info

                v = IBMSVManageSystemCert()
                v.apply()

            self.assertTrue(exc.value.args[0]['changed'])
            self.assertEqual(exc.value.args[0]['msg'],
                             "Truststore {0} removed successfully from cluster {1}. "
                             "Truststore {2} does not exist, or already removed from cluster {3}. "
                             .format('Truststore1', 'system1', 'Truststore2', 'system2'))
            self.assertEqual(mock_execute_command.call_count, 3)
            mock_execute_command.reset_mock()

        '''
        ##################################################################################
        Case 4: Remove truststore from single cluster when exist.
        ##################################################################################
        '''
        with set_module_args({
            'clustername': 'system1',
            'username': 'username',
            'password': 'password',
            'state': 'absent',
            'primary_truststore_name': 'Truststore1',
        }):

            with (patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
                        'ibm_sv_manage_system_certificate.IBMSVManageSystemCert._execute_command'
                        ) as mock_execute_command,
                  pytest.raises(AnsibleExitJson) as exc):

                lstruststore_op = {"name": "Truststore1", "id": "1"}
                removetruststore_op = None

                system_mock_info = [lstruststore_op, removetruststore_op]

                mock_execute_command.side_effect = system_mock_info

                v = IBMSVManageSystemCert()
                v.apply()

            self.assertTrue(exc.value.args[0]['changed'])
            self.assertEqual(exc.value.args[0]['msg'],
                             "Truststore {0} removed successfully from cluster {1}. "
                             .format('Truststore1', 'system1'))
            self.assertEqual(mock_execute_command.call_count, 2)
            mock_execute_command.reset_mock()

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_sv_manage_system_certificate.IBMSVManageSystemCert._exchange_certificate')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.'
           'module_utils.ibm_svc_ssh.IBMSVCssh._svc_connect')
    def test_build_check_8_7_3_and_older_build(self,
                                               svc_connect_mock,
                                               mock_exchange):
        '''
        ##################################################################################
        Case 1: Create truststore on both clusters with 8.7.3.x build where -flashgrid
        option is required for mktruststore command.
        ##################################################################################
        '''
        with set_module_args({
            'clustername': 'system1',
            'username': 'username',
            'password': 'password',
            'state': 'present',
            'primary_truststore_name': 'Truststore1',
            'remote_truststore_name': 'Truststore2',
            'remote_clustername': 'system2',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password'
        }):

            with (patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
                        'ibm_sv_manage_system_certificate.IBMSVManageSystemCert._execute_command'
                        ) as mock_execute_command,
                  pytest.raises(AnsibleExitJson) as exc):

                lstruststore_op = None
                system_info_1 = {'id': '000002042E698D',
                                 'name': 'primary',
                                 'code_level': '8.7.3.0'}
                system_info_2 = {'id': '000002042E698P',
                                 'name': 'remote',
                                 'code_level': '8.7.3.2'}
                export_cert_op = None
                truststore_create_op = None

                system_mock_info = [lstruststore_op, system_info_1, system_info_2,
                                    export_cert_op, truststore_create_op, lstruststore_op,
                                    export_cert_op, truststore_create_op]

                mock_execute_command.side_effect = system_mock_info

                v = IBMSVManageSystemCert()
                v.apply()

            cmd_args_for_remote = mock_execute_command.call_args_list[4].args[0]  # 4th call mktruststore for remote.
            cmd_args_for_primary = mock_execute_command.call_args_list[7].args[0]  # 8th call mktruststore for primary.
            self.assertEqual(mock_execute_command.call_count, 8)
            self.assertTrue('-flashgrid' in cmd_args_for_remote)
            self.assertTrue('-flashgrid' in cmd_args_for_primary)
            mock_execute_command.reset_mock()

        '''
        ##################################################################################
        Case 2: Create truststore on clusters with one is 8.7.3.x build and other is 8.7.2.x
        ##################################################################################
        '''
        with set_module_args({
            'clustername': 'system1',
            'username': 'username',
            'password': 'password',
            'state': 'present',
            'primary_truststore_name': 'Truststore1',
            'remote_truststore_name': 'Truststore2',
            'remote_clustername': 'system2',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password'
        }):

            with (patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
                        'ibm_sv_manage_system_certificate.IBMSVManageSystemCert._execute_command'
                        ) as mock_execute_command,
                  pytest.raises(AnsibleExitJson) as exc):

                lstruststore_op = None
                system_info_1 = {'id': '000002042E698S',
                                 'name': 'primary',
                                 'code_level': '8.7.3.0'}
                system_info_2 = {'id': '000002042E698R',
                                 'name': 'remote',
                                 'code_level': '8.7.2.0'}
                export_cert_op = None
                truststore_create_op = None

                system_mock_info = [lstruststore_op, system_info_1, system_info_2,
                                    export_cert_op, truststore_create_op, lstruststore_op,
                                    export_cert_op, truststore_create_op]

                mock_execute_command.side_effect = system_mock_info

                v = IBMSVManageSystemCert()
                v.apply()

            cmd_args_for_remote = mock_execute_command.call_args_list[4].args[0]
            cmd_args_for_primary = mock_execute_command.call_args_list[7].args[0]
            self.assertEqual(mock_execute_command.call_count, 8)

            self.assertTrue('-restapi' in cmd_args_for_remote)
            self.assertTrue('-flashgrid' in cmd_args_for_primary)
            mock_execute_command.reset_mock()
