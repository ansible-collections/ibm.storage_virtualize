# Copyright (C) 2023 IBM CORPORATION
# Author(s): Sanjaikumaar M <sanjaikumaar.m@ibm.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Storage Virtualize Ansible module: ibm_sv_manage_fc_partnership """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.storage_virtualize.plugins.modules.ibm_sv_manage_fc_partnership import IBMSVFCPartnership


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


class TestIBMSVFCPartnership(unittest.TestCase):
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'remote_system': 'cluster_A'
        })

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVFCPartnership()
        self.assertTrue(exc.value.args[0]['failed'])

    def test_missing_mandatory_parameter(self):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'state': 'present'
        })

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVFCPartnership()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_fc_partnership(self, svc_authorize_mock,
                                   svc_obj_info_mock,
                                   svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'remote_clustername',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password',
            'remote_system': 'cluster_A',
            'linkbandwidthmbits': 20,
            'backgroundcopyrate': 50,
            'start': True,
            'state': 'present'
        })

        svc_obj_info_mock.side_effect = [
            {'id': '0123456789'},  # lssystem mock object
            {},  # lspartnership mock object
            {}  # lspartnership mock object
        ]

        with pytest.raises(AnsibleExitJson) as exc:
            fc = IBMSVFCPartnership()
            fc.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_create_fc_partnership_invalid_params(self, svc_authorize_mock,
                                                          svc_obj_info_mock):
        """
        Following parameters not supported during creation: stop
        """
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'remote_clustername',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password',
            'remote_system': 'cluster_A',
            'linkbandwidthmbits': 20,
            'backgroundcopyrate': 50,
            'stop': True,
            'state': 'present',
            'pbrinuse': 'yes'
        })

        svc_obj_info_mock.side_effect = [
            {'id': '0123456789'},  # lssystem mock object
            {}  # lspartnership mock object
        ]

        with pytest.raises(AnsibleFailJson) as exc:
            fc = IBMSVFCPartnership()
            fc.apply()
        self.assertTrue(exc.value.args[0]['failed'])
        self.assertEqual(exc.value.args[0]['msg'], 'Following parameters not supported during creation: stop, pbrinuse')

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_fc_partnership_idempotency(self, svc_authorize_mock,
                                               svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'remote_clustername',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password',
            'remote_system': 'cluster_A',
            'linkbandwidthmbits': 20,
            'backgroundcopyrate': 50,
            'state': 'present'
        })

        svc_obj_info_mock.side_effect = [
            {'id': '0123456789'},  # lssystem mock object
            {'id': 0, 'link_bandwidth_mbits': '20', 'background_copy_rate': '50'},  # lspartnership mock object
            {'id': 0, 'link_bandwidth_mbits': '20', 'background_copy_rate': '50'}  # lspartnership mock object
        ]

        with pytest.raises(AnsibleExitJson) as exc:
            fc = IBMSVFCPartnership()
            fc.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_fc_partnership_two_systems(self, svc_authorize_mock,
                                               svc_obj_info_mock,
                                               svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'remote_clustername',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password',
            'remote_system': 'cluster_A',
            'linkbandwidthmbits': 30,
            'backgroundcopyrate': 60,
            'state': 'present',
            'pbrinuse': 'yes'
        })

        svc_obj_info_mock.side_effect = [
            {'id': '0123456789'},  # lssystem mock object
            {'id': 0, 'link_bandwidth_mbits': '20', 'background_copy_rate': '50', 'pbr_in_use': 'no'},  # lspartnership mock object
            {'id': 0, 'link_bandwidth_mbits': '20', 'background_copy_rate': '50', 'pbr_in_use': 'no'}  # lspartnership mock object
        ]

        with pytest.raises(AnsibleExitJson) as exc:
            fc = IBMSVFCPartnership()
            fc.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_fc_partnership_two_systems_idempotency(self, svc_authorize_mock,
                                                           svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'remote_clustername',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password',
            'remote_system': 'cluster_A',
            'linkbandwidthmbits': 30,
            'backgroundcopyrate': 60,
            'state': 'present',
            'pbrinuse': 'yes'
        })

        svc_obj_info_mock.side_effect = [
            {'id': '0123456789'},  # lssystem mock object
            {'id': 0, 'link_bandwidth_mbits': '30', 'background_copy_rate': '60', 'pbr_in_use': 'yes'},  # lspartnership mock object
            {'id': 0, 'link_bandwidth_mbits': '30', 'background_copy_rate': '60', 'pbr_in_use': 'yes'}  # lspartnership mock object
        ]

        with pytest.raises(AnsibleExitJson) as exc:
            fc = IBMSVFCPartnership()
            fc.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_fc_partnership_one_system(self, svc_authorize_mock,
                                              svc_obj_info_mock,
                                              svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'remote_system': 'cluster_A',
            'linkbandwidthmbits': 30,
            'backgroundcopyrate': 60,
            'state': 'present',
            'pbrinuse': 'yes'
        })

        svc_obj_info_mock.side_effect = [
            {'id': 0, 'link_bandwidth_mbits': '20', 'background_copy_rate': '50', 'pbr_in_use': 'no'}  # lspartnership mock object
        ]

        with pytest.raises(AnsibleExitJson) as exc:
            fc = IBMSVFCPartnership()
            fc.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_fc_partnership_one_system_idempotency(self, svc_authorize_mock,
                                                          svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'remote_system': 'cluster_A',
            'linkbandwidthmbits': 30,
            'backgroundcopyrate': 60,
            'state': 'present',
            'pbrinuse': 'yes'
        })

        svc_obj_info_mock.side_effect = [
            {'id': 0, 'link_bandwidth_mbits': '30', 'background_copy_rate': '60', 'pbr_in_use': 'yes'},  # lspartnership mock object
            {'id': 0, 'link_bandwidth_mbits': '30', 'background_copy_rate': '60', 'pbr_in_use': 'yes'}  # lspartnership mock object
        ]

        with pytest.raises(AnsibleExitJson) as exc:
            fc = IBMSVFCPartnership()
            fc.apply()
        self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_stop_fc_partnership(self, svc_authorize_mock,
                                 svc_obj_info_mock,
                                 svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'remote_clustername',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password',
            'remote_system': 'cluster_A',
            'stop': True,
            'state': 'present'
        })

        svc_obj_info_mock.side_effect = [
            {'id': '0123456789'},  # lssystem mock object
            {'id': 0, 'link_bandwidth_mbits': '20', 'background_copy_rate': '50'},  # lspartnership mock object
            {'id': 0, 'link_bandwidth_mbits': '20', 'background_copy_rate': '50'}  # lspartnership mock object
        ]

        with pytest.raises(AnsibleExitJson) as exc:
            fc = IBMSVFCPartnership()
            fc.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_stop_fc_partnership_idempotency(self, svc_authorize_mock,
                                             svc_obj_info_mock,
                                             svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'remote_clustername',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password',
            'remote_system': 'cluster_A',
            'stop': True,
            'state': 'present'
        })

        svc_obj_info_mock.side_effect = [
            {'id': '0123456789'},  # lssystem mock object
            {'id': 0, 'link_bandwidth_mbits': '20', 'background_copy_rate': '50'},  # lspartnership mock object
            {'id': 0, 'link_bandwidth_mbits': '20', 'background_copy_rate': '50'}  # lspartnership mock object
        ]

        with pytest.raises(AnsibleExitJson) as exc:
            fc = IBMSVFCPartnership()
            fc.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_fc_partnership(self, svc_authorize_mock,
                                   svc_obj_info_mock,
                                   svc_run_command_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'remote_clustername',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password',
            'remote_system': 'cluster_A',
            'state': 'absent'
        })

        svc_obj_info_mock.side_effect = [
            {'id': '0123456789'},  # lssystem mock object
            {'id': 0, 'link_bandwidth_mbits': '20', 'background_copy_rate': '50'},  # lspartnership mock object
            {'id': 0, 'link_bandwidth_mbits': '20', 'background_copy_rate': '50'}  # lspartnership mock object
        ]

        with pytest.raises(AnsibleExitJson) as exc:
            fc = IBMSVFCPartnership()
            fc.apply()
        self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_delete_fc_partnership_pbr(self, svc_authorize_mock,
                                               svc_obj_info_mock):
        """
        Following parameters not supported during deletion: pbrinuse
        """
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'remote_clustername',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password',
            'remote_system': 'cluster_A',
            'state': 'absent',
            'pbrinuse': 'yes'
        })

        svc_obj_info_mock.side_effect = [
            {'id': '0123456789'},  # lssystem mock object
            {'id': 0, 'link_bandwidth_mbits': '20', 'background_copy_rate': '50'}  # lspartnership mock object
        ]

        with pytest.raises(AnsibleFailJson) as exc:
            fc = IBMSVFCPartnership()
            fc.apply()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_fc_partnership_idempotency(self, svc_authorize_mock,
                                               svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'remote_clustername': 'remote_clustername',
            'remote_username': 'remote_username',
            'remote_password': 'remote_password',
            'remote_system': 'cluster_A',
            'state': 'absent'
        })

        svc_obj_info_mock.side_effect = [
            {'id': '0123456789'},  # lssystem mock object
            {},  # lspartnership mock object
            {}  # lspartnership mock object
        ]

        with pytest.raises(AnsibleExitJson) as exc:
            fc = IBMSVFCPartnership()
            fc.apply()
        self.assertFalse(exc.value.args[0]['changed'])


if __name__ == '__main__':
    unittest.main()
