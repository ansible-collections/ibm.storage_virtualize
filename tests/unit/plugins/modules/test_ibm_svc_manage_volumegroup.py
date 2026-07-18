# Copyright (C) 2020 IBM CORPORATION
# Author(s): Sandip Gulab Rajbanshi <sandip.rajbanshi@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Storage Virtualize Ansible module: ibm_svc_manage_volumegroup """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.storage_virtualize.plugins.modules.ibm_svc_manage_volumegroup import IBMSVCVG
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


class TestIBMSVCvdisk(unittest.TestCase):
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

    def test_module_fail_when_required_args_missing(self):
        """ required arguments are reported as errors """
        with set_module_args({}):
            with pytest.raises(AnsibleFailJson) as exc:
                IBMSVCVG()
            print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_vg(self, mock_svc_authorize, svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
        }):
            svc_obj_info_mock.return_value = {
                "id": "8",
                "name": "test_volumegroup",
                "volume_count": "0",
                "backup_status": "empty",
                "last_backup_time": "",
                "owner_id": "",
                "owner_name": "",
                "safeguarded_policy_id": "",
                "safeguarded_policy_name": "",
                "safeguarded_policy_start_time": "",
                "snapshot_policy_name": "",
                "snapshot_policy_suspended": "no",
                "ignore_user_flash_copy_maps": "no",
                "snapshot_policy_safeguarded": "no"
            }
            vg = IBMSVCVG()
            vg.get_existing_vg("test_volumegroup")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_probe_adding_ownershipgroup(self, mock_svc_authorize):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'ownershipgroup': 'test_ownershipgroup_new',
        }):
            data = {
                "id": "8",
                "name": "test_volumegroup",
                "volume_count": "0",
                "backup_status": "empty",
                "last_backup_time": "",
                "owner_id": "",
                "owner_name": "",
                "safeguarded_policy_id": "",
                "safeguarded_policy_name": "",
                "safeguarded_policy_start_time": "",
                "snapshot_policy_name": "",
                "snapshot_policy_suspended": "no",
                "ignore_user_flash_copy_maps": "no",
                "snapshot_policy_safeguarded": "no"
            }
            vg = IBMSVCVG()
            probe_data = vg.vg_probe(data)
            self.assertTrue('ownershipgroup' in probe_data)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_probe_updating_ownershipgroup(self, mock_svc_authorize):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'ownershipgroup': 'test_ownershipgroup_new',
        }):
            data = {
                "id": "8",
                "name": "test_volumegroup",
                "volume_count": "0",
                "backup_status": "empty",
                "last_backup_time": "",
                "owner_id": "",
                "owner_name": "test_ownershipgroup_old",
                "safeguarded_policy_id": "",
                "safeguarded_policy_name": "",
                "safeguarded_policy_start_time": "",
                "snapshot_policy_name": "",
                "snapshot_policy_suspended": "no",
                "ignore_user_flash_copy_maps": "no",
                "snapshot_policy_safeguarded": "no"
            }
            vg = IBMSVCVG()
            probe_data = vg.vg_probe(data)
            self.assertTrue('ownershipgroup' in probe_data)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_probe_with_noownershipgroup(self, mock_svc_authorize):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'noownershipgroup': True
        }):
            data = {
                "id": "8",
                "name": "test_volumegroup",
                "volume_count": "0",
                "backup_status": "empty",
                "last_backup_time": "",
                "owner_id": "",
                "owner_name": "test_ownershipgroup",
                "safeguarded_policy_id": "",
                "safeguarded_policy_name": "",
                "safeguarded_policy_start_time": "",
                "snapshot_policy_name": "",
                "snapshot_policy_suspended": "no",
                "ignore_user_flash_copy_maps": "no",
                "snapshot_policy_safeguarded": "no"
            }
            vg = IBMSVCVG()
            probe_data = vg.vg_probe(data)
            self.assertTrue('noownershipgroup' in probe_data)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_probe_add_safeguardpolicyname(self, mock_svc_authorize):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'safeguardpolicyname': 'policy_name'
        }):
            data = {
                "id": "8",
                "name": "test_volumegroup",
                "volume_count": "0",
                "backup_status": "empty",
                "last_backup_time": "",
                "owner_id": "",
                "owner_name": "test_ownershipgroup",
                "safeguarded_policy_id": "",
                "safeguarded_policy_name": "",
                "safeguarded_policy_start_time": "",
                "snapshot_policy_name": "",
                "snapshot_policy_suspended": "no",
                "ignore_user_flash_copy_maps": "no",
                "snapshot_policy_safeguarded": "no"
            }
            vg = IBMSVCVG()
            probe_data = vg.vg_probe(data)
            self.assertTrue('safeguardedpolicy' in probe_data)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_probe_update_safeguardpolicyname(self, mock_svc_authorize):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'safeguardpolicyname': 'new_policy_name'
        }):
            data = {
                "id": "8",
                "name": "test_volumegroup",
                "volume_count": "0",
                "backup_status": "empty",
                "last_backup_time": "",
                "owner_id": "",
                "owner_name": "test_ownershipgroup",
                "safeguarded_policy_id": "",
                "safeguarded_policy_name": "old_policy_name",
                "safeguarded_policy_start_time": "",
                "snapshot_policy_name": "",
                "snapshot_policy_suspended": "no",
                "ignore_user_flash_copy_maps": "no",
                "snapshot_policy_safeguarded": "no"
            }
            vg = IBMSVCVG()
            probe_data = vg.vg_probe(data)
            self.assertTrue('safeguardedpolicy' in probe_data)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_for_mutual_exclusive_parameter_1(self, mock_svc_authorize):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'ownershipgroup': 'test_ownershipgroup',
            'noownershipgroup': True
        }):
            data = {
                "id": "8",
                "name": "test_volumegroup",
                "volume_count": "0",
                "backup_status": "empty",
                "last_backup_time": "",
                "owner_id": "",
                "owner_name": "",
                "safeguarded_policy_id": "",
                "safeguarded_policy_name": "",
                "safeguarded_policy_start_time": "",
                "snapshot_policy_name": "",
                "snapshot_policy_suspended": "no",
                "ignore_user_flash_copy_maps": "no",
                "snapshot_policy_safeguarded": "no"
            }
            vg = IBMSVCVG()
            with pytest.raises(AnsibleFailJson) as exc:
                vg.vg_probe(data)
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_for_mutual_exclusive_parameter_2(self, mock_svc_authorize):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'safeguardpolicyname': 'policy_name',
            'nosafeguardpolicy': True
        }):
            data = {
                "id": "8",
                "name": "test_volumegroup",
                "volume_count": "0",
                "backup_status": "empty",
                "last_backup_time": "",
                "owner_id": "",
                "owner_name": "",
                "safeguarded_policy_id": "",
                "safeguarded_policy_name": "",
                "safeguarded_policy_start_time": "",
                "snapshot_policy_name": "",
                "snapshot_policy_suspended": "no",
                "ignore_user_flash_copy_maps": "no",
                "snapshot_policy_safeguarded": "no"
            }
            vg = IBMSVCVG()
            with pytest.raises(AnsibleFailJson) as exc:
                vg.vg_probe(data)
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_for_mutual_exclusive_parameter_3(self, mock_svc_authorize):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'ownershipgroup': 'test_ownershipgroup',
            'safeguardpolicyname': 'policy_name'
        }):
            data = {
                "id": "8",
                "name": "test_volumegroup",
                "volume_count": "0",
                "backup_status": "empty",
                "last_backup_time": "",
                "owner_id": "",
                "owner_name": "",
                "safeguarded_policy_id": "",
                "safeguarded_policy_name": "",
                "safeguarded_policy_start_time": "",
                "snapshot_policy_name": "",
                "snapshot_policy_suspended": "no",
                "ignore_user_flash_copy_maps": "no",
                "snapshot_policy_safeguarded": "no"
            }
            vg = IBMSVCVG()
            with pytest.raises(AnsibleFailJson) as exc:
                vg.vg_probe(data)
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_create(self, mock_svc_authorize, svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'ownershipgroup': 'test_ownershipgroup',
        }):
            svc_run_command_mock.return_value = {
                'id': '56',
                'message': 'success'
            }
            vg = IBMSVCVG()
            probe_data = vg.vg_create()

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_update_with_noownershipgroup_nosafeguardpolicy(self,
                                                               mock_svc_authorize,
                                                               svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'noownershipgroup': True,
            'nosafeguardpolicy': True
        }):
            probe_data = {
                'noownershipgroup': True,
                'nosafeguardpolicy': True
            }
            svc_run_command_mock.return_value = None
            vg = IBMSVCVG()
            probe_data = vg.vg_update(probe_data)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_update_with_ownershipgroup_nosafeguardpolicy(self,
                                                             mock_svc_authorize,
                                                             svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'ownershipgroup': 'group_name',
            'nosafeguardpolicy': True
        }):
            probe_data = {
                'ownershipgroup': 'group_name',
                'nosafeguardpolicy': True
            }
            svc_run_command_mock.return_value = None
            vg = IBMSVCVG()
            probe_data = vg.vg_update(probe_data)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_update_with_safeguardpolicyname(self, mock_svc_authorize,
                                                svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'safeguardpolicyname': 'policy_name'
        }):
            probe_data = {
                'safeguardedpolicy': 'policy_name'
            }
            svc_run_command_mock.return_value = None
            vg = IBMSVCVG()
            probe_data = vg.vg_update(probe_data)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_update_with_policystarttime(self, mock_svc_authorize,
                                            svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'safeguardpolicyname': 'policy_name',
            'policystarttime': 'YYMMDDHHMM'
        }):
            probe_data = {
                'safeguardedpolicy': 'policy_name',
                'policystarttime': 'YYMMDDHHMM'
            }
            svc_run_command_mock.return_value = None
            vg = IBMSVCVG()
            probe_data = vg.vg_update(probe_data)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_update_with_only_noownershipgroup(self, mock_svc_authorize,
                                                  svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'noownershipgroup': True,
        }):
            probe_data = {
                'noownershipgroup': True
            }
            svc_run_command_mock.return_value = None
            vg = IBMSVCVG()
            probe_data = vg.vg_update(probe_data)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_update_with_only_nosafeguardpolicy(self, mock_svc_authorize,
                                                   svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'nosafeguardpolicy': True,
        }):
            probe_data = {
                'nosafeguardpolicy': True,
            }
            svc_run_command_mock.return_value = None
            vg = IBMSVCVG()
            probe_data = vg.vg_update(probe_data)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_delete(self, mock_svc_authorize, svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'state': 'absent',
        }):
            svc_run_command_mock.return_value = None
            vg = IBMSVCVG()
            vg.vg_delete()

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_vg_delete_with_invalid_params(self, mock_svc_authorize):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'type': 'thinclone',
            'pool': 'pool0',
            'state': 'absent'
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                vg = IBMSVCVG()
                vg.vg_delete()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vg_delete_evictvolumes(self, mock_svc_authorize, svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'state': 'absent',
            'evictvolumes': True
        }):
            svc_run_command_mock.return_value = None
            vg = IBMSVCVG()
            vg.vg_delete()

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_module_for_creation_of_new_volumegroup(self, mock_svc_authorize,
                                                    svc_obj_info_mock,
                                                    svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'state': 'present',
            'ownershipgroup': 'ownershipgroup_name'
        }):
            svc_obj_info_mock.return_value = []
            svc_run_command_mock.return_value = {
                'id': 56,
                'message': 'success message'
            }
            with pytest.raises(AnsibleExitJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_module_for_creation_when_volumegroup_aleady_existing(
            self,
            mock_svc_authorize,
            svc_obj_info_mock,
            svc_run_command_mock
    ):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'state': 'present',
        }):
            svc_obj_info_mock.return_value = {
                "id": "8",
                "name": "test_volumegroup",
                "volume_count": "0",
                "backup_status": "empty",
                "last_backup_time": "",
                "owner_id": "",
                "owner_name": "",
                "safeguarded_policy_id": "",
                "safeguarded_policy_name": "",
                "safeguarded_policy_start_time": "",
                "snapshot_policy_name": "",
                "snapshot_policy_suspended": "no",
                "ignore_user_flash_copy_maps": "no",
                "snapshot_policy_safeguarded": "no"
            }
            with pytest.raises(AnsibleExitJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_module_while_updating_ownersipgroup(self, mock_svc_authorize,
                                                 soim, srcm):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'state': 'present',
            'ownershipgroup': 'new_name'
        }):
            soim.return_value = {
                "id": "8",
                "name": "test_volumegroup",
                "volume_count": "0",
                "backup_status": "empty",
                "last_backup_time": "",
                "owner_id": "",
                "owner_name": "old_name",
                "safeguarded_policy_id": "",
                "safeguarded_policy_name": "",
                "safeguarded_policy_start_time": "",
                "snapshot_policy_name": "",
                "snapshot_policy_suspended": "no",
                "ignore_user_flash_copy_maps": "no",
                "snapshot_policy_safeguarded": "no"
            }
            srcm.return_value = None
            with pytest.raises(AnsibleExitJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_module_for_deleting_an_existing_volumegroup(self, mock_svc_authorize,
                                                         svc_obj_info_mock,
                                                         svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'state': 'absent',
        }):
            svc_obj_info_mock.return_value = {
                "id": "8",
                "name": "test_volumegroup",
                "volume_count": "0",
                "backup_status": "empty",
                "last_backup_time": "",
                "owner_id": "",
                "owner_name": "",
                "safeguarded_policy_id": "",
                "safeguarded_policy_name": "",
                "safeguarded_policy_start_time": "",
                "snapshot_policy_name": "",
                "snapshot_policy_suspended": "no",
                "ignore_user_flash_copy_maps": "no",
                "snapshot_policy_safeguarded": "no"
            }
            with pytest.raises(AnsibleExitJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_module_for_deleting_nonexisting_volumegroup(self, mock_svc_authorize,
                                                         svc_obj_info_mock,
                                                         svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'state': 'absent',
        }):
            svc_obj_info_mock.return_value = {}
            with pytest.raises(AnsibleExitJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_volumegroup_with_snapshotpolicy(self, mock_svc_authorize,
                                                    svc_obj_info_mock,
                                                    svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'snapshotpolicy': 'ss_policy1',
            'replicationpolicy': 'rp0',
            'state': 'present',
        }):
            svc_obj_info_mock.return_value = {}
            with pytest.raises(AnsibleExitJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_volumegroup_with_snapshotpolicy_idempotency(self, mock_svc_authorize,
                                                                svc_obj_info_mock,
                                                                svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'snapshotpolicy': 'ss_policy1',
            'replicationpolicy': 'rp0',
            'state': 'present',
        }):
            svc_obj_info_mock.return_value = {
                "id": "8",
                "name": "test_volumegroup",
                "volume_count": "0",
                "backup_status": "empty",
                "last_backup_time": "",
                "owner_id": "",
                "owner_name": "",
                "safeguarded_policy_id": "",
                "safeguarded_policy_name": "",
                "safeguarded_policy_start_time": "",
                "snapshot_policy_name": "ss_policy1",
                "snapshot_policy_suspended": "no",
                "ignore_user_flash_copy_maps": "no",
                "snapshot_policy_safeguarded": "no",
                "replication_policy_name": "rp0"
            }
            with pytest.raises(AnsibleExitJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_volumegroup_with_safeguarded_snapshotpolicy(self,
                                                                mock_svc_authorize,
                                                                svc_obj_info_mock,
                                                                svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'snapshotpolicy': 'ss_policy1',
            'safeguarded': True,
            'ignoreuserfcmaps': 'yes',
            'state': 'present',
        }):
            svc_obj_info_mock.return_value = {}
            with pytest.raises(AnsibleExitJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_snapshot_policy(self, mock_svc_authorize,
                                    svc_obj_info_mock,
                                    svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'snapshotpolicy': 'ss_policy2',
            'replicationpolicy': 'rp0',
            'state': 'present',
        }):
            data = {
                "id": "8",
                "name": "test_volumegroup",
                "volume_count": "0",
                "backup_status": "empty",
                "last_backup_time": "",
                "owner_id": "",
                "owner_name": "",
                "safeguarded_policy_id": "",
                "safeguarded_policy_name": "",
                "safeguarded_policy_start_time": "",
                "snapshot_policy_name": "ss_policy1",
                "snapshot_policy_suspended": "no",
                "ignore_user_flash_copy_maps": "no",
                "snapshot_policy_safeguarded": "no",
                "replication_policy_name": ""
            }

            vg = IBMSVCVG()
            probe_data = vg.vg_probe(data)
            self.assertTrue('snapshotpolicy' in probe_data)
            self.assertTrue('replicationpolicy' in probe_data)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_safeguarded_snapshot_policy(self, mock_svc_authorize,
                                                svc_obj_info_mock,
                                                svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'snapshotpolicy': 'ss_policy2',
            'safeguarded': True,
            'ignoreuserfcmaps': 'yes',
            'state': 'present',
        }):
            data = {
                "id": "8",
                "name": "test_volumegroup",
                "volume_count": "0",
                "backup_status": "empty",
                "last_backup_time": "",
                "owner_id": "",
                "owner_name": "",
                "safeguarded_policy_id": "",
                "safeguarded_policy_name": "",
                "safeguarded_policy_start_time": "",
                "snapshot_policy_name": "ss_policy1",
                "snapshot_policy_suspended": "no",
                "ignore_user_flash_copy_maps": "no",
                "snapshot_policy_safeguarded": "no"
            }

            vg = IBMSVCVG()
            probe_data = vg.vg_probe(data)
            self.assertTrue('safeguarded' in probe_data)
            self.assertTrue('snapshotpolicy' in probe_data)
            self.assertTrue('ignoreuserfcmaps' in probe_data)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_unmap_snapshot_policy(self, mock_svc_authorize,
                                          svc_obj_info_mock,
                                          svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'nosnapshotpolicy': True,
            'noreplicationpolicy': True,
            'state': 'present',
        }):
            data = {
                "id": "8",
                "name": "test_volumegroup",
                "volume_count": "0",
                "backup_status": "empty",
                "last_backup_time": "",
                "owner_id": "",
                "owner_name": "",
                "safeguarded_policy_id": "",
                "safeguarded_policy_name": "",
                "safeguarded_policy_start_time": "",
                "snapshot_policy_name": "ss_policy2",
                "snapshot_policy_suspended": "no",
                "ignore_user_flash_copy_maps": "no",
                "snapshot_policy_safeguarded": "no",
                "replication_policy_name": "rp0"
            }

            vg = IBMSVCVG()
            probe_data = vg.vg_probe(data)
            self.assertTrue('nosnapshotpolicy' in probe_data)
            self.assertTrue('noreplicationpolicy' in probe_data)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_suspend_snapshot_policy_in_volumegroup(self, mock_svc_authorize,
                                                    svc_obj_info_mock,
                                                    svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'snapshotpolicysuspended': 'yes',
            'state': 'present',
        }):
            data = {
                "id": "8",
                "name": "test_volumegroup",
                "volume_count": "0",
                "backup_status": "empty",
                "last_backup_time": "",
                "owner_id": "",
                "owner_name": "",
                "safeguarded_policy_id": "",
                "safeguarded_policy_name": "",
                "safeguarded_policy_start_time": "",
                "snapshot_policy_name": "ss_policy2",
                "snapshot_policy_suspended": "no",
                "ignore_user_flash_copy_maps": "no",
                "snapshot_policy_safeguarded": "no"
            }

            vg = IBMSVCVG()
            probe_data = vg.vg_probe(data)
            self.assertTrue('snapshotpolicysuspended' in probe_data)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_volumegroup_from_VG_snapshot(self, mock_svc_authorize,
                                                 svc_obj_info_mock,
                                                 svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'type': 'thinclone',
            'snapshot': 'snapshot1',
            'fromsourcegroup': 'volgrp1',
            'state': 'present',
        }):
            svc_obj_info_mock.return_value = {}
            with pytest.raises(AnsibleExitJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.set_parentuid')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_volumegroup_from_orphan_snapshot(self, mock_svc_authorize,
                                                     svc_obj_info_mock,
                                                     set_parentuid_mock,
                                                     svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'type': 'thinclone',
            'snapshot': 'snapshot1',
            'state': 'present',
        }):
            svc_obj_info_mock.return_value = {}
            vg = IBMSVCVG()
            vg.parentuid = 5
            with pytest.raises(AnsibleExitJson) as exc:
                vg.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_update_storage_partition(self, mock_svc_authorize,
                                              svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'partition': 'partition1',
            'state': 'present'
        }):
            data = {
                "id": "8",
                "name": "test_volumegroup",
                "volume_count": "0",
                "backup_status": "empty",
                "last_backup_time": "",
                "owner_id": "",
                "owner_name": "",
                "safeguarded_policy_id": "",
                "safeguarded_policy_name": "",
                "safeguarded_policy_start_time": "",
                "snapshot_policy_name": "",
                "snapshot_policy_suspended": "no",
                "ignore_user_flash_copy_maps": "no",
                "snapshot_policy_safeguarded": "no",
                "partition_name": ""
            }
            svc_obj_info_mock.return_value = data
            with pytest.raises(AnsibleFailJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'], 'Following parameters not supported during update: partition')

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.create_transient_snapshot')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.set_parentuid')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.get_existing_vg')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_vg_thinclone_from_source_volumes(self, svc_authorize_mock,
                                                     svc_run_cmd_mock,
                                                     svc_get_existing_vg_mock,
                                                     svc_parentuid_mock,
                                                     create_transient_snapshot_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'vg_thinclone2',
            'state': 'present',
            'fromsourcevolumes': 'v1:d1',
            'type': 'thinclone',
            'pool': 'pool0'
        }):
            svc_get_existing_vg_mock.return_value = {}
            create_transient_snapshot_mock.return_value = 'snapshot_3335105753'

            with pytest.raises(AnsibleExitJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.get_existing_vg')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_vg_thinclone_from_source_volumes_idempotency(self, svc_authorize_mock,
                                                                 svc_get_existing_vg_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'v1d1thclone',
            'state': 'present',
            'fromsourcevolumes': 'v1:d1',
            'type': 'thinclone',
            'pool': 'pool0'
        }):
            svc_get_existing_vg_mock.return_value = {
                'id': '0',
                'name': 'v1d1thclone',
                'volume_count': '2',
                'backup_status': 'off',
                'last_backup_time': '',
                'owner_id': '',
                'owner_name': '',
                'safeguarded_policy_id': '',
                'safeguarded_policy_name': '',
                'safeguarded_policy_start_time': '',
                'replication_policy_id': '',
                'replication_policy_name': '',
                'volume_group_type': 'thinclone',
                'uid': '77',
                'source_volume_group_id': '',
                'source_volume_group_name': '',
                'parent_uid': '76',
                'source_snapshot_id': '0',
                'source_snapshot': 'snapshot_3335105753',
                'snapshot_count': '0',
                'protection_provisioned_capacity': '0.00MB',
                'protection_written_capacity': '0.00MB',
                'snapshot_policy_id': '',
                'snapshot_policy_name': '',
                'safeguarded_snapshot_count': '0',
                'ignore_user_flash_copy_maps': 'no',
                'partition_id': '',
                'partition_name': '',
                'restore_in_progress': 'no',
                'owner_type': 'none',
                'draft_partition_id': '',
                'draft_partition_name': '',
                'last_restore_time': '',
                'source_volumes_set': {'v1', 'd1'},
                'source_volumes_pool_set': {'pool0'}
            }

            with pytest.raises(AnsibleExitJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    # Test when existing clone/thinclone with same name but different source volumes
    # and user tries to create a normal volumegroup, it should fail
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.get_existing_vg')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_normal_vg_with_existing_thinclone_vg_name(self, svc_authorize_mock,
                                                              svc_get_existing_vg_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'v1d1thclone',
            'state': 'present',
            'pool': 'pool0'
        }):
            svc_get_existing_vg_mock.return_value = {
                'id': '0',
                'name': 'v1d1thclone',
                'volume_count': '2',
                'backup_status': 'off',
                'last_backup_time': '',
                'owner_id': '',
                'owner_name': '',
                'safeguarded_policy_id': '',
                'safeguarded_policy_name': '',
                'safeguarded_policy_start_time': '',
                'replication_policy_id': '',
                'replication_policy_name': '',
                'volume_group_type': 'thinclone',
                'uid': '77',
                'source_volume_group_id': '',
                'source_volume_group_name': '',
                'parent_uid': '76',
                'source_snapshot_id': '0',
                'source_snapshot': 'snapshot_3335105753',
                'snapshot_count': '0',
                'protection_provisioned_capacity': '0.00MB',
                'protection_written_capacity': '0.00MB',
                'snapshot_policy_id': '',
                'snapshot_policy_name': '',
                'safeguarded_snapshot_count': '0',
                'ignore_user_flash_copy_maps': 'no',
                'partition_id': '',
                'partition_name': '',
                'restore_in_progress': 'no',
                'owner_type': 'none',
                'draft_partition_id': '',
                'draft_partition_name': '',
                'last_restore_time': '',
                'source_volumes_set': {'v1', 'd1'},
                'source_volumes_pool_set': {'pool0'}
            }

            with pytest.raises(AnsibleFailJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertFalse(exc.value.args[0]['changed'])
            self.assertEqual(exc.value.args[0]['msg'], 'Existing thinclone volumegroup found.')

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.get_existing_vg')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_modify_vg_source_volumes(self,
                                             svc_authorize_mock,
                                             svc_get_existing_vg_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'v1d1thclone',
            'state': 'present',
            'fromsourcevolumes': 'v3:d1',
            'pool': 'pool0'
        }):
            svc_get_existing_vg_mock.return_value = {
                'id': '0',
                'name': 'v1d1thclone',
                'volume_count': '2',
                'backup_status': 'off',
                'last_backup_time': '',
                'owner_id': '',
                'owner_name': '',
                'safeguarded_policy_id': '',
                'safeguarded_policy_name': '',
                'safeguarded_policy_start_time': '',
                'replication_policy_id': '',
                'replication_policy_name': '',
                'volume_group_type': 'thinclone',
                'uid': '77',
                'source_volume_group_id': '',
                'source_volume_group_name': '',
                'parent_uid': '76',
                'source_snapshot_id': '0',
                'source_snapshot': 'snapshot_3335105753',
                'snapshot_count': '0',
                'protection_provisioned_capacity': '0.00MB',
                'protection_written_capacity': '0.00MB',
                'snapshot_policy_id': '',
                'snapshot_policy_name': '',
                'safeguarded_snapshot_count': '0',
                'ignore_user_flash_copy_maps': 'no',
                'partition_id': '',
                'partition_name': '',
                'restore_in_progress': 'no',
                'owner_type': 'none',
                'draft_partition_id': '',
                'draft_partition_name': '',
                'last_restore_time': '',
                'source_volumes_set': {'v1', 'd1'},
                'source_volumes_pool_set': {'pool0'}
            }

            with pytest.raises(AnsibleFailJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertFalse(exc.value.args[0]['changed'])
            self.assertEqual(exc.value.args[0]['msg'], 'Parameter [fromsourcevolumes] is invalid for modifying volumegroup.')

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_update_thinclone_vg_pool(self,
                                              svc_authorize_mock,
                                              svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'v1d1thclone',
            'state': 'present',
            'fromsourcevolumes': 'v1:d1',
            'type': 'thinclone',
            'pool': 'pool1'
        }):
            vg_info = {
                'id': '0',
                'name': 'v1d1thclone',
                'volume_count': '2',
                'backup_status': 'off',
                'last_backup_time': '',
                'owner_id': '',
                'owner_name': '',
                'safeguarded_policy_id': '',
                'safeguarded_policy_name': '',
                'safeguarded_policy_start_time': '',
                'replication_policy_id': '',
                'replication_policy_name': '',
                'volume_group_type': 'thinclone',
                'uid': '77',
                'source_volume_group_id': '',
                'source_volume_group_name': '',
                'parent_uid': '76',
                'source_snapshot_id': '0',
                'source_snapshot': 'snapshot_3335105753',
                'snapshot_count': '0',
                'protection_provisioned_capacity': '0.00MB',
                'protection_written_capacity': '0.00MB',
                'snapshot_policy_id': '',
                'snapshot_policy_name': '',
                'safeguarded_snapshot_count': '0',
                'ignore_user_flash_copy_maps': 'no',
                'partition_id': '',
                'partition_name': '',
                'restore_in_progress': 'no',
                'owner_type': 'none',
                'draft_partition_id': '',
                'draft_partition_name': '',
                'last_restore_time': ''
            }

            lsvolumepopulation_info = [
                {
                    "id": "0", "name": "V1", "IO_group_id": "0", "IO_group_name": "io_grp0", "status": "online",
                    "mdisk_grp_id": "2", "mdisk_grp_name": "pool0", "parent_mdisk_grp_name": "pool0",
                    "type": "thinclone", "source_volume_name": "v1"
                },
                {
                    "id": "2", "name": "D1", "IO_group_id": "0", "IO_group_name": "io_grp0", "status": "online",
                    "mdisk_grp_id": "1", "mdisk_grp_name": "pool1", "parent_mdisk_grp_name": "pool1",
                    "type": "thinclone", "source_volume_name": "d1"
                }
            ]

            vol_inside_pool_info = [
                {"id": "2", "name": "d1"}
            ]

            svc_obj_info_mock.side_effect = [vg_info, lsvolumepopulation_info, vol_inside_pool_info]

            with pytest.raises(AnsibleFailJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'], 'Provided pool [pool1] does not match the pool of one or more source volumes.')

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_transient_snapshot(self,
                                       svc_authorize_mock,
                                       svc_run_cmd_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'vg_thinclone2',
            'state': 'present',
            'fromsourcevolumes': 'v1:d1',
            'type': 'thinclone',
            'pool': 'pool0'
        }):
            vg = IBMSVCVG()
            snapshot_name = vg.create_transient_snapshot()
            self.assertTrue('snapshot_' in snapshot_name)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.create_transient_snapshot')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.set_parentuid')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.get_existing_vg')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_vg_clone_from_source_volumes(self,
                                                 svc_authorize_mock,
                                                 svc_run_cmd_mock,
                                                 svc_get_existing_vg_mock,
                                                 svc_parentuid_mock,
                                                 create_transient_snapshot_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'vg_clone',
            'state': 'present',
            'fromsourcevolumes': 'v1:d1',
            'type': 'clone',
            'pool': 'pool0'
        }):
            svc_get_existing_vg_mock.return_value = {}
            create_transient_snapshot_mock.return_value = 'snapshot_3335105753'

            with pytest.raises(AnsibleExitJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.get_existing_vg')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_vg_clone_from_source_volumes_idempotency(self,
                                                             svc_authorize_mock,
                                                             svc_get_existing_vg_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'v1d1clone',
            'state': 'present',
            'fromsourcevolumes': 'v1:d1',
            'type': 'clone',
            'pool': 'pool0'
        }):
            svc_get_existing_vg_mock.return_value = {
                'id': '0',
                'name': 'v1d1clone',
                'volume_count': '2',
                'backup_status': 'off',
                'last_backup_time': '',
                'owner_id': '',
                'owner_name': '',
                'safeguarded_policy_id': '',
                'safeguarded_policy_name': '',
                'safeguarded_policy_start_time': '',
                'replication_policy_id': '',
                'replication_policy_name': '',
                'volume_group_type': '',
                'uid': '77',
                'source_volume_group_id': '',
                'source_volume_group_name': '',
                'parent_uid': '76',
                'source_snapshot_id': '0',
                'source_snapshot': 'snapshot_3335105753',
                'snapshot_count': '0',
                'protection_provisioned_capacity': '0.00MB',
                'protection_written_capacity': '0.00MB',
                'snapshot_policy_id': '',
                'snapshot_policy_name': '',
                'safeguarded_snapshot_count': '0',
                'ignore_user_flash_copy_maps': 'no',
                'partition_id': '',
                'partition_name': '',
                'restore_in_progress': 'no',
                'owner_type': 'none',
                'draft_partition_id': '',
                'draft_partition_name': '',
                'last_restore_time': '',
                'source_volumes_set': {'v1', 'd1'},
                'source_volumes_pool_set': {'pool0'}
            }

            with pytest.raises(AnsibleExitJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    # Test create clone with different source volumes but a cloned VG already exists
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.get_existing_vg')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_modify_vg_source_volumes(self,
                                             svc_authorize_mock,
                                             svc_get_existing_vg_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'v1d1clone',
            'state': 'present',
            'type': 'clone',
            'fromsourcevolumes': 'v3:d1',
            'pool': 'pool0'
        }):
            svc_get_existing_vg_mock.return_value = {
                'id': '0',
                'name': 'v1d1clone',
                'volume_count': '2',
                'backup_status': 'off',
                'last_backup_time': '',
                'owner_id': '',
                'owner_name': '',
                'safeguarded_policy_id': '',
                'safeguarded_policy_name': '',
                'safeguarded_policy_start_time': '',
                'replication_policy_id': '',
                'replication_policy_name': '',
                'volume_group_type': '',
                'uid': '77',
                'source_volume_group_id': '',
                'source_volume_group_name': '',
                'parent_uid': '76',
                'source_snapshot_id': '0',
                'source_snapshot': 'snapshot_3335105753',
                'snapshot_count': '0',
                'protection_provisioned_capacity': '0.00MB',
                'protection_written_capacity': '0.00MB',
                'snapshot_policy_id': '',
                'snapshot_policy_name': '',
                'safeguarded_snapshot_count': '0',
                'ignore_user_flash_copy_maps': 'no',
                'partition_id': '',
                'partition_name': '',
                'restore_in_progress': 'no',
                'owner_type': 'none',
                'draft_partition_id': '',
                'draft_partition_name': '',
                'last_restore_time': '',
                'source_volumes_set': {'v1', 'd1'},
                'source_volumes_pool_set': {'pool0'}
            }

            with pytest.raises(AnsibleFailJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertFalse(exc.value.args[0]['changed'])
            self.assertEqual(exc.value.args[0]['msg'], 'Parameter [fromsourcevolumes] is invalid for modifying volumegroup.')

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_update_cloned_vg_pool(self,
                                           svc_authorize_mock,
                                           svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'v1d1clone',
            'state': 'present',
            'fromsourcevolumes': 'v1:d1',
            'type': 'clone',
            'pool': 'pool1'
        }):
            vg_info = {
                'id': '0',
                'name': 'v1d1clone',
                'volume_count': '2',
                'backup_status': 'off',
                'last_backup_time': '',
                'owner_id': '',
                'owner_name': '',
                'safeguarded_policy_id': '',
                'safeguarded_policy_name': '',
                'safeguarded_policy_start_time': '',
                'replication_policy_id': '',
                'replication_policy_name': '',
                'volume_group_type': '',
                'uid': '77',
                'source_volume_group_id': '',
                'source_volume_group_name': '',
                'parent_uid': '76',
                'source_snapshot_id': '0',
                'source_snapshot': 'snapshot_3335105753',
                'snapshot_count': '0',
                'protection_provisioned_capacity': '0.00MB',
                'protection_written_capacity': '0.00MB',
                'snapshot_policy_id': '',
                'snapshot_policy_name': '',
                'safeguarded_snapshot_count': '0',
                'ignore_user_flash_copy_maps': 'no',
                'partition_id': '',
                'partition_name': '',
                'restore_in_progress': 'no',
                'owner_type': 'none',
                'draft_partition_id': '',
                'draft_partition_name': '',
                'last_restore_time': ''
            }

            vol_inside_vg_info = [
                {"id": "0", "name": "V1"},
                {"id": "2", "name": "D1"}
            ]

            v1_info = [
                {
                    "id": "0", "name": "V1", "IO_group_id": "0", "IO_group_name": "io_grp0", "status": "online",
                    "mdisk_grp_id": "2", "mdisk_grp_name": "pool0", "parent_mdisk_grp_name": "pool0",
                    "type": "clone", "source_volume_name": "v1"
                }, {
                    "copy_id": "0", "status": "online",
                    "sync": "yes", "auto_delete": "no", "primary": "yes", "mdisk_grp_id": "2", "mdisk_grp_name": "pool0"
                }
            ]
            d1_info = [
                {
                    "id": "2", "name": "D1", "IO_group_id": "0", "IO_group_name": "io_grp0", "status": "online",
                    "mdisk_grp_id": "1", "mdisk_grp_name": "pool1", "parent_mdisk_grp_name": "pool1",
                    "type": "clone", "source_volume_name": "d1"
                }, {
                    "copy_id": "0", "status": "online",
                    "sync": "yes", "auto_delete": "no", "primary": "yes", "mdisk_grp_id": "1", "mdisk_grp_name": "pool1"
                }
            ]

            vol_inside_pool_info = [
                {"id": "2", "name": "d1"}
            ]

            svc_obj_info_mock.side_effect = [vg_info, vol_inside_vg_info, v1_info, d1_info, vol_inside_pool_info]

            with pytest.raises(AnsibleFailJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'], 'Provided pool [pool1] does not match the pool of one or more source volumes.')

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.get_existing_vg')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_VG_in_draftpartition(self,
                                         svc_authorize_mock,
                                         svc_get_existing_vg_mock,
                                         svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'VG0',
            'state': 'present',
            'draftpartition': 'ptn0'
        }):
            svc_get_existing_vg_mock.return_value = {}
            svc_run_command_mock.return_value = {}
            with pytest.raises(AnsibleExitJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertTrue(exc.value.args[0]['changed'])
            self.assertEqual(exc.value.args[0]['msg'], 'Volume group [VG0] has been created.')

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.get_existing_vg')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_VG_in_draftpartition_idempotency(self,
                                                     svc_authorize_mock,
                                                     svc_get_existing_vg_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'VG0',
            'state': 'present',
            'draftpartition': 'ptn0'
        }):
            svc_get_existing_vg_mock.return_value = {
                "draft_partition_id": "0",
                "draft_partition_name": "ptn0",
                "id": "2",
                "name": "VG0",
                "partition_id": "",
                "partition_name": ""
            }
            with pytest.raises(AnsibleExitJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertFalse(exc.value.args[0]['changed'])
            self.assertEqual(exc.value.args[0]['msg'], 'No Modifications detected, Volume group already exists.')

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.get_existing_vg')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_remove_VG_with_invalid_param_draftpartition(self,
                                                                 svc_authorize_mock,
                                                                 svc_get_existing_vg_mock,
                                                                 svc_run_command_mock):
        '''
        Specifying invalid parameter draftpartition while removing volumegroup; should fail
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'VG0',
            'state': 'absent',
            'draftpartition': 'ptn0'
        }):
            svc_run_command_mock.return_value = {}
            svc_get_existing_vg_mock.return_value = {
                "draft_partition_id": "0",
                "draft_partition_name": "ptn0",
                "id": "2",
                "name": "VG0",
                "partition_id": "",
                "partition_name": ""
            }
            with pytest.raises(AnsibleFailJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'], 'State=absent but following parameter(s) exist: draftpartition')

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.get_existing_vg')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_modify_VG_in_published_partition(self,
                                              svc_authorize_mock,
                                              svc_get_existing_vg_mock):
        '''
        Test for modifying voluemgeroup which is part of published partition but partition is specified in draftpartition.
        Note: 'ptno' is a published partition
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'VG0',
            'state': 'present',
            'draftpartition': 'ptn0'
        }):
            svc_get_existing_vg_mock.return_value = {
                "draft_partition_id": "",
                "draft_partition_name": "",
                "id": "2",
                "name": "VG0",
                "partition_id": "0",
                "partition_name": "ptn0"
            }
            with pytest.raises(AnsibleExitJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertFalse(exc.value.args[0]['changed'])
            self.assertEqual(exc.value.args[0]['msg'], 'No Modifications detected, Volume group already exists.')

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.get_existing_vg')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_create_VG_with_mutually_exclusive_parameter_1(self,
                                                                   svc_authorize_mock,
                                                                   svc_get_existing_vg_mock):
        '''
        Test for creating volumegroup incase of mutually exclusive draftpartition and partition parameter
        '''

        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'VG0',
            'state': 'present',
            'draftpartition': 'ptn0',
            'partition': 'ptn1'
        }):
            svc_get_existing_vg_mock.return_value = {}
            with pytest.raises(AnsibleFailJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'], 'Mutually exclusive parameters: draftpartition, partition')

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.get_existing_vg')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_modify_VG_with_mutually_exclusive_parameter_2(self,
                                                                   svc_authorize_mock,
                                                                   svc_get_existing_vg_mock):
        '''
       Test for modifying volumegroup incase of mutually exclusive draftpartition and partition parameter
        '''

        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'VG0',
            'state': 'present',
            'partition': 'ptn1',
            'draftpartition': 'ptn0'
        }):
            svc_get_existing_vg_mock.return_value = {
                "draft_partition_id": "0",
                "draft_partition_name": "ptn0",
                "id": "2",
                "name": "VG0",
                "partition_id": "",
                "partition_name": ""
            }
            with pytest.raises(AnsibleFailJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'], 'Following parameters not supported during update: partition')

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_dr_replication_policy(self, mock_svc_authorize,
                                          svc_obj_info_mock,
                                          svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'nodrreplication': True,
            'state': 'present',
        }):
            data = {
                "id": "8",
                "name": "test_volumegroup",
                "volume_count": "0",
                "backup_status": "empty",
                "last_backup_time": "",
                "owner_id": "",
                "owner_name": "",
                "safeguarded_policy_id": "",
                "safeguarded_policy_name": "",
                "safeguarded_policy_start_time": "",
                "snapshot_policy_name": "ss_policy2",
                "snapshot_policy_suspended": "no",
                "ignore_user_flash_copy_maps": "no",
                "snapshot_policy_safeguarded": "no",
                "replication_policy_name": "rp0"
            }
            svc_obj_info_mock.return_value = data
            svc_run_command_mock.return_value = "success"
            with pytest.raises(AnsibleExitJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_dr_replication_policy_idempotency(self, mock_svc_authorize,
                                                      svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volumegroup',
            'nodrreplication': True,
            'state': 'present',
        }):
            data = {
                "id": "8",
                "name": "test_volumegroup",
                "volume_count": "0",
                "backup_status": "empty",
                "last_backup_time": "",
                "owner_id": "",
                "owner_name": "",
                "safeguarded_policy_id": "",
                "safeguarded_policy_name": "",
                "safeguarded_policy_start_time": "",
                "snapshot_policy_name": "ss_policy2",
                "snapshot_policy_suspended": "no",
                "ignore_user_flash_copy_maps": "no",
                "snapshot_policy_safeguarded": "no",
                "replication_policy_name": ""
            }
            svc_obj_info_mock.return_value = data
            with pytest.raises(AnsibleExitJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_for_mutual_exclusive_parameter_4(self, mock_svc_authorize,
                                                      svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_volume',
            'state': 'present',
            'nodrreplication': True,
            'replicationpolicy': True
        }):
            data = {
                "id": "8",
                "name": "test_volumegroup",
                "volume_count": "0",
                "backup_status": "empty",
                "last_backup_time": "",
                "owner_id": "",
                "owner_name": "",
                "safeguarded_policy_id": "",
                "safeguarded_policy_name": "",
                "safeguarded_policy_start_time": "",
                "snapshot_policy_name": "ss_policy2",
                "snapshot_policy_suspended": "no",
                "ignore_user_flash_copy_maps": "no",
                "snapshot_policy_safeguarded": "no",
                "replication_policy_name": "rp0"
            }
            svc_obj_info_mock.return_value = data
            with pytest.raises(AnsibleFailJson) as exc:
                vg = IBMSVCVG()
                vg.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.get_existing_vg')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_convert_thinclone_vg_to_clone(self,
                                           mock_svc_authorize,
                                           get_existing_vg_mock,
                                           svc_run_command_mock):
        # Convert a thinclone VG to clone
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'vg0',
            'state': 'present',
            'type': 'clone'
        }):
            get_existing_vg_mock.return_value = {
                'name': 'vg0',
                'volume_group_type' : 'thinclone'
            }
            svc_run_command_mock.return_value = None

            with pytest.raises(AnsibleExitJson) as exc:
                v = IBMSVCVG()
                v.apply()
            self.assertTrue(exc.value.args[0]['changed'])
            self.assertEqual(exc.value.args[0]['msg'], 'Volume group [vg0] has been modified.')

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.get_existing_vg')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_convert_thinclone_vg_to_clone_idempotency_1(self,
                                                         mock_svc_authorize,
                                                         get_existing_vg_mock,
                                                         svc_run_command_mock):
        # Try to convert a thinclone VG to clone when it has already been run and copy is in progress
        # At this time, volumegroup's volume_group_type = 'clone'
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'vg0',
            'state': 'present',
            'type': 'clone'
        }):
            get_existing_vg_mock.return_value = {
                'name': 'vg0',
                'volume_group_type' : 'clone'
            }
            svc_run_command_mock.return_value = None

            with pytest.raises(AnsibleExitJson) as exc:
                v = IBMSVCVG()
                v.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.get_existing_vg')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_convert_thinclone_vg_to_clone_idempotency_2(self,
                                                         mock_svc_authorize,
                                                         get_existing_vg_mock,
                                                         svc_run_command_mock):
        # Try to convert a thinclone VG to clone when it has already been run and copy is completed
        # At this time, volumegroup's volume_group_type = ''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'vg0',
            'state': 'present',
            'type': 'clone'
        }):
            get_existing_vg_mock.return_value = {
                'name': 'vg0',
                'volume_group_type' : ''  # Volumegrouphas already converted to clone and copy is completed.
            }
            svc_run_command_mock.return_value = None

            with pytest.raises(AnsibleExitJson) as exc:
                v = IBMSVCVG()
                v.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.get_existing_vg')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_convert_vg_to_thinclone(self,
                                             mock_svc_authorize,
                                             get_existing_vg_mock,
                                             svc_run_command_mock):
        # If user passes type=thinclone, test whether the correct failure path is taken.
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'vg0',
            'state': 'present',
            'type': 'thinclone'
        }):
            get_existing_vg_mock.return_value = {
                'name': 'vg0',
                'volume_group_type' : ''  # Volumegroup is either clone or normal VG (not thinclone)
            }
            svc_run_command_mock.return_value = None

            with pytest.raises(AnsibleFailJson) as exc:
                v = IBMSVCVG()
                v.apply()
            self.assertEqual(exc.value.args[0]['msg'], 'type = thinclone is invalid for updating volumegroup.'
                             ' Only type = clone is supported.')

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.get_existing_vg')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_invalid_params_with_type_change(self,
                                                     mock_svc_authorize,
                                                     get_existing_vg_mock,
                                                     svc_run_command_mock):
        # Try to convert a thinclone VG to clone, along with other param replicationpolicy
        # It should be exclusively passed, and not with any chvolumegroup parameters, so expect failure.
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'vg0',
            'state': 'present',
            'type': 'clone',
            'replicationpolicy': 'rp0'
        }):
            get_existing_vg_mock.return_value = {
                'name': 'vg0',
                'volume_group_type' : 'thinclone'  # Volumegroup is either clone or normal VG (not thinclone)
            }
            svc_run_command_mock.return_value = None

            with pytest.raises(AnsibleFailJson) as exc:
                v = IBMSVCVG()
                v.apply()
            self.assertEqual(exc.value.args[0]['msg'], 'Following parameter(s) are invalid'
                             ' while converting thinclone volumegroup to clone: replicationpolicy')

    # UUID-based tests for volumegroup
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.get_existing_vg')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_creation_of_new_volumegroup_using_UUID(self, mock_svc_authorize,
                                                    get_existing_vg_mock):
        '''Test creating a new volumegroup using UUID as name'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': '420EC615-4404-55BA-D8A7-5F91C23E7B40',
            'state': 'present',
        }):
            get_existing_vg_mock.return_value = {}
            with pytest.raises(AnsibleFailJson) as exc:
                v = IBMSVCVG()
                v.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'], "Volume group with UUID [420EC615-4404-55BA-D8A7-5F91C23E7B40] does not exist and cannot be created.")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.get_existing_vg')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_idempotency_creation_when_volumegroup_already_existing_using_UUID(
            self, mock_svc_authorize, get_existing_vg_mock):
        '''Test idempotency when creating an existing volumegroup using UUID'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': '420EC615-4404-55BA-D8A7-5F91C23E7B40',
            'state': 'present',
        }):
            get_existing_vg_mock.return_value = {
                "id": "10",
                "name": "test_volumegroup",
                "volume_count": "0",
                "backup_status": "empty",
                "last_backup_time": "",
                "owner_id": "",
                "owner_name": "",
                "safeguarded_policy_id": "",
                "safeguarded_policy_name": "",
                "safeguarded_policy_start_time": "",
                "snapshot_policy_name": "",
                "snapshot_policy_suspended": "no",
                "ignore_user_flash_copy_maps": "no",
                "snapshot_policy_safeguarded": "no",
                "uid": "420EC615-4404-55BA-D8A7-5F91C23E7B40"
            }
            with pytest.raises(AnsibleExitJson) as exc:
                v = IBMSVCVG()
                v.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.get_existing_vg')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_module_for_deleting_an_existing_volumegroup_using_UUID(self, mock_svc_authorize,
                                                                    get_existing_vg_mock,
                                                                    svc_run_command_mock):
        '''Test deleting an existing volumegroup using UUID'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': '420EC615-4404-55BA-D8A7-5F91C23E7B40',
            'state': 'absent',
        }):
            get_existing_vg_mock.return_value = {
                "id": "10",
                "name": "test_volumegroup",
                "volume_count": "0",
                "uid": "420EC615-4404-55BA-D8A7-5F91C23E7B40"
            }
            svc_run_command_mock.return_value = None
            with pytest.raises(AnsibleExitJson) as exc:
                v = IBMSVCVG()
                v.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.get_existing_vg')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_idempotency_deleting_nonexisting_volumegroup_using_UUID(self, mock_svc_authorize,
                                                                     get_existing_vg_mock):
        '''Test idempotency when deleting a non-existing volumegroup using UUID'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': '420EC615-4404-55BA-D8A7-5F91C23E7B40',
            'state': 'absent',
        }):
            get_existing_vg_mock.return_value = {}
            with pytest.raises(AnsibleExitJson) as exc:
                v = IBMSVCVG()
                v.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_volumegroup.IBMSVCVG.get_existing_vg')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_module_while_updating_ownershipgroup_using_UUID(self, mock_svc_authorize,
                                                             get_existing_vg_mock,
                                                             svc_run_command_mock):
        '''Test updating ownershipgroup using UUID'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': '420EC615-4404-55BA-D8A7-5F91C23E7B40',
            'state': 'present',
            'ownershipgroup': 'test_ownershipgroup_new'
        }):
            get_existing_vg_mock.return_value = {
                "id": "10",
                "name": "test_volumegroup",
                "volume_count": "0",
                "backup_status": "empty",
                "last_backup_time": "",
                "owner_id": "",
                "owner_name": "test_ownershipgroup_old",
                "safeguarded_policy_id": "",
                "safeguarded_policy_name": "",
                "safeguarded_policy_start_time": "",
                "snapshot_policy_name": "",
                "snapshot_policy_suspended": "no",
                "ignore_user_flash_copy_maps": "no",
                "snapshot_policy_safeguarded": "no",
                "uid": "420EC615-4404-55BA-D8A7-5F91C23E7B40"
            }
            svc_run_command_mock.return_value = None
            with pytest.raises(AnsibleExitJson) as exc:
                v = IBMSVCVG()
                v.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_rename_volumegroup_using_UUID_old_name(self, mock_svc_authorize,
                                                    svc_obj_info_mock,
                                                    svc_run_command_mock):
        '''Test renaming volumegroup using UUID as old_name'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'new_vg_name',
            'old_name': '420EC615-4404-55BA-D8A7-5F91C23E7B40',
            'state': 'present',
        }):
            svc_obj_info_mock.side_effect = [
                [],  # new name doesn't exist
                {    # old UUID exists
                    "id": "10",
                    "name": "old_vg_name",
                    "uid": "420EC615-4404-55BA-D8A7-5F91C23E7B40",
                    "volume_count": "0",
                    "owner_name": "",
                    "snapshot_policy_name": "",
                    "replication_policy_name": "",
                    "partition_name": "",
                    "draft_partition_name": ""
                }
            ]
            svc_run_command_mock.return_value = None
            with pytest.raises(AnsibleExitJson) as exc:
                v = IBMSVCVG()
                v.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_volumegroup_with_UUID_snapshotpolicy(self, mock_svc_authorize,
                                                         svc_obj_info_mock,
                                                         svc_run_command_mock):
        '''Test creating volumegroup with UUID snapshotpolicy'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_vg',
            'state': 'present',
            'snapshotpolicy': '058C1215-9786-5C3E-B2C6-8F41A7D35E90'
        }):
            svc_obj_info_mock.return_value = []
            svc_run_command_mock.return_value = {
                'id': '10',
                'message': 'Volume Group, id [10], successfully created'
            }
            with pytest.raises(AnsibleExitJson) as exc:
                v = IBMSVCVG()
                v.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_volumegroup_snapshotpolicy_UUID_match(self, mock_svc_authorize,
                                                          svc_obj_info_mock,
                                                          svc_run_command_mock):
        '''Test updating volumegroup when UUID snapshotpolicy matches existing'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_vg',
            'state': 'present',
            'snapshotpolicy': '058C1215-9786-5C3E-B2C6-8F41A7D35E90'
        }):
            svc_obj_info_mock.side_effect = [
                {    # existing volumegroup
                    "id": "10",
                    "name": "test_vg",
                    "uid": "420EC615-4404-55BA-D8A7-5F91C23E7B40",
                    "volume_count": "0",
                    "owner_name": "",
                    "snapshot_policy_name": "test_snapshot_policy",
                    "snapshot_policy_safeguarded": "no",
                    "replication_policy_name": "",
                    "partition_name": "",
                    "draft_partition_name": ""
                },
                [{   # snapshotpolicy info
                    'id': '1',
                    'name': 'test_snapshot_policy',
                    'uuid': '058C1215-9786-5C3E-B2C6-8F41A7D35E90'
                }]
            ]
            with pytest.raises(AnsibleExitJson) as exc:
                v = IBMSVCVG()
                v.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_volumegroup_with_UUID_pool(self, mock_svc_authorize,
                                               svc_obj_info_mock,
                                               svc_run_command_mock):
        '''Test creating volumegroup with UUID pool'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_vg',
            'state': 'present',
            'type': 'clone',
            'fromsourcegroup': 'source_vg',
            'pool': '80050768108180ED700000000000006A'
        }):
            svc_obj_info_mock.return_value = []
            svc_run_command_mock.return_value = {
                'id': '10',
                'message': 'Volume Group, id [10], successfully created'
            }
            with pytest.raises(AnsibleExitJson) as exc:
                v = IBMSVCVG()
                v.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_volumegroup_with_UUID_replicationpolicy(self, mock_svc_authorize,
                                                            svc_obj_info_mock,
                                                            svc_run_command_mock):
        '''Test creating volumegroup with UUID replicationpolicy'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_vg',
            'state': 'present',
            'replicationpolicy': '0D6A7840-1AD2-57D1-A3D8-71F4C92E6B50'
        }):
            svc_obj_info_mock.return_value = []
            svc_run_command_mock.return_value = {
                'id': '10',
                'message': 'Volume Group, id [10], successfully created'
            }
            with pytest.raises(AnsibleExitJson) as exc:
                v = IBMSVCVG()
                v.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_volumegroup_replicationpolicy_UUID_match(self, mock_svc_authorize,
                                                             svc_obj_info_mock,
                                                             svc_run_command_mock):
        '''Test updating volumegroup when UUID replicationpolicy matches existing'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_vg',
            'state': 'present',
            'replicationpolicy': '0D6A7840-1AD2-57D1-A3D8-71F4C92E6B50'
        }):
            svc_obj_info_mock.side_effect = [
                {    # existing volumegroup
                    "id": "10",
                    "name": "test_vg",
                    "uid": "420EC615-4404-55BA-D8A7-5F91C23E7B40",
                    "volume_count": "0",
                    "owner_name": "",
                    "snapshot_policy_name": "",
                    "replication_policy_name": "test_replication_policy",
                    "partition_name": "",
                    "draft_partition_name": ""
                },
                {    # replicationpolicy info
                    'id': '1',
                    'name': 'test_replication_policy',
                    'uuid': '0D6A7840-1AD2-57D1-A3D8-71F4C92E6B50'
                }
            ]
            with pytest.raises(AnsibleExitJson) as exc:
                v = IBMSVCVG()
                v.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_volumegroup_with_UUID_partition(self, mock_svc_authorize,
                                                    svc_obj_info_mock,
                                                    svc_run_command_mock):
        '''Test creating volumegroup with UUID partition'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_vg',
            'state': 'present',
            'partition': 'A0050768108180ED700000000000008A'
        }):
            svc_obj_info_mock.return_value = []
            svc_run_command_mock.return_value = {
                'id': '10',
                'message': 'Volume Group, id [10], successfully created'
            }
            with pytest.raises(AnsibleExitJson) as exc:
                v = IBMSVCVG()
                v.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_volumegroup_partition_UUID_match(self, mock_svc_authorize,
                                                     svc_obj_info_mock,
                                                     svc_run_command_mock):
        '''Test updating volumegroup when UUID partition matches existing'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_vg',
            'state': 'present',
            'partition': 'A0050768108180ED700000000000008A'
        }):
            svc_obj_info_mock.side_effect = [
                {    # existing volumegroup
                    "id": "10",
                    "name": "test_vg",
                    "uid": "420EC615-4404-55BA-D8A7-5F91C23E7B40",
                    "volume_count": "0",
                    "owner_name": "",
                    "snapshot_policy_name": "",
                    "replication_policy_name": "",
                    "partition_name": "test_partition",
                    "draft_partition_name": ""
                },
                {    # partition info
                    'id': '1',
                    'name': 'test_partition',
                    'uuid': 'A0050768108180ED700000000000008A'
                }
            ]
            with pytest.raises(AnsibleExitJson) as exc:
                v = IBMSVCVG()
                v.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_volumegroup_with_UUID_draftpartition(self, mock_svc_authorize,
                                                         svc_obj_info_mock,
                                                         svc_run_command_mock):
        '''Test creating volumegroup with UUID draftpartition'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_vg',
            'state': 'present',
            'draftpartition': 'B0050768108180ED700000000000009A'
        }):
            svc_obj_info_mock.return_value = []
            svc_run_command_mock.return_value = {
                'id': '10',
                'message': 'Volume Group, id [10], successfully created'
            }
            with pytest.raises(AnsibleExitJson) as exc:
                v = IBMSVCVG()
                v.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_volumegroup_draftpartition_UUID_match(self, mock_svc_authorize,
                                                          svc_obj_info_mock,
                                                          svc_run_command_mock):
        '''Test updating volumegroup when UUID draftpartition matches existing'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_vg',
            'state': 'present',
            'draftpartition': 'B0050768108180ED700000000000009A'
        }):
            svc_obj_info_mock.side_effect = [
                {    # existing volumegroup
                    "id": "10",
                    "name": "test_vg",
                    "uid": "420EC615-4404-55BA-D8A7-5F91C23E7B40",
                    "volume_count": "0",
                    "owner_name": "",
                    "snapshot_policy_name": "",
                    "replication_policy_name": "",
                    "partition_name": "",
                    "draft_partition_name": "test_draft_partition"
                },
                {    # draftpartition info
                    'id': '1',
                    'name': 'test_draft_partition',
                    'uuid': 'B0050768108180ED700000000000009A'
                }
            ]
            with pytest.raises(AnsibleExitJson) as exc:
                v = IBMSVCVG()
                v.apply()
            self.assertFalse(exc.value.args[0]['changed'])


if __name__ == '__main__':
    unittest.main()
