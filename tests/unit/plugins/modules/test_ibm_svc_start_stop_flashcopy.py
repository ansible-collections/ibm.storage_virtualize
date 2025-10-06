# Copyright (C) 2020 IBM CORPORATION
# Author(s): Sreshtant Bohidar <sreshtant.bohidar@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Storage Virtualize Ansible module: ibm_svc_start_stop_flashcopy """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.storage_virtualize.plugins.modules.ibm_svc_start_stop_flashcopy import IBMSVCFlashcopyStartStop
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


class TestIBMSVCFlashcopyStartStop(unittest.TestCase):
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
                IBMSVCFlashcopyStartStop()
            print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_fcmapping(self, svc_authorize_mock, svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_fcmap',
            'state': 'started'
        }):
            svc_obj_info_mock.return_value = {
                "id": "1", "name": "test_fcmap", "source_vdisk_id": "12", "source_vdisk_name": "test_vol0", "target_vdisk_id": "13",
                "target_vdisk_name": "test_vol1", "group_id": "", "group_name": "", "status": "idle_or_copied", "progress": "0", "copy_rate": "50",
                "start_time": "1759250169", "dependent_mappings": "0", "autodelete": "off", "clean_progress": "100", "clean_rate": "50", "incremental": "on",
                "difference": "100", "grain_size": "256", "IO_group_id": "0", "IO_group_name": "io_grp0", "partner_FC_id": "", "partner_FC_name": "",
                "restoring": "no", "rc_controlled": "no", "keep_target": "no", "type": "generic", "restore_progress": "0", "fc_controlled": "no",
                "owner_id": "", "owner_name": "", "size_mismatch": "no", "start_capacity": "", "is_snapshot": "no", "snapshot_id": ""
            }
            obj = IBMSVCFlashcopyStartStop()
            data = obj.get_existing_fcmapping()
            self.assertEqual('test_fcmap', data['name'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_fcconsistgrp(self, svc_authorize_mock, svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_fccstgrp',
            'state': 'started',
            'isgroup': True
        }):
            svc_obj_info_mock.return_value = {
                'id': '1', 'name': 'test_fccstgrp', 'status': 'idle_or_copied',
                'autodelete': 'off', 'start_time': '', 'owner_id': '0',
                'owner_name': 'test_ownershipgroup', 'FC_mapping_id': '0',
                'FC_mapping_name': 'test_fcmap0'
            }
            obj = IBMSVCFlashcopyStartStop()
            data = obj.get_existing_fcmapping()
            self.assertEqual('test_fccstgrp', data['name'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_start_existsting_fc_mappping(self, svc_authorize_mock, svc_obj_info_mock, svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_fcmap',
            'state': 'started'
        }):
            svc_obj_info_mock.return_value = {
                "id": "1", "name": "test_fcmap", "source_vdisk_id": "12", "source_vdisk_name": "test_vol0", "target_vdisk_id": "13",
                "target_vdisk_name": "test_vol1", "group_id": "", "group_name": "", "status": "idle_or_copied", "progress": "0", "copy_rate": "50",
                "start_time": "1759250169", "dependent_mappings": "0", "autodelete": "off", "clean_progress": "100", "clean_rate": "50", "incremental": "on",
                "difference": "100", "grain_size": "256", "IO_group_id": "0", "IO_group_name": "io_grp0", "partner_FC_id": "", "partner_FC_name": "",
                "restoring": "no", "rc_controlled": "no", "keep_target": "no", "type": "generic", "restore_progress": "0", "fc_controlled": "no",
                "owner_id": "", "owner_name": "", "size_mismatch": "no", "start_capacity": "", "is_snapshot": "no", "snapshot_id": ""
            }
            with pytest.raises(AnsibleExitJson) as exc:
                obj = IBMSVCFlashcopyStartStop()
                obj.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_start_nonexiststing_fc_mappping(self, svc_authorize_mock, svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_fcmap',
            'state': 'started'
        }):
            svc_obj_info_mock.return_value = {}
            with pytest.raises(AnsibleFailJson) as exc:
                obj = IBMSVCFlashcopyStartStop()
                obj.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'], "FlashCopy Mapping [test_fcmap] does not exist.")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_start_existsting_fc_consistgrp(self, svc_authorize_mock, svc_obj_info_mock, svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_fccstgrp',
            'state': 'started',
            'isgroup': True
        }):
            svc_obj_info_mock.return_value = {
                'id': '1', 'name': 'test_fccstgrp', 'status': 'idle_or_copied',
                'autodelete': 'off', 'start_time': '', 'owner_id': '0',
                'owner_name': 'test_ownershipgroup', 'FC_mapping_id': '0',
                'FC_mapping_name': 'test_fcmap0'
            }
            with pytest.raises(AnsibleExitJson) as exc:
                obj = IBMSVCFlashcopyStartStop()
                obj.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_start_nonexiststing_fc_consistgrp(self, svc_authorize_mock, svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_fccstgrp',
            'state': 'started',
            'isgroup': True
        }):
            svc_obj_info_mock.return_value = {}
            with pytest.raises(AnsibleFailJson) as exc:
                obj = IBMSVCFlashcopyStartStop()
                obj.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'], "FlashCopy Consistency Group [test_fccstgrp] does not exist.")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_stop_existsting_fc_mappping(self, svc_authorize_mock, svc_obj_info_mock, svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_fcmap',
            'state': 'stopped'
        }):
            svc_obj_info_mock.return_value = {
                "id": "1", "name": "test_fcmap", "source_vdisk_id": "12", "source_vdisk_name": "test_vol0", "target_vdisk_id": "13",
                "target_vdisk_name": "test_vol1", "group_id": "", "group_name": "", "status": "copying", "progress": "0", "copy_rate": "50",
                "start_time": "1759250169", "dependent_mappings": "0", "autodelete": "off", "clean_progress": "100", "clean_rate": "50", "incremental": "on",
                "difference": "100", "grain_size": "256", "IO_group_id": "0", "IO_group_name": "io_grp0", "partner_FC_id": "", "partner_FC_name": "",
                "restoring": "no", "rc_controlled": "no", "keep_target": "no", "type": "generic", "restore_progress": "0", "fc_controlled": "no",
                "owner_id": "", "owner_name": "", "size_mismatch": "no", "start_capacity": "", "is_snapshot": "no", "snapshot_id": ""
            }
            with pytest.raises(AnsibleExitJson) as exc:
                obj = IBMSVCFlashcopyStartStop()
                obj.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_stop_existsting_fc_mappping_with_force(self, svc_authorize_mock, svc_obj_info_mock, svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_fcmap',
            'state': 'stopped',
            'force': True
        }):
            svc_obj_info_mock.return_value = {
                "id": "1", "name": "test_fcmap", "source_vdisk_id": "12", "source_vdisk_name": "test_vol0", "target_vdisk_id": "13",
                "target_vdisk_name": "test_vol1", "group_id": "", "group_name": "", "status": "copying", "progress": "0", "copy_rate": "50",
                "start_time": "1759250169", "dependent_mappings": "0", "autodelete": "off", "clean_progress": "100", "clean_rate": "50", "incremental": "on",
                "difference": "100", "grain_size": "256", "IO_group_id": "0", "IO_group_name": "io_grp0", "partner_FC_id": "", "partner_FC_name": "",
                "restoring": "no", "rc_controlled": "no", "keep_target": "no", "type": "generic", "restore_progress": "0", "fc_controlled": "no",
                "owner_id": "", "owner_name": "", "size_mismatch": "no", "start_capacity": "", "is_snapshot": "no", "snapshot_id": ""
            }
            with pytest.raises(AnsibleExitJson) as exc:
                obj = IBMSVCFlashcopyStartStop()
                obj.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_stop_nonexiststing_fc_mappping(self, svc_authorize_mock, svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_fcmap',
            'state': 'stopped'
        }):
            svc_obj_info_mock.return_value = {}
            with pytest.raises(AnsibleFailJson) as exc:
                obj = IBMSVCFlashcopyStartStop()
                obj.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'], "FlashCopy Mapping [test_fcmap] does not exist.")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_stop_existsting_fc_consistgrp(self, svc_authorize_mock, svc_obj_info_mock, svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_fccstgrp',
            'isgroup': True,
            'state': 'stopped'
        }):
            svc_obj_info_mock.return_value = {
                'id': '4', 'name': 'test_fccstgrp', 'status': 'copying',
                'autodelete': 'off', 'start_time': '210112110946', 'owner_id': '0',
                'owner_name': 'test_ownershipgroup', 'FC_mapping_id': '0',
                'FC_mapping_name': 'test_fcmap0'
            }
            with pytest.raises(AnsibleExitJson) as exc:
                obj = IBMSVCFlashcopyStartStop()
                obj.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_stop_existsting_fc_consistgrp_with_force(self, svc_authorize_mock, svc_obj_info_mock, svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_fccstgrp',
            'isgroup': True,
            'state': 'stopped',
            'force': True
        }):
            svc_obj_info_mock.return_value = {
                'id': '4', 'name': 'test_fccstgrp', 'status': 'copying',
                'autodelete': 'off', 'start_time': '210112110946', 'owner_id': '0',
                'owner_name': 'test_ownershipgroup', 'FC_mapping_id': '0',
                'FC_mapping_name': 'test_fcmap0'
            }
            with pytest.raises(AnsibleExitJson) as exc:
                obj = IBMSVCFlashcopyStartStop()
                obj.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_stop_nonexiststing_fc_consistgrp(self, svc_authorize_mock, svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_fccstgrp',
            'isgroup': True,
            'state': 'stopped'
        }):
            svc_obj_info_mock.return_value = {}
            with pytest.raises(AnsibleFailJson) as exc:
                obj = IBMSVCFlashcopyStartStop()
                obj.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'], "FlashCopy Consistency Group [test_fccstgrp] does not exist.")


if __name__ == "__main__":
    unittest.main()
