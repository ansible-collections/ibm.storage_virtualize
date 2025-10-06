# Copyright (C) 2020 IBM CORPORATION
# Author(s): Sanjaikumaar M <sanjaikumaar.m@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Storage Virtualize Ansible module: ibm_svc_manage_ownershipgroup """

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.storage_virtualize.plugins.modules.ibm_svc_manage_ownershipgroup import \
    IBMSVCOwnershipgroup
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


class TestIBMSVCOwnershipgroup(unittest.TestCase):

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
                IBMSVCOwnershipgroup()
            self.assertTrue(exc.value.args[0]['failed'])

    def test_module_fail_when_name_parameter_missing(self):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password'
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                IBMSVCOwnershipgroup()
            self.assertTrue(exc.value.args[0]['failed'])

    def test_module_fail_when_name_is_blank(self):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': ''
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                IBMSVCOwnershipgroup()
            self.assertTrue(exc.value.args[0]['failed'])

    def test_module_fail_when_state_parameter_missing(self):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'name': 'ansible_owshgroup',
            'username': 'username',
            'password': 'password'
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                IBMSVCOwnershipgroup()
            self.assertTrue(exc.value.args[0]['failed'])

    def test_module_fail_when_state_parameter_is_blank(self):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'name': 'ansible_owshgroup',
            'username': 'username',
            'password': 'password',
            'state': ''
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                IBMSVCOwnershipgroup()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_ownershipgroup.IBMSVCOwnershipgroup.check_existing_owgroups')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_ownershipgroup_with_keepobjects(self,
                                                    svc_authorize_mock,
                                                    check_existing_ownership_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_owshgroup',
            'keepobjects': True
        }):
            check_existing_ownership_mock.return_value = False

            ownership = IBMSVCOwnershipgroup()
            with pytest.raises(AnsibleFailJson) as exc:
                ownership.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_ownershipgroup.IBMSVCOwnershipgroup.check_existing_owgroups')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_ownershipgroup(self, svc_authorize_mock,
                                   svc_run_mock,
                                   check_existing_ownership_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_owshgroup'
        }):
            message = {
                'id': '0',
                'message': 'Ownership Group, id [0], successfully created'
            }
            svc_run_mock.return_value = message
            check_existing_ownership_mock.return_value = {}

            ownership = IBMSVCOwnershipgroup()
            with pytest.raises(AnsibleExitJson) as exc:
                ownership.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_ownershipgroup.IBMSVCOwnershipgroup.check_existing_owgroups')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_existing_owgroups(self,
                                      svc_authorize_mock,
                                      check_existing_ownership_mock):

        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_owshgroup'
        }):
            return_val = {
                'id': '0',
                'name': 'ansible_owshgroup'
            }
            check_existing_ownership_mock.return_value = return_val
            ownership = IBMSVCOwnershipgroup()
            with pytest.raises(AnsibleExitJson) as exc:
                ownership.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_ownershipgroup.IBMSVCOwnershipgroup.check_existing_owgroups')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_owgrp_without_keepobjs(self,
                                           svc_authorize_mock,
                                           check_existing_ownership_mock,
                                           svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_owshgroup'
        }):
            check_existing_ownership_mock.return_value = True
            ownership = IBMSVCOwnershipgroup()
            with pytest.raises(AnsibleExitJson) as exc:
                ownership.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_ownershipgroup.IBMSVCOwnershipgroup.check_existing_owgroups')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    def test_delete_owgrp_with_keepobjs_scenario_1(self,
                                                   svc_run_command_mock,
                                                   check_existing_ownership_mock,
                                                   svc_authorize_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_owshgroup',
            'keepobjects': True
        }):
            check_existing_ownership_mock.return_value = True
            ownership = IBMSVCOwnershipgroup()
            with pytest.raises(AnsibleExitJson) as exc:
                ownership.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_ownershipgroup.IBMSVCOwnershipgroup.check_existing_owgroups')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_token_wrap')
    def test_delete_owgrp_with_keepobjs_scenario_2(self,
                                                   svc_token_mock,
                                                   check_existing_ownership_mock,
                                                   svc_authorize_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_owshgroup',
            'keepobjects': True
        }):
            check_existing_ownership_mock.return_value = True
            svc_token_mock.return_value = {
                'err': "httperror HTTP Error 500: Internal Server Error",
                'out': 'Ownership group associated with one or more usergroup'
            }
            ownership = IBMSVCOwnershipgroup()
            with pytest.raises(AnsibleFailJson) as exc:
                ownership.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_manage_ownershipgroup.IBMSVCOwnershipgroup.check_existing_owgroups')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    def test_delete_owgrp_non_existence(self,
                                        svc_run_command_mock,
                                        check_existing_owgroup_mock,
                                        svc_authorize_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_owshgroup',
            'keepobjects': True
        }):
            check_existing_owgroup_mock.return_value = False
            ownership = IBMSVCOwnershipgroup()
            with pytest.raises(AnsibleExitJson) as exc:
                ownership.apply()
            self.assertFalse(exc.value.args[0]['changed'])


if __name__ == '__main__':
    unittest.main()
