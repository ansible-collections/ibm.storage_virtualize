# Copyright (C) 2022 IBM CORPORATION
# Author(s): Sanjaikumaar M <sanjaikumaar.m@ibm.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Storage Virtualize Ansible module: ibm_sv_manage_cloud_backups """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.storage_virtualize.plugins.modules.ibm_sv_manage_cloud_backups import IBMSVCloudBackup
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


class TestIBMSVCloudBackup(unittest.TestCase):
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

    def test_missing_state_parameter(self):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'volume_name': 'vol1'
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                IBMSVCloudBackup()
            self.assertTrue(exc.value.args[0]['failed'])

    def test_mutually_exclusive_parameters_1(self):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'volume_name': 'vol1',
            'volumegroup_name': 'VG1',
            'state': 'present'
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                IBMSVCloudBackup()
            self.assertTrue(exc.value.args[0]['failed'])

    def test_mutually_exclusive_parameters_2(self):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'volume_name': 'vol1',
            'volume_UID': '8320948320948',
            'state': 'absent'
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                IBMSVCloudBackup()
            self.assertTrue(exc.value.args[0]['failed'])

    def test_mutually_exclusive_parameters_3(self):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'volume_UID': '8320948320948',
            'all': True,
            'generation': 1,
            'state': 'absent'
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                IBMSVCloudBackup()
            self.assertTrue(exc.value.args[0]['failed'])

    def test_invalid_parameters_delete_1(self):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'volumegroup_name': 'VG1',
            'state': 'absent'
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                IBMSVCloudBackup()
            self.assertTrue(exc.value.args[0]['failed'])

    def test_invalid_parameters_delete_2(self):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'volume_name': 'vol1',
            'full': True,
            'state': 'absent'
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                IBMSVCloudBackup()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_with_invalid_create_parameters(self, svc_authorize_mock,
                                            svc_obj_info_mock,
                                            svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'volume_name': 'vol1',
            'volume_UID': '230984093284032984',
            'generation': 1,
            'state': 'present'
        }):
            svc_obj_info_mock.return_value = {'id': 1, 'name': 'vol1'}
            with pytest.raises(AnsibleFailJson) as exc:
                aws = IBMSVCloudBackup()
                aws.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_token_wrap')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_cloud_backup_volume(self, svc_authorize_mock,
                                        svc_obj_info_mock,
                                        svc_token_wrap_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'volume_name': 'vol1',
            'state': 'present'
        }):
            aws = IBMSVCloudBackup()
            svc_obj_info_mock.return_value = {'id': 1, 'name': 'vol1'}
            svc_token_wrap_mock.return_value = {'out': None}

            with pytest.raises(AnsibleExitJson) as exc:
                aws.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_token_wrap')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_cloud_backup_volume_idempotency(self, svc_authorize_mock,
                                                    svc_obj_info_mock,
                                                    svc_token_wrap_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'volume_name': 'vol1',
            'state': 'present'
        }):
            aws = IBMSVCloudBackup()
            svc_obj_info_mock.return_value = {'id': 1, 'name': 'vol1'}
            svc_token_wrap_mock.return_value = {'out': b'CMMVC9083E'}

            with pytest.raises(AnsibleExitJson) as exc:
                aws.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_token_wrap')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_cloud_backup_with_invalid_volume(self, svc_authorize_mock,
                                                     svc_obj_info_mock,
                                                     svc_token_wrap_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'volume_name': 'vol1',
            'state': 'present'
        }):
            aws = IBMSVCloudBackup()
            svc_obj_info_mock.return_value = {}

            with pytest.raises(AnsibleFailJson) as exc:
                aws.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_token_wrap')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_cloud_backup_volumegroup(self, svc_authorize_mock,
                                             svc_obj_info_mock,
                                             svc_token_wrap_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'volumegroup_name': 'VG1',
            'state': 'present'
        }):
            aws = IBMSVCloudBackup()
            svc_obj_info_mock.return_value = {'id': 1, 'name': 'VG1'}
            svc_token_wrap_mock.return_value = {'out': None}

            with pytest.raises(AnsibleExitJson) as exc:
                aws.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_token_wrap')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_cloud_backup_volumegroup_idempotency(self, svc_authorize_mock,
                                                         svc_obj_info_mock,
                                                         svc_token_wrap_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'volumegroup_name': 'VG1',
            'state': 'present'
        }):
            aws = IBMSVCloudBackup()
            svc_obj_info_mock.return_value = {'id': 1, 'name': 'VG1'}
            svc_token_wrap_mock.return_value = {'out': b'CMMVC9083E'}

            with pytest.raises(AnsibleExitJson) as exc:
                aws.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_token_wrap')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_cloud_backup_with_invalid_volumegroup(self, svc_authorize_mock,
                                                          svc_obj_info_mock,
                                                          svc_token_wrap_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'volumegroup_name': 'VG1',
            'state': 'present'
        }):
            aws = IBMSVCloudBackup()
            svc_obj_info_mock.return_value = {}

            with pytest.raises(AnsibleFailJson) as exc:
                aws.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_cloud_backup_with_volume_name(self, svc_authorize_mock,
                                                  svc_obj_info_mock,
                                                  svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'volume_name': 'vol1',
            'generation': 1,
            'state': 'absent'
        }):
            aws = IBMSVCloudBackup()
            svc_obj_info_mock.return_value = {'id': 1, 'name': 'vol1'}

            with pytest.raises(AnsibleExitJson) as exc:
                aws.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_cloud_backup_with_volume_name_idempotency(self, svc_authorize_mock,
                                                              svc_obj_info_mock,
                                                              svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'volume_name': 'vol1',
            'generation': 1,
            'state': 'absent'
        }):
            aws = IBMSVCloudBackup()
            svc_obj_info_mock.return_value = {}

            with pytest.raises(AnsibleExitJson) as exc:
                aws.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_cloud_backup_with_uid(self, svc_authorize_mock,
                                          svc_obj_info_mock,
                                          svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'volume_UID': '3280948320948',
            'all': True,
            'state': 'absent'
        }):
            aws = IBMSVCloudBackup()
            svc_obj_info_mock.return_value = {'id': 1, 'name': 'vol1'}

            with pytest.raises(AnsibleExitJson) as exc:
                aws.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_cloud_backup_with_uid_idempotency(self, svc_authorize_mock,
                                                      svc_obj_info_mock,
                                                      svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'volume_UID': '3280948320948',
            'all': True,
            'state': 'absent'
        }):
            aws = IBMSVCloudBackup()
            svc_obj_info_mock.return_value = {}

            with pytest.raises(AnsibleExitJson) as exc:
                aws.apply()
            self.assertFalse(exc.value.args[0]['changed'])


if __name__ == '__main__':
    unittest.main()
