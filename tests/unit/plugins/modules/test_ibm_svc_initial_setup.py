# Copyright (C) 2020 IBM CORPORATION
# Author(s): Sanjaikumaar M <sanjaikumaar.m@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Storage Virtualize Ansible module: ibm_svc_initial_setup """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.storage_virtualize.plugins.modules.ibm_svc_initial_setup import IBMSVCInitialSetup
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


class TestIBMSVCInitialSetup(unittest.TestCase):
    """ a group of related Unit Tests"""

    def setUp(self):

        # Patch svc_authorize
        self.auth_patcher = patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi._svc_authorize')
        self.mock_auth = self.auth_patcher.start()
        self.addCleanup(self.auth_patcher.stop)

        # Patch svc_run_command
        self.run_cmd_patcher = patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi.svc_run_command')
        self.mock_run_command = self.run_cmd_patcher.start()
        self.addCleanup(self.run_cmd_patcher.stop)

        # Patch module helper
        self.mock_module_helper = patch.multiple(
            basic.AnsibleModule,
            exit_json=exit_json,
            fail_json=fail_json
        )
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

        # Initialize the object under test
        self.restapi = IBMSVCRestApi(
            self.mock_module_helper, '1.2.3.4',
            'domain.ibm.com', 'username', 'password',
            False, 'test.log', ''
        )

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_dnsserver_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_license_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    def test_missing_mandatory_params(self, system_info_mock, license_info_mock, dns_info_mock):
        """
        Missing input parameters
        """
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
        }):
            license_info_mock.return_value = {
                "license_physical_flash": "off"
            }

            svc_is = IBMSVCInitialSetup()
            with pytest.raises(AnsibleExitJson) as exc:
                svc_is.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    def test_failure_mutually_exclusive_params_1(self):
        '''
        Mutually exclusive parameters: time, ntpip
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'time': '101009142021',
            'ntpip': '9.9.9.9'
        }):
            svc_is = IBMSVCInitialSetup()
            with pytest.raises(AnsibleFailJson) as exc:
                svc_is.apply()

            self.assertTrue(exc.value.args[0]['failed'])

    def test_failure_dns_validation_1(self):
        """
        Missing required input parameter: dnsname
        """
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'dnsip': ['9.9.9.9']
        }):
            svc_is = IBMSVCInitialSetup()
            with pytest.raises(AnsibleFailJson) as exc:
                svc_is.apply()

            self.assertTrue(exc.value.args[0]['failed'])

    def test_failure_dns_validation_2(self):
        """
        Test for empty parameter value: dnsname
        """
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'dnsip': ['9.9.9.9'],
            'dnsname': []
        }):
            svc_is = IBMSVCInitialSetup()
            with pytest.raises(AnsibleFailJson) as exc:
                svc_is.apply()

            self.assertTrue(exc.value.args[0]['failed'])

    def test_failure_license_key_validation(self):
        """
        Test for empty parameter values: license_key
        """
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'license_key': ['']
        }):
            svc_is = IBMSVCInitialSetup()
            with pytest.raises(AnsibleFailJson) as exc:
                svc_is.apply()

            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_dnsserver_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_license_info')
    def test_system_update1(self, license_info_mock, dns_info_mock, system_info_mock):
        '''
        Test to update system with parameters: system_name, dns, time
        '''
        with set_module_args({
            'clustername': 'cluster_test_0',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'system_name': 'cluster_test_0',
            'time': '020411552025',
            'timezone': 200,
            'dnsname': ['test_dns3'],
            'dnsip': ['1.1.1.1']
        }):
            system_info_mock.return_value = {
                "id": "0000010023806192",
                "name": "",
                "location": "local",
                "cluster_locale": "en_US",
                "time_zone": "200 Asia/Calcutta",
                "cluster_ntp_IP_address": "",
            }

            dns_info_mock.return_value = [
                {
                    "id": "0",
                    "name": "test_dns1",
                    "type": "ipv4",
                    "IP_address": "9.20.136.11",
                    "status": "active"
                },
                {
                    "id": "1",
                    "name": "test_dns2",
                    "type": "ipv4",
                    "IP_address": "9.20.136.25",
                    "status": "active"
                }
            ]

            license_info_mock.return_value = {
                "license_physical_flash": "off",
            }

            svc_is = IBMSVCInitialSetup()
            with pytest.raises(AnsibleExitJson) as exc:
                svc_is.apply()

            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_dnsserver_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_license_info')
    def test_system_update1_idempotency(self, license_info_mock, dns_info_mock, system_info_mock):
        """
        Test to update the system with parameters, keeping the same values(idempotency): system_name, dns, and time.
        """
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'system_name': 'cluster_test_0',
            'ntpip': '9.9.9.9',
            'timezone': '200',
            'dnsname': ['test_dns'],
            'dnsip': ['1.1.1.1']
        }):
            system_info_mock.return_value = {
                "id": "0000010023806192",
                "name": "cluster_test_0",
                "location": "local",
                "cluster_locale": "en_US",
                "time_zone": "200 Asia/Calcutta",
                "cluster_ntp_IP_address": "9.9.9.9",
            }

            dns_info_mock.return_value = [
                {
                    "id": "0",
                    "name": "test_dns",
                    "type": "ipv4",
                    "IP_address": "1.1.1.1",
                    "status": "active"
                }
            ]

            license_info_mock.return_value = {
                "license_physical_flash": "off",
            }

            svc_is = IBMSVCInitialSetup()
            with pytest.raises(AnsibleExitJson) as exc:
                svc_is.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_license_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_feature_info')
    def test_license_key_update(self, license_key_info_mock, license_info_mock, system_info_mock):
        '''
        Test to update feature parameter: license_key
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'license_key': ['0123-4567-89AB-CDEF']
        }):
            system_info_mock.return_value = {
                "id": "00000204ABE10050",
                "name": "cluster_test_0",
                "time_zone": "522 UTC",
                "cluster_ntp_IP_address": "",
                "iscsi_auth_method": "none",
                "iscsi_chap_secret": "",
                "vdisk_protection_time": "15",
                "vdisk_protection_enabled": "yes",
                "product_name": "IBM Storage FlashSystem 5300",
                "flashcopy_default_grainsize": "256",
                "storage_insights_control_access": "no",
            }

            license_key_info_mock.return_value = [
                {
                    "id": "0",
                    "name": "encryption",
                    "state": "inactive",
                    "license_key": "",
                    "trial_expiration_date": "",
                    "serial_num": "",
                    "mtm": ""
                }
            ]

            license_info_mock.return_value = {
                "license_physical_flash": "off"
            }

            svc_is = IBMSVCInitialSetup()
            with pytest.raises(AnsibleExitJson) as exc:
                svc_is.apply()

            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_license_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_feature_info')
    def test_license_key_update_idempotency(self, license_key_info_mock, license_info_mock, system_info_mock):
        '''
        Test to update feature parameter, keeping the same value(idempotency): license_key
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'license_key': ['0123-4567-89AB-CDEF']
        }):
            system_info_mock.return_value = {
                "id": "00000204ABE10050",
                "name": "cluster_test_0",
                "time_zone": "522 UTC",
                "cluster_ntp_IP_address": "",
                "iscsi_auth_method": "none",
                "iscsi_chap_secret": "",
                "vdisk_protection_time": "15",
                "vdisk_protection_enabled": "yes",
                "product_name": "IBM Storage FlashSystem 5300",
                "flashcopy_default_grainsize": "256",
                "storage_insights_control_access": "no",
            }

            license_key_info_mock.return_value = [
                {
                    "id": "0",
                    "name": "encryption",
                    "state": "inactive",
                    "license_key": "0123-4567-89AB-CDEF",
                    "trial_expiration_date": "",
                    "serial_num": "",
                    "mtm": ""
                }
            ]

            license_info_mock.return_value = {
                "license_physical_flash": "off"
            }
            svc_is = IBMSVCInitialSetup()
            with pytest.raises(AnsibleExitJson) as exc:
                svc_is.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_license_info')
    def test_system_update2(self, license_info_mock, system_info_mock):
        '''
        Test to update system with parameter: timezone
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'system_name': 'cluster_test_0',
            'time': '101009142021',
            'timezone': 200,
        }):
            system_info_mock.return_value = {
                "id": "0000010023806192",
                "name": "cluster_test_0",
                "location": "local",
                "cluster_locale": "en_US",
                "time_zone": "",
                "cluster_ntp_IP_address": "",
            }

            license_info_mock.return_value = {
                "license_physical_flash": "off"
            }

            svc_is = IBMSVCInitialSetup()
            with pytest.raises(AnsibleExitJson) as exc:
                svc_is.apply()

            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_license_info')
    def test_license_update1(self, license_info_mock, system_info_mock):
        '''
        Test to update license for storwise with 'compression' parameter
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'remote': 5,
            'virtualization': 1,
            'flash': 1,
            'compression': 4,
            'cloud': 1,
            'easytier': 1,
            'physical_flash': True,
            'encryption': True
        }):
            system_info_mock.return_value = {
                "id": "0000010023806192",
                "name": "cluster_test_0",
                "location": "local",
                "cluster_locale": "en_US",
                "time_zone": "200 Asia/Calcutta",
                "cluster_ntp_IP_address": "9.9.9.9",
                "product_name": "IBM Storwize V7000"
            }

            license_info_mock.return_value = {
                "license_flash": "0",
                "license_remote": "4",
                "license_virtualization": "0",
                "license_physical_disks": "0",
                "license_physical_flash": "off",
                "license_physical_remote": "off",
                "license_compression_capacity": "4",
                "license_compression_enclosures": "5",
                "license_easy_tier": "0",
                "license_cloud_enclosures": "0"
            }

            svc_is = IBMSVCInitialSetup()
            with pytest.raises(AnsibleExitJson) as exc:
                svc_is.apply()

            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_license_info')
    def test_license_update1_idempotency(self, license_info_mock, system_info_mock):
        '''
        Test to update license for storwise with 'compression' parameter, keeping the same value(idempotency)
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'remote': 5,
            'virtualization': 1,
            'flash': 0,
            'compression': 4,
            'cloud': 0,
            'easytier': 0,
            'physical_flash': "off",
            'encryption': True
        }):
            system_info_mock.return_value = {
                "id": "0000010023806192",
                "name": "cluster_test_0",
                "location": "local",
                "cluster_locale": "en_US",
                "time_zone": "200 Asia/Calcutta",
                "cluster_ntp_IP_address": "9.9.9.9",
                "product_name": "IBM Storwize V7000"
            }

            license_info_mock.return_value = {
                "license_flash": "0",
                "license_remote": "5",
                "license_virtualization": "1",
                "license_physical_disks": "0",
                "license_physical_flash": "off",
                "license_physical_remote": "off",
                "license_compression_capacity": "0",
                "license_compression_enclosures": "4",
                "license_easy_tier": "0",
                "license_cloud_enclosures": "0"
            }

            svc_is = IBMSVCInitialSetup()
            with pytest.raises(AnsibleExitJson) as exc:
                svc_is.apply()

            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_license_info')
    def test_license_update2(self, license_info_mock, system_info_mock):
        '''
        Test to update license for SVC with 'compression' parameter
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'remote': 5,
            'virtualization': 1,
            'flash': 1,
            'compression': 4,
            'cloud': 1,
            'easytier': 1,
            'physical_flash': True,
            'encryption': True
        }):
            system_info_mock.return_value = {
                "id": "0000010023806192",
                "name": "cluster_test_0",
                "location": "local",
                "cluster_locale": "en_US",
                "time_zone": "200 Asia/Calcutta",
                "cluster_ntp_IP_address": "9.9.9.9",
                "product_name": "SVC"
            }

            license_info_mock.return_value = {
                "license_flash": "0",
                "license_remote": "4",
                "license_virtualization": "0",
                "license_physical_disks": "0",
                "license_physical_flash": "off",
                "license_physical_remote": "off",
                "license_compression_capacity": "0",
                "license_compression_enclosures": "4",
                "license_easy_tier": "0",
                "license_cloud_enclosures": "0"
            }

            svc_is = IBMSVCInitialSetup()
            with pytest.raises(AnsibleExitJson) as exc:
                svc_is.apply()

            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_license_info')
    def test_license_update2_idempotency(self, license_info_mock, system_info_mock):
        '''
        Test to update license for SVC with 'compression' parameter, keeping the same value(idempotency)
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'remote': 5,
            'virtualization': 1,
            'flash': 1,
            'compression': 4,
            'cloud': 1,
            'easytier': 1,
            'physical_flash': "on",
        }):
            system_info_mock.return_value = {
                "id": "0000010023806192",
                "name": "cluster_test_0",
                "location": "local",
                "cluster_locale": "en_US",
                "time_zone": "200 Asia/Calcutta",
                "cluster_ntp_IP_address": "9.9.9.9",
                "product_name": "SVC"
            }

            license_info_mock.return_value = {
                "license_flash": "1",
                "license_remote": "5",
                "license_virtualization": "1",
                "license_physical_disks": "0",
                "license_physical_flash": "on",
                "license_physical_remote": "off",
                "license_compression_capacity": "4",
                "license_compression_enclosures": "5",
                "license_easy_tier": "1",
                "license_cloud_enclosures": "1"
            }

            svc_is = IBMSVCInitialSetup()
            with pytest.raises(AnsibleExitJson) as exc:
                svc_is.apply()

            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_license_info')
    def test_system_update3(self, license_info_mock, system_info_mock):
        '''
        Test to update system with parameters: flashcopydefaultgrainsize, storageinsightscontrolaccess
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'flashcopydefaultgrainsize': 256,
            'storageinsightscontrolaccess': 'yes'
        }):
            system_info_mock.return_value = {
                "id": "0000010023806192",
                "name": "cluster_test_0",
                "flashcopy_default_grainsize": "64",
                "storage_insights_control_access": "no",
                "location": "local",
                "cluster_locale": "en_US",
                "time_zone": "200 Asia/Calcutta"
            }

            license_info_mock.return_value = {
                "license_physical_flash": "off",
            }

            svc_is = IBMSVCInitialSetup()
            with pytest.raises(AnsibleExitJson) as exc:
                svc_is.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_license_info')
    def test_system_update3_idempotency(self, license_info_mock, system_info_mock):
        """
        Test to update the system with parameters, keeping the same values(idempotency): flashcopydefaultgrainsize, storageinsightscontrolaccess
        """
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'flashcopydefaultgrainsize': 256,
            'storageinsightscontrolaccess': 'yes'
        }):
            system_info_mock.return_value = {
                "id": "0000010023806192",
                "name": "cluster_test_0",
                "flashcopy_default_grainsize": "256",
                "storage_insights_control_access": "yes",
                "location": "local",
                "cluster_locale": "en_US",
                "time_zone": "200 Asia/Calcutta"
            }

            license_info_mock.return_value = {
                "license_physical_flash": "off",
            }

            svc_is = IBMSVCInitialSetup()
            with pytest.raises(AnsibleExitJson) as exc:
                svc_is.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_license_info')
    def test_system_update4(self, license_info_mock, system_info_mock):
        """
        Test to update the system with parameters: vdiskprotectiontime, vdiskprotectionenabled
        """
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'vdiskprotectiontime': 20,
            'vdiskprotectionenabled': 'yes',
        }):
            system_info_mock.return_value = {
                "id": "0000010023806192",
                "name": "cluster_test_0",
                "storage_insights_control_access": "no",
                "location": "local",
                "cluster_locale": "en_US",
                "time_zone": "200 Asia/Calcutta",
                'vdisk_protection_time': 15,
                'vdisk_protection_enabled': 'no',
            }

            license_info_mock.return_value = {
                "license_physical_flash": "off",
            }

            svc_is = IBMSVCInitialSetup()
            with pytest.raises(AnsibleExitJson) as exc:
                svc_is.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_license_info')
    def test_system_update4_idempotency(self, license_info_mock, system_info_mock):
        """
        Test to update the system with parameters, keeping the same values(idempotency): vdiskprotectiontime, vdiskprotectionenabled
        """
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'vdiskprotectiontime': 15,
            'vdiskprotectionenabled': 'no',
        }):
            system_info_mock.return_value = {
                "id": "0000010023806192",
                "name": "cluster_test_0",
                'vdisk_protection_time': 15,
                'vdisk_protection_enabled': 'no',
            }

            license_info_mock.return_value = {
                "license_physical_flash": "off",
            }

            svc_is = IBMSVCInitialSetup()
            with pytest.raises(AnsibleExitJson) as exc:
                svc_is.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_license_info')
    def test_system_update5(self, license_info_mock, system_info_mock):
        """
        Test to update the system with parameters: iscsiauthmethod, chapsecret
        """
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'iscsiauthmethod' : 'chap',
            'chapsecret': 'test1'
        }):
            system_info_mock.return_value = {
                "id": "0000010023806192",
                "name": "cluster_test_0",
                'iscsi_auth_method' : 'none',
                'iscsi_chap_secret' : ''
            }

            license_info_mock.return_value = {
                "license_physical_flash": "off",
            }

            svc_is = IBMSVCInitialSetup()
            with pytest.raises(AnsibleExitJson) as exc:
                svc_is.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_license_info')
    def test_system_update5_idempotency(self, license_info_mock, system_info_mock):
        """
        Test to update the system with parameters, keeping the same values(idempotency): iscsiauthmethod, chapsecret
        """
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'iscsiauthmethod' : 'chap',
            'chapsecret': 'test1'
        }):
            system_info_mock.return_value = {
                "id": "0000010023806192",
                "name": "cluster_test_0",
                'iscsi_auth_method' : 'chap',
                'iscsi_chap_secret' : 'test1'
            }

            license_info_mock.return_value = {
                "license_physical_flash": "off",
            }

            svc_is = IBMSVCInitialSetup()
            with pytest.raises(AnsibleExitJson) as exc:
                svc_is.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_system_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_initial_setup.IBMSVCInitialSetup.get_license_info')
    def test_system_update6(self, license_info_mock, system_info_mock):
        """
        Test to update the system with parameters: iscsiauthmethod, chapsecret
        """
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'iscsiauthmethod' : 'none',
            'chapsecret': ''
        }):
            system_info_mock.return_value = {
                "id": "0000010023806192",
                "name": "cluster_test_0",
                'iscsi_auth_method' : 'chap',
                'iscsi_chap_secret' : 'test1'
            }

            license_info_mock.return_value = {
                "license_physical_flash": "off",
            }

            svc_is = IBMSVCInitialSetup()
            with pytest.raises(AnsibleExitJson) as exc:
                svc_is.apply()
            self.assertTrue(exc.value.args[0]['changed'])


if __name__ == '__main__':
    unittest.main()
