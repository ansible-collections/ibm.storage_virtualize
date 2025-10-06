# Copyright (C) 2022 IBM CORPORATION
# Author(s): Sreshtant Bohidar <sreshtant.bohidar@ibm.com>
#            Rahul Pawar <rahul.p@ibm.com>
#            Aditya Bhosale <adityabhosale@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Storage Virtualize Ansible module: ibm_svc_usergroup """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.storage_virtualize.plugins.modules.ibm_svc_manage_ip import IBMSVCIp
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


class TestIBMSVCUser(unittest.TestCase):
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
                IBMSVCIp()
            print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_basic_checks(self, mock_svc_authorize):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'node': 'node1',
            'port': 1,
            'portset': 0,
            'ip_address': '10.0.1.1',
            'subnet_prefix': 20,
            'gateway': '10.10.10.10',
            'vlan': 1,
            'shareip': True,
            'state': 'present'
        }):
            ip = IBMSVCIp()
            data = ip.basic_checks()
            self.assertEqual(data, None)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_ip_info(self, mock_svc_authorize, svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'node': 'node1',
            'port': 1,
            'portset': 'portset0',
            'ip_address': '10.0.1.1',
            'subnet_prefix': 20,
            'gateway': '10.10.10.10',
            'vlan': 1,
            'shareip': True,
            'state': 'present'
        }):
            svc_obj_info_mock.return_value = [
                {
                    "id": "0",
                    "node_id": "1",
                    "node_name": "node1",
                    "port_id": "1",
                    "portset_id": "0",
                    "portset_name": "portset0",
                    "IP_address": "10.0.1.1",
                    "prefix": "20",
                    "vlan": "",
                    "gateway": "",
                },
                {
                    "id": "1",
                    "node_id": "1",
                    "node_name": "node1",
                    "port_id": "1",
                    "portset_id": "1",
                    "portset_name": "portset1",
                    "IP_address": "10.0.1.2",
                    "prefix": "20",
                    "vlan": "",
                    "gateway": "",
                }
            ]
            ip = IBMSVCIp()
            data = ip.get_ip_info("10.0.1.1")
            self.assertEqual(data["IP_address"], "10.0.1.1")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_ip(self, mock_svc_authorize, svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'node': 'node1',
            'port': 1,
            'portset': 0,
            'ip_address': '10.0.1.1',
            'subnet_prefix': 20,
            'gateway': '10.10.10.10',
            'vlan': 1,
            'shareip': True,
            'state': 'present'
        }):
            svc_run_command_mock.return_value = {
                'id': '0',
                'message': 'IP Address, id [0], successfully created'
            }
            ip = IBMSVCIp()
            data = ip.create_ip()
            self.assertEqual(data, None)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_ip_when_port_portset_node_absent(self, mock_svc_authorize, svc_obj_info_mock, svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'ip_address': '10.0.1.1',
            'subnet_prefix': 20,
            'gateway': '10.10.10.10',
            'vlan': 1,
            'shareip': True,
            'state': 'present'
        }):
            svc_run_command_mock.return_value = {
                'id': '0',
                'message': 'IP Address, id [0], successfully created'
            }
            with pytest.raises(AnsibleExitJson) as exc:
                ip = IBMSVCIp()
                ip.apply()
                self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_change_ip_with_valid_param(self, mock_svc_authorize, svc_obj_info_mock, svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'old_ip_address': '10.1.1.11',
            'ip_address': '10.1.1.12',
            'subnet_prefix': 24,
            'gateway': '10.1.1.1',
            'vlan': 1,
            'state': 'present',
        }):
            svc_obj_info_mock.return_value = [{
                'id': '1',
                'node_id': '1',
                'node_name': 'node1',
                'port_id': '2',
                'portset_id': '0',
                'portset_name': 'portset0',
                'IP_address': '10.1.1.11',
                'prefix': '24',
                'vlan': '',
                'gateway': '',
                'owner_id': '',
                'owner_name': ''
            }]
            with pytest.raises(AnsibleExitJson) as exc:
                v = IBMSVCIp()
                v.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_change_prefix(self, mock_svc_authorize, svc_obj_info_mock, svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'ip_address': '10.1.1.11',
            'subnet_prefix': 28,
            'state': 'present',
        }):
            svc_obj_info_mock.return_value = [{
                'id': '1',
                'node_id': '1',
                'node_name': 'node1',
                'port_id': '2',
                'portset_id': '0',
                'portset_name': 'portset0',
                'IP_address': '10.1.1.11',
                'prefix': '24',
                'vlan': '',
                'gateway': '',
                'owner_id': '',
                'owner_name': ''
            }]
            with pytest.raises(AnsibleExitJson) as exc:
                v = IBMSVCIp()
                v.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_reset_gateway_vlan(self, mock_svc_authorize, svc_obj_info_mock, svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'ip_address': '10.1.1.11',
            'subnet_prefix': 24,
            'state': 'present',
            'resetgateway': True,
            'resetvlan': True
        }):
            svc_obj_info_mock.return_value = [{
                'id': '1',
                'node_id': '1',
                'node_name': 'node1',
                'port_id': '2',
                'portset_id': '0',
                'portset_name': 'portset0',
                'IP_address': '10.1.1.11',
                'prefix': '24',
                'vlan': '60',
                'gateway': '10.1.1.1',
                'owner_id': '',
                'owner_name': ''
            }]
            with pytest.raises(AnsibleExitJson) as exc:
                v = IBMSVCIp()
                v.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_gateway_vlan(self, mock_svc_authorize, svc_obj_info_mock, svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'ip_address': '10.1.1.11',
            'subnet_prefix': 24,
            'state': 'present',
            'gateway': '10.1.1.2',
            'vlan': 70
        }):
            svc_obj_info_mock.return_value = [{
                'id': '1',
                'node_id': '1',
                'node_name': 'node1',
                'port_id': '2',
                'portset_id': '0',
                'portset_name': 'portset0',
                'IP_address': '10.1.1.11',
                'prefix': '24',
                'vlan': '60',
                'gateway': '10.1.1.1',
                'owner_id': '',
                'owner_name': ''
            }]
            with pytest.raises(AnsibleExitJson) as exc:
                v = IBMSVCIp()
                v.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_update_portset(self, mock_svc_authorize, svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'ip_address': '1.1.1.11',
            'subnet_prefix': 24,
            'node': 'node1',
            'port': 2,
            'portset': 'test_data2',
            'state': 'present'
        }):
            svc_obj_info_mock.return_value = [{
                'id': '1',
                'node_id': '1',
                'node_name': 'node1',
                'port_id': '2',
                'portset_id': '0',
                'portset_name': 'portset0',
                'IP_address': '1.1.1.11',
                'prefix': '24',
                'vlan': '60',
                'gateway': '1.1.1.1',
                'owner_id': '',
                'owner_name': ''
            }]
            with pytest.raises(AnsibleFailJson) as exc:
                v = IBMSVCIp()
                v.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(
                exc.value.args[0]['msg'],
                "IP 1.1.1.11 already exists. Portset cannot be changed. To create shared data IP, use shareip parameter."
            )

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_update_node_port(self, mock_svc_authorize, svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'ip_address': '1.1.1.11',
            'subnet_prefix': 24,
            'node': 'node2',
            'port': 3,
            'portset': 'portset0',
            'state': 'present'
        }):
            svc_obj_info_mock.return_value = [{
                'id': '1',
                'node_id': '1',
                'node_name': 'node1',
                'port_id': '2',
                'portset_id': '0',
                'portset_name': 'portset0',
                'IP_address': '1.1.1.11',
                'prefix': '24',
                'vlan': '60',
                'gateway': '1.1.1.1',
                'owner_id': '',
                'owner_name': ''
            }]
            with pytest.raises(AnsibleFailJson) as exc:
                v = IBMSVCIp()
                v.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(
                exc.value.args[0]['msg'],
                "Update is not supported for parameter(s): node, port"
            )

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_ip_with_invalid_param(self, mock_svc_authorize, svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'ip_address': '1.1.1.2',
            'node': 'node1',
            'port': 1,
            'subnet_prefix': 20,
            'gateway': '10.10.10.10',
            'vlan': 1,
            'shareip': True,
            'state': 'absent'
        }):
            svc_obj_info_mock.return_value = [
                {"id": "0", "IP_address": "1.1.1.1"},
                {"id": "1", "IP_address": "1.1.1.2"}
            ]
            with pytest.raises(AnsibleFailJson) as exc:
                v = IBMSVCIp()
                v.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(
                exc.value.args[0]['msg'],
                "The parameter ['subnet_prefix', 'gateway', 'vlan', 'shareip', 'node', 'port'] are not applicable when state is absent."
            )

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_deletion_when_multiple_IP_detected(self, mock_svc_authorize, svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'ip_address': '1.1.1.1',
            'state': 'absent'
        }):
            svc_obj_info_mock.return_value = [
                {"id": "0", "IP_address": "1.1.1.1", "portset_id": "0", "portset_name": "data_portset0"},
                {"id": "1", "IP_address": "1.1.1.1", "portset_id": "1", "portset_name": "data_portset1"},
                {"id": "2", "IP_address": "1.1.1.2", "portset_id": "2", "portset_name": "mgmt_portset0"}
            ]
            with pytest.raises(AnsibleFailJson) as exc:
                v = IBMSVCIp()
                v.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(
                exc.value.args[0]['msg'],
                "Multiple objects found with IP 1.1.1.1. Please specify portset."
            )

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_ip_address(self, mock_svc_authorize, svc_obj_info_mock, svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'ip_address': '1.1.1.2',
            'state': 'absent'
        }):
            svc_obj_info_mock.return_value = [
                {"id": "0", "IP_address": "1.1.1.1"},
                {"id": "1", "IP_address": "1.1.1.2"}
            ]
            with pytest.raises(AnsibleExitJson) as exc:
                v = IBMSVCIp()
                v.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_ip_address_with_portset(self, mock_svc_authorize, svc_obj_info_mock, svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'ip_address': '1.1.1.1',
            'portset': 'data_portset1',
            'state': 'absent'
        }):
            svc_obj_info_mock.return_value = [
                {"id": "0", "IP_address": "1.1.1.1", "portset_id": "0", "portset_name": "data_portset0"},
                {"id": "1", "IP_address": "1.1.1.1", "portset_id": "1", "portset_name": "data_portset1"},
                {"id": "2", "IP_address": "1.1.1.2", "portset_id": "2", "portset_name": "mgmt_portset0"}
            ]
            with pytest.raises(AnsibleExitJson) as exc:
                v = IBMSVCIp()
                v.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_ip_address_with_portset_idempotency(self, mock_svc_authorize, svc_obj_info_mock, svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'ip_address': '1.1.1.1',
            'portset': 'data_portset1',
            'state': 'absent'
        }):
            svc_obj_info_mock.return_value = [
                {"id": "0", "IP_address": "1.1.1.1", "portset_id": "0", "portset_name": "data_portset0"}
            ]
            with pytest.raises(AnsibleExitJson) as exc:
                v = IBMSVCIp()
                v.apply()
            self.assertFalse(exc.value.args[0]['changed'])


if __name__ == '__main__':
    unittest.main()
