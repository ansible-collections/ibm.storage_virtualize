# Copyright (C) 2022 IBM CORPORATION
# Author(s): Sanjaikumaar M <sanjaikumaar.m@ibm.com>
#            Rahul Pawar <rahul.p@ibm.com>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Storage Virtualize Ansible module: ibm_svc_manage_portset """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.storage_virtualize.plugins.modules.ibm_svc_manage_portset import IBMSVCPortset
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


class TestIBMSVCPortset(unittest.TestCase):
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
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': '',
            'state': 'present'
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                IBMSVCPortset()
            self.assertTrue(exc.value.args[0]['failed'])

    def test_mutually_exclusive_case(self):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'ownershipgroup': 'new_owner',
            'noownershipgroup': True,
            'state': 'present'
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                IBMSVCPortset()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_portset_with_required_params(self,
                                                 svc_authorize_mock,
                                                 svc_run_command_mock,
                                                 svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'state': 'present'
        }):
            svc_obj_info_mock.return_value = {}
            svc_run_command_mock.return_value = {
                'id': '0',
                'message': 'Portset, id [0], successfully created'
            }
            with pytest.raises(AnsibleExitJson) as exc:
                p = IBMSVCPortset()
                p.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_replication_type_portset(self,
                                             svc_authorize_mock,
                                             svc_run_command_mock,
                                             svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'porttype': 'ethernet',
            'portset_type': 'replication',
            'ownershipgroup': 'new_owner',
            'state': 'present'
        }):
            svc_obj_info_mock.return_value = {}
            svc_run_command_mock.return_value = {
                'id': '0',
                'message': 'Portset, id [0], successfully created'
            }
            with pytest.raises(AnsibleExitJson) as exc:
                p = IBMSVCPortset()
                p.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_host_type_portset(self,
                                      svc_authorize_mock,
                                      svc_run_command_mock,
                                      svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'porttype': 'fc',
            'ownershipgroup': 'new_owner',
            'portset_type': 'host',
            'state': 'present'
        }):
            svc_obj_info_mock.return_value = {}
            svc_run_command_mock.return_value = {
                'id': '0',
                'message': 'Portset, id [0], successfully created'
            }

            with pytest.raises(AnsibleExitJson) as exc:
                p = IBMSVCPortset()
                p.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_portset_with_highspeedreplication_type(self,
                                                           svc_authorize_mock,
                                                           svc_run_command_mock,
                                                           svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset1',
            'porttype': 'ethernet',
            'portset_type': 'highspeedreplication',
            'state': 'present'
        }):
            svc_obj_info_mock.return_value = {}

            with pytest.raises(AnsibleExitJson) as exc:
                p = IBMSVCPortset()
                p.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_create_fc_portset_with_highspeedreplication_type(self,
                                                                      svc_authorize_mock,
                                                                      svc_run_command_mock,
                                                                      svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset1',
            'porttype': 'fc',
            'portset_type': 'highspeedreplication',
            'state': 'present'
        }):
            svc_obj_info_mock.return_value = {}

            with pytest.raises(AnsibleExitJson) as exc:
                p = IBMSVCPortset()
                p.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_portset_idempotency(self,
                                        svc_authorize_mock,
                                        svc_run_command_mock,
                                        svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'porttype': 'fc',
            'portset_type': 'host',
            'ownershipgroup': 'new_owner',
            'autozoneenabled': 'yes',
            'autozonepolicy': 'one_to_one',
            'state': 'present'
        }):
            svc_obj_info_mock.side_effect = [
                # lsportset OP:
                {
                    "id": "4",
                    "name": "portset0",
                    "type": "host",
                    "port_type": "fc",
                    "port_count": "0",
                    "host_count": "0",
                    "lossless": "",
                    "owner_id": "0",
                    "owner_name": "new_owner",
                    "auto_zone_enabled": "yes",
                    "auto_zone_policy": "one_to_one"
                },
                # lssystem OP:
                {"id": "00000204AEA0632C", "name": "system0", "code_level": "9.1.3.0 (build 193.16.2602231501000)"}
            ]

            with pytest.raises(AnsibleExitJson) as exc:
                p = IBMSVCPortset()
                p.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_portset(self,
                            svc_authorize_mock,
                            svc_run_command_mock,
                            svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'noownershipgroup': True,
            'state': 'present'
        }):
            svc_obj_info_mock.return_value = {
                "id": "4",
                "name": "portset0",
                "type": "host",
                "port_count": "0",
                "host_count": "0",
                "lossless": "",
                "owner_id": "0",
                "owner_name": "new_owner"
            }

            with pytest.raises(AnsibleExitJson) as exc:
                p = IBMSVCPortset()
                p.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_portset_rename(self, svc_authorize_mock,
                            svc_run_command_mock,
                            svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'new_name',
            'old_name': 'portset0',
            'state': 'present'
        }):
            svc_obj_info_mock.return_value = {
                "id": "4",
                "name": "portset0",
                "type": "host",
                "port_count": "0",
                "host_count": "0",
                "lossless": "",
                "owner_id": "0",
                "owner_name": "new_owner"
            }

            arg_data = []
            v = IBMSVCPortset()
            data = v.portset_rename(arg_data)
            self.assertEqual(data, 'Portset [portset0] has been successfully rename to [new_name].')

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_delete_portset_with_invalid_param(self,
                                                       svc_authorize_mock,
                                                       svc_run_command_mock,
                                                       svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'portset_type': 'host',
            'ownershipgroup': 'new_owner',
            'autozoneenabled': 'yes',
            'autozonepolicy': 'one_to_one',
            'state': 'absent'
        }):
            svc_obj_info_mock.return_value = {
                "id": "4",
                "name": "portset0",
                "type": "host",
                "port_count": "0",
                "host_count": "0",
                "lossless": "",
                "owner_id": "0",
                "owner_name": "new_owner"
            }

            with pytest.raises(AnsibleFailJson) as exc:
                IBMSVCPortset()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(
                exc.value.args[0]['msg'], "Parameters ownershipgroup, portset_type, autozoneenabled, autozonepolicy not supported while deleting a portset."
            )

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_portset(self,
                            svc_authorize_mock,
                            svc_run_command_mock,
                            svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'state': 'absent'
        }):
            svc_obj_info_mock.return_value = {
                "id": "4",
                "name": "portset0",
                "port_count": "0",
                "host_count": "0",
                "lossless": "",
                "owner_id": "0",
                "owner_name": "new_owner"
            }

            with pytest.raises(AnsibleExitJson) as exc:
                p = IBMSVCPortset()
                p.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_portset_idempotency(self,
                                        svc_authorize_mock,
                                        svc_run_command_mock,
                                        svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'state': 'absent'
        }):
            svc_obj_info_mock.return_value = {}

            with pytest.raises(AnsibleExitJson) as exc:
                p = IBMSVCPortset()
                p.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_portset_with_replicationportsetlinkuid(self, svc_authorize_mock, svc_run_command_mock, svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'fcportset1',
            'porttype': 'fc',
            'portset_type': 'host',
            'replicationportsetlinkuid': 'F8C5C02FC24F019154B57B59DD753BFF',
            'state': 'present'
        }):
            svc_obj_info_mock.return_value = {}
            svc_run_command_mock.return_value = {
                'id': '0',
                'message': 'Portset, id [0], successfully created'
            }

            with pytest.raises(AnsibleExitJson) as exc:
                p = IBMSVCPortset()
                p.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_portset_with_replicationportsetlinkuid_idempotency(self, svc_authorize_mock, svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'fcportset1',
            'porttype': 'fc',
            'portset_type': 'host',
            'replicationportsetlinkuid': 'F8C5C02FC24F019154B57B59DD753BFF',
            'state': 'present'
        }):
            svc_obj_info_mock.return_value = {
                'id': '0',
                'name': 'fcportset1',
                'type': 'host',
                'portset_type': 'host',
                'port_type': 'fc',
                'replication_portset_link_uid': 'F8C5C02FC24F019154B57B59DD753BFF',
            }

            with pytest.raises(AnsibleExitJson) as exc:
                p = IBMSVCPortset()
                p.apply()
            self.assertFalse(exc.value.args[0]['changed'])
            self.assertEqual(exc.value.args[0]['msg'], "Portset (fcportset1) already exists. No modifications done.")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_replicationportsetlinkuid(self, svc_authorize_mock, svc_run_command_mock, svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'fcportset1',
            'porttype': 'fc',
            'portset_type': 'host',
            'replicationportsetlinkuid': 'F8C5C02FC24F019154B57B59DD753BFF',
            'state': 'present'
        }):
            svc_obj_info_mock.return_value = {
                'id': '0',
                'name': 'fcportset1',
                'type': 'host',
                'portset_type': 'host',
                'port_type': 'fc',
                'replication_portset_link_uid': '3A05584AC8EEA48B514F9C4F14A03540',
            }
            with pytest.raises(AnsibleExitJson) as exc:
                p = IBMSVCPortset()
                p.apply()
            self.assertTrue(exc.value.args[0]['changed'])
            self.assertEqual(exc.value.args[0]['msg'], "Portset (fcportset1) updated.")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_portset_with_resetreplicationportsetlinkuid(self, svc_authorize_mock, svc_run_command_mock, svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'fcportset1',
            'porttype': 'fc',
            'portset_type': 'host',
            'resetreplicationportsetlinkuid': True,
            'state': 'present'
        }):
            svc_obj_info_mock.return_value = {}
            svc_run_command_mock.return_value = {}

            with pytest.raises(AnsibleFailJson) as exc:
                p = IBMSVCPortset()
                p.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'], "Parameter resetreplicationportsetlinkuid is not supported while creating portset.")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_portset_with_autozoneenabled_autozonepolicy(self,
                                                                svc_authorize_mock,
                                                                svc_run_command_mock,
                                                                svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'porttype': 'fc',
            'portset_type': 'host',
            'ownershipgroup': 'new_owner',
            'autozoneenabled': 'yes',
            'autozonepolicy': 'one_to_one',
            'state': 'present'
        }):
            svc_obj_info_mock.side_effect = [
                # lsportset OP:
                {},
                # lssystem OP:
                {"id": "00000204AEA0632C", "name": "system0", "code_level": "9.1.3.0 (build 193.16.2602231501000)"}
            ]
            svc_run_command_mock.return_value = {
                'id': '0',
                'message': 'Portset, id [0], successfully created'
            }
            with pytest.raises(AnsibleExitJson) as exc:
                p = IBMSVCPortset()
                p.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_create_portset_on_old_version(self,
                                                   svc_authorize_mock,
                                                   svc_run_command_mock,
                                                   svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'porttype': 'fc',
            'portset_type': 'host',
            'ownershipgroup': 'new_owner',
            'autozoneenabled': 'yes',
            'autozonepolicy': 'one_to_one',
            'state': 'present'
        }):
            svc_obj_info_mock.side_effect = [
                # lsportset OP:
                {},
                # lssystem OP:
                {"id": "00000204AEA0632C", "name": "system0", "code_level": "9.1.0.0 (build 193.16.2602231501000)"}
            ]
            with pytest.raises(AnsibleFailJson) as exc:
                p = IBMSVCPortset()
                p.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'], "Parameter autozoneenabled is not supported in the current code level.")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_create_portset_with_ethernet_porttype(self,
                                                           svc_authorize_mock,
                                                           svc_run_command_mock,
                                                           svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'porttype': 'ethernet',
            'portset_type': 'host',
            'ownershipgroup': 'new_owner',
            'autozoneenabled': 'yes',
            'autozonepolicy': 'one_to_one',
            'state': 'present'
        }):
            svc_obj_info_mock.side_effect = [
                # lsportset OP:
                {},
                # lssystem OP:
                {"id": "00000204AEA0632C", "name": "system0", "code_level": "9.1.3.0 (build 193.16.2602231501000)"}
            ]
            with pytest.raises(AnsibleFailJson) as exc:
                p = IBMSVCPortset()
                p.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'], "Parameter autozoneenabled is only applicable for FC portsets.")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_create_portset_without_autozoneenabled(self,
                                                            svc_authorize_mock,
                                                            svc_run_command_mock,
                                                            svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'porttype': 'ethernet',
            'portset_type': 'host',
            'ownershipgroup': 'new_owner',
            'autozonepolicy': 'one_to_one',
            'state': 'present'
        }):
            svc_obj_info_mock.side_effect = [
                # lsportset OP:
                {},
                # lssystem OP:
                {"id": "00000204AEA0632C", "name": "system0", "code_level": "9.1.3.0 (build 193.16.2602231501000)"}
            ]
            with pytest.raises(AnsibleFailJson) as exc:
                p = IBMSVCPortset()
                p.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'], "Parameter autozonepolicy is only applicable when autozoneenabled is set to yes.")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_update_portset_with_autozoneenabled_and_autozonepolicy(self,
                                                                            svc_authorize_mock,
                                                                            svc_run_command_mock,
                                                                            svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'porttype': 'ethernet',
            'portset_type': 'replication',
            'ownershipgroup': 'new_owner',
            'autozoneenabled': 'no',
            'autozonepolicy': 'one_to_one_all_fabrics',
            'state': 'present'
        }):
            svc_obj_info_mock.side_effect = [
                # lsportset OP:
                {
                    "id": "0",
                    "name": "portset0",
                    "type": "host",
                    "port_type": "fc",
                    "port_count": "0",
                    "host_count": "0",
                    "lossless": "",
                    "owner_id": "0",
                    "owner_name": "new_owner",
                    "auto_zone_enabled": "yes",
                    "auto_zone_policy": "one_to_one"
                },
                # lssystem OP:
                {"id": "00000204AEA0632C", "name": "system0", "code_level": "9.1.3.0 (build 193.16.2602231501000)"}
            ]
            with pytest.raises(AnsibleFailJson) as exc:
                p = IBMSVCPortset()
                p.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertIn(
                "Cannot modify autozoneenabled or autozonepolicy",
                exc.value.args[0]['msg']
            )

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_portset_with_autozoneenabled_and_autozonepolicy_idempotency(self,
                                                                                svc_authorize_mock,
                                                                                svc_run_command_mock,
                                                                                svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'porttype': 'fc',
            'portset_type': 'host',
            'ownershipgroup': 'new_owner',
            'autozoneenabled': 'yes',
            'autozonepolicy': 'one_to_one',
            'state': 'present'
        }):
            svc_obj_info_mock.side_effect = [
                # lsportset OP:
                {
                    "id": "0",
                    "name": "portset0",
                    "type": "host",
                    "port_type": "fc",
                    "port_count": "0",
                    "host_count": "0",
                    "lossless": "",
                    "owner_id": "0",
                    "owner_name": "new_owner",
                    "auto_zone_enabled": "yes",
                    "auto_zone_policy": "one_to_one"
                },
                # lssystem OP:
                {"id": "00000204AEA0632C", "name": "system0", "code_level": "9.1.3.0 (build 193.16.2602231501000)"}
            ]
            with pytest.raises(AnsibleExitJson) as exc:
                p = IBMSVCPortset()
                p.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_update_portset_with_autozoneenabled_and_autozonepolicy_on_old_version(self,
                                                                                           svc_authorize_mock,
                                                                                           svc_run_command_mock,
                                                                                           svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'porttype': 'fc',
            'portset_type': 'host',
            'ownershipgroup': 'new_owner',
            'autozoneenabled': 'yes',
            'autozonepolicy': 'one_to_one',
            'state': 'present'
        }):
            svc_obj_info_mock.side_effect = [
                # lsportset OP:
                {
                    "id": "0",
                    "name": "portset0",
                    "type": "host",
                    "port_type": "fc",
                    "port_count": "0",
                    "host_count": "0",
                    "lossless": "",
                    "owner_id": "0",
                    "owner_name": "new_owner",
                    "auto_zone_enabled": "yes",
                    "auto_zone_policy": "one_to_one"
                },
                # lssystem OP:
                {"id": "00000204AEA0632C", "name": "system0", "code_level": "9.1.0.0 (build 193.16.2602231501000)"}
            ]
            with pytest.raises(AnsibleFailJson) as exc:
                p = IBMSVCPortset()
                p.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'], "Parameters autozoneenabled, autozonepolicy not supported in the current code level.")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_autozone_immutability_error(self,
                                         svc_authorize_mock,
                                         svc_obj_info_mock):
        """Test that attempting to modify autozone settings fails with proper error"""
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'porttype': 'fc',
            'autozoneenabled': 'no',  # Trying to change from 'yes' to 'no'
            'state': 'present'
        }):
            svc_obj_info_mock.side_effect = [
                # lsportset OP:
                {
                    "id": "4",
                    "name": "portset0",
                    "type": "host",
                    "port_type": "fc",
                    "port_count": "0",
                    "host_count": "0",
                    "owner_id": "0",
                    "owner_name": "new_owner",
                    "auto_zone_enabled": "yes",  # Current value
                    "auto_zone_policy": "one_to_one"
                },
                # lssystem OP:
                {"id": "00000204AEA0632C", "name": "system0", "code_level": "9.1.3.0 (build 193.16.2602231501000)"}
            ]
            with pytest.raises(AnsibleFailJson) as exc:
                p = IBMSVCPortset()
                p.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertIn('Cannot modify autozoneenabled', exc.value.args[0]['msg'])
            self.assertIn('immutable', exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_autozonepolicy_immutability_error(self,
                                               svc_authorize_mock,
                                               svc_obj_info_mock):
        """Test that attempting to modify autozonepolicy fails with proper error"""
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'portset0',
            'porttype': 'fc',
            'autozonepolicy': 'one_to_one_all_fabrics',  # Trying to change policy
            'state': 'present'
        }):
            svc_obj_info_mock.side_effect = [
                # lsportset OP:
                {
                    "id": "4",
                    "name": "portset0",
                    "type": "host",
                    "port_type": "fc",
                    "port_count": "0",
                    "host_count": "0",
                    "owner_id": "0",
                    "owner_name": "new_owner",
                    "auto_zone_enabled": "yes",
                    "auto_zone_policy": "one_to_one"  # Current value
                },
                # lssystem OP:
                {"id": "00000204AEA0632C", "name": "system0", "code_level": "9.1.3.0 (build 193.16.2602231501000)"}
            ]
            with pytest.raises(AnsibleFailJson) as exc:
                p = IBMSVCPortset()
                p.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertIn('Cannot modify', exc.value.args[0]['msg'])
            self.assertIn('immutable', exc.value.args[0]['msg'])


if __name__ == '__main__':
    unittest.main()

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_autozone_policy_without_enabled(self,
                                             svc_authorize_mock,
                                             svc_obj_info_mock):
        """Test that autozonepolicy without autozoneenabled fails"""
        set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'test_portset',
            'portset_type': 'host',
            'porttype': 'fc',
            'autozonepolicy': 'one_to_one',
            'state': 'present'
        })
        svc_obj_info_mock.return_value = {}

        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCPortset()

        self.assertTrue(exc.value.args[0]['failed'])
        self.assertIn('autozonepolicy', exc.value.args[0]['msg'].lower())

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_autozone_policy_with_disabled(self,
                                           svc_authorize_mock,
                                           svc_obj_info_mock):
        """Test that autozonepolicy with autozoneenabled=no fails"""
        set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'test_portset',
            'portset_type': 'host',
            'porttype': 'fc',
            'autozoneenabled': 'no',
            'autozonepolicy': 'one_to_one',
            'state': 'present'
        })
        svc_obj_info_mock.return_value = {}

        with pytest.raises(AnsibleFailJson) as exc:
            obj = IBMSVCPortset()

        self.assertTrue(exc.value.args[0]['failed'])
        self.assertIn('autozonepolicy', exc.value.args[0]['msg'].lower())

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_autozone_create_with_all_fabrics_policy(self,
                                                     svc_authorize_mock,
                                                     svc_obj_info_mock):
        """Test creating autozone portset with one_to_one_all_fabrics policy"""
        set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'test_portset',
            'portset_type': 'host',
            'porttype': 'fc',
            'autozoneenabled': 'yes',
            'autozonepolicy': 'one_to_one_all_fabrics',
            'state': 'present'
        })
        svc_obj_info_mock.side_effect = [
            {},
            {
                'id': '00000204AEA0632C',
                'name': 'system0',
                'code_level': '9.1.3.0 (build 193.16.2602231501000)'
            }
        ]

        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCPortset()
            obj.apply()

        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_autozone_check_mode(self,
                                 svc_authorize_mock,
                                 svc_obj_info_mock):
        """Test autozone portset creation in check mode"""
        set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'test_portset',
            'portset_type': 'host',
            'porttype': 'fc',
            'autozoneenabled': 'yes',
            'autozonepolicy': 'one_to_one',
            'state': 'present',
            '_ansible_check_mode': True
        })
        svc_obj_info_mock.side_effect = [
            {},
            {
                'id': '00000204AEA0632C',
                'name': 'system0',
                'code_level': '9.1.3.0 (build 193.16.2602231501000)'
            }
        ]

        with pytest.raises(AnsibleExitJson) as exc:
            obj = IBMSVCPortset()
            obj.apply()

        self.assertTrue(exc.value.args[0]['changed'])
