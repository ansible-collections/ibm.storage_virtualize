# Copyright (C) 2020 IBM CORPORATION
# Author(s): Peng Wang <wangpww@cn.ibm.com>
#            Sreshtant Bohidar <sreshtant.bohidar@ibm.com>
#            Sudheesh Reddy Satti<Sudheesh.Reddy.Satti@ibm.com>
#            Sandip Gulab Rajbanshi <sandip.rajbanshi@ibm.com>
#            Rahul Pawar <rahul.p@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Storage Virtualize Ansible module: ibm_svc_host """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.storage_virtualize.plugins.modules.ibm_svc_host import IBMSVChost
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


class TestIBMSVChost(unittest.TestCase):
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
        self.existing_fcwwpn = []

    def set_default_args(self):
        return dict({
            'name': 'test',
            'state': 'present'
        })

    def test_module_fail_when_required_args_missing(self):
        """ required arguments are reported as errors """
        with set_module_args({}):
            with pytest.raises(AnsibleFailJson) as exc:
                IBMSVChost()
            print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_host(self, svc_authorize_mock, svc_obj_info_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
        }):
            host_ret = [{"id": "1", "name": "ansible_host", "port_count": "1",
                         "iogrp_count": "4", "status": "offline",
                         "site_id": "", "site_name": "",
                         "host_cluster_id": "", "host_cluster_name": "",
                         "protocol": "scsi", "owner_id": "",
                         "owner_name": ""}]
            svc_obj_info_mock.return_value = host_ret
            host = IBMSVChost().get_existing_host('ansible_host')
            self.assertEqual('ansible_host', host['name'])
            self.assertEqual('1', host['id'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_create_get_existing_host_called(self, svc_authorize_mock,
                                                  get_existing_host_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_host',
        }):
            get_existing_host_mock.return_value = [1]
            host_created = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                host_created.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.host_probe')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_host_but_host_existed(self, svc_authorize_mock,
                                          host_probe_mock,
                                          get_existing_host_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
        }):
            host_ret = [{"id": "1", "name": "ansible_host", "port_count": "1",
                         "iogrp_count": "4", "status": "offline",
                         "site_id": "", "site_name": "",
                         "host_cluster_id": "", "host_cluster_name": "",
                         "protocol": "scsi", "owner_id": "",
                         "owner_name": ""}]
            get_existing_host_mock.return_value = host_ret
            host_probe_mock.return_value = []
            host_created = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                host_created.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.host_create')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_host_successfully(self, svc_authorize_mock,
                                      host_create_mock,
                                      get_existing_host_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'fcwwpn': '100000109B570216'
        }):
            host = {u'message': u'Host, id [14], '
                                u'successfully created', u'id': u'14'}
            host_create_mock.return_value = host
            get_existing_host_mock.return_value = []
            host_created = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                host_created.apply()

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_host_failed_since_missed_required_param(
            self, svc_authorize_mock, get_existing_host_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
        }):
            get_existing_host_mock.return_value = []
            host_created = IBMSVChost()
            with pytest.raises(AnsibleFailJson) as exc:
                host_created.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_host_but_host_not_existed(self, svc_authorize_mock,
                                              get_existing_host_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
        }):
            get_existing_host_mock.return_value = []
            host_deleted = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                host_deleted.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.host_delete')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_host_successfully(self, svc_authorize_mock,
                                      host_delete_mock,
                                      get_existing_host_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
        }):
            host_ret = [{"id": "1", "name": "ansible_host", "port_count": "1",
                         "iogrp_count": "4", "status": "offline",
                         "site_id": "", "site_name": "",
                         "host_cluster_id": "", "host_cluster_name": "",
                         "protocol": "scsi", "owner_id": "",
                         "owner_name": ""}]
            get_existing_host_mock.return_value = host_ret
            host_deleted = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                host_deleted.apply()

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.host_fcwwpn_update')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_fcwwpn_update_when_existing_absent(self, svc_authorize_mock, get_existing_host_mock, host_fcwwpn_update_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'fcwwpn': '1000001AA0570262',
            'protocol': 'scsi',
            'type': 'generic'
        }):
            lshost_data = {'id': '24', 'name': 'test', 'port_count': '5', 'type': 'generic',
                           'mask': '1111111', 'iogrp_count': '4', 'status': 'offline',
                           'site_id': '', 'site_name': '', 'host_cluster_id': '', 'host_cluster_name': '',
                           'protocol': 'scsi', 'nodes': [{'WWPN': '1000001AA0570260', 'node_logged_in_count': '0', 'state': 'online'},
                                                         {'WWPN': '1000001AA0570261', 'node_logged_in_count': '0', 'state': 'online'},
                                                         {'WWPN': '1000001AA0570262', 'node_logged_in_count': '0', 'state': 'online'}]}
            get_existing_host_mock.return_value = lshost_data
            host_created = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                host_created.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.host_fcwwpn_update')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_fcwwpn_update_when_new_added(self, svc_authorize_mock, get_existing_host_mock, host_fcwwpn_update_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'fcwwpn': '1000001AA0570260:1000001AA0570261:1000001AA0570262:1000001AA0570264',
            'protocol': 'scsi',
            'type': 'generic'
        }):
            lshost_data = {'id': '24', 'name': 'test', 'port_count': '5', 'type': 'generic',
                           'mask': '1111111', 'iogrp_count': '4', 'status': 'offline',
                           'site_id': '', 'site_name': '', 'host_cluster_id': '', 'host_cluster_name': '',
                           'protocol': 'scsi', 'nodes': [{'WWPN': '1000001AA0570260', 'node_logged_in_count': '0', 'state': 'online'},
                                                         {'WWPN': '1000001AA0570261', 'node_logged_in_count': '0', 'state': 'online'},
                                                         {'WWPN': '1000001AA0570262', 'node_logged_in_count': '0', 'state': 'online'}]}
            get_existing_host_mock.return_value = lshost_data
            host_created = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                host_created.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.host_fcwwpn_update')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_fcwwpn_update_when_existing_removed_and_new_added(self, svc_authorize_mock, get_existing_host_mock, host_fcwwpn_update_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'fcwwpn': '1000001AA0570264:1000001AA0570265:1000001AA0570266',
            'protocol': 'scsi',
            'type': 'generic'
        }):
            lshost_data = {'id': '24', 'name': 'test', 'port_count': '5', 'type': 'generic',
                           'mask': '1111111', 'iogrp_count': '4', 'status': 'offline',
                           'site_id': '', 'site_name': '', 'host_cluster_id': '', 'host_cluster_name': '',
                           'protocol': 'scsi', 'nodes': [{'WWPN': '1000001AA0570260', 'node_logged_in_count': '0', 'state': 'online'},
                                                         {'WWPN': '1000001AA0570261', 'node_logged_in_count': '0', 'state': 'online'},
                                                         {'WWPN': '1000001AA0570262', 'node_logged_in_count': '0', 'state': 'online'}]}
            get_existing_host_mock.return_value = lshost_data
            host_created = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                host_created.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_iogrp_update_when_existing_removed_and_new_added(self, svc_authorize_mock, svc_obj_info_mock, svc_run_command_mock):
        """
        Tests IO group update by adding some new IO groups and removing some existing ones
        """
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'iogrp': '1:2:3',
            'protocol': 'scsi',
            'type': 'generic'
        }):
            svc_obj_info_mock.side_effect = [
                {
                    "id": "2", "name": "test", "port_count": "1", "type": "generic", "iogrp_count": "3", "status": "degraded",
                    "site_id": "", "site_name": "", "host_cluster_id": "", "host_cluster_name": "", "protocol": "scsi",
                    "status_policy": "redundant", "status_site": "all", "io_activity_status": "inactive", "discovery_status": "offline",
                    "nodes": [{"WWPN": "10000090FAA0BA49", "node_logged_in_count": "1", "state": "inactive"}], "owner_id": "",
                    "owner_name": "", "portset_id": "64", "portset_name": "portset64", "partition_id": "", "partition_name": "",
                    "location1_status": "", "location2_status": "", "draft_partition_id": "", "draft_partition_name": "",
                    "ungrouped_volume_mapping": "no", "auto_storage_discovery": "no", "location_system_name": "", "auth_method": "",
                    "host_username": "", "storage_username": "", "host_secret": "no", "storage_secret": "no", "offline_alert_suppressed": "no"
                },
                [
                    {"id": "0", "name": "io_grp0"},
                    {"id": "1", "name": "io_grp1"},
                    {"id": "2", "name": "io_grp2"},
                    {"id": "3", "name": "io_grp3"},
                    {"id": "4", "name": "recovery_io_grp"}
                ],
                [
                    {"id": "0", "name": "io_grp0"},
                    {"id": "1", "name": "io_grp1"},
                    {"id": "2", "name": "io_grp2"}
                ]
            ]
            host_created = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                host_created.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_iogrp_update_when_existing_removed_and_new_added_idempotency(self, svc_authorize_mock, svc_obj_info_mock, svc_run_command_mock):
        """
        Tests IO group update idempotency by assigning same IO groups as existing host IO group configuration
        """
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'iogrp': '0:io_grp1:io_grp2',
            'protocol': 'scsi',
            'type': 'generic'
        }):
            svc_obj_info_mock.side_effect = [
                {
                    "id": "2", "name": "test", "port_count": "1", "type": "generic", "iogrp_count": "3", "status": "degraded",
                    "site_id": "", "site_name": "", "host_cluster_id": "", "host_cluster_name": "", "protocol": "scsi",
                    "status_policy": "redundant", "status_site": "all", "io_activity_status": "inactive", "discovery_status": "offline",
                    "nodes": [{"WWPN": "10000090FAA0BA49", "node_logged_in_count": "1", "state": "inactive"}], "owner_id": "",
                    "owner_name": "", "portset_id": "64", "portset_name": "portset64", "partition_id": "", "partition_name": "",
                    "location1_status": "", "location2_status": "", "draft_partition_id": "", "draft_partition_name": "",
                    "ungrouped_volume_mapping": "no", "auto_storage_discovery": "no", "location_system_name": "", "auth_method": "",
                    "host_username": "", "storage_username": "", "host_secret": "no", "storage_secret": "no", "offline_alert_suppressed": "no"
                },
                [
                    {"id": "0", "name": "io_grp0"},
                    {"id": "1", "name": "io_grp1"},
                    {"id": "2", "name": "io_grp2"},
                    {"id": "3", "name": "io_grp3"},
                    {"id": "4", "name": "recovery_io_grp"}
                ],
                [
                    {"id": "0", "name": "io_grp0"},
                    {"id": "1", "name": "io_grp1"},
                    {"id": "2", "name": "io_grp2"}
                ]
            ]
            host_created = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                host_created.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_fcwwpn_update(self, svc_authorize_mock, svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'fcwwpn': '1000001AA0570264:1000001AA0570265:1000001AA0570266',
            'protocol': 'scsi',
            'type': 'generic'
        }):
            obj = IBMSVChost()
            obj.existing_fcwwpn = ['1000001AA0570262', '1000001AA0570263', '1000001AA0570264']
            obj.input_fcwwpn = ['1000001AA0570264', '1000001AA0570265', '1000001AA0570266']
            self.assertEqual(obj.host_fcwwpn_update(None), None)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_site_update(self, svc_authorize_mock, svc_obj_info_mock, src):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'fcwwpn': '1000001AA0570260:1000001AA0570261:1000001AA0570262',
            'protocol': 'scsi',
            'type': 'generic',
            'site': 'site1'
        }):
            svc_obj_info_mock.return_value = {
                'id': '24', 'name': 'test', 'port_count': '5', 'type': 'generic',
                'mask': '1111111', 'iogrp_count': '4', 'status': 'offline',
                'site_id': '', 'site_name': 'site2', 'host_cluster_id': '', 'host_cluster_name': '',
                'protocol': 'scsi', 'nodes': [
                    {'WWPN': '1000001AA0570260', 'node_logged_in_count': '0', 'state': 'online'},
                    {'WWPN': '1000001AA0570261', 'node_logged_in_count': '0', 'state': 'online'},
                    {'WWPN': '1000001AA0570262', 'node_logged_in_count': '0', 'state': 'online'}
                ]
            }
            with pytest.raises(AnsibleExitJson) as exc:
                obj = IBMSVChost()
                obj.apply()
            self.assertEqual(True, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_hostcluster_update(self, svc_authorize_mock, svc_obj_info_mock, src):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'protocol': 'scsi',
            'type': 'generic',
            'site': 'site1',
            'hostcluster': 'hostcluster0'
        }):
            svc_obj_info_mock.return_value = {
                'id': '24', 'name': 'test', 'port_count': '5', 'type': 'generic',
                'mask': '1111111', 'iogrp_count': '4', 'status': 'offline',
                'site_id': '', 'site_name': 'site2', 'host_cluster_id': '1', 'host_cluster_name': 'hostcluster0'
            }
            with pytest.raises(AnsibleExitJson) as exc:
                obj = IBMSVChost()
                obj.apply()
            self.assertEqual(True, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_duplicate_checker(self, svc_authorize_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'fcwwpn': '1000001AA0570260:1000001AA0570260:1000001AA0570260',
            'protocol': 'scsi',
            'type': 'generic',
            'site': 'site1'
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                obj = IBMSVChost()
                obj.apply()
            self.assertEqual(True, exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_rename(self, mock_auth, mock_old, mock_cmd):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'old_name': 'name',
            'name': 'new_name',
            'state': 'present',
        }):
            mock_old.return_value = [
                {
                    "id": "1", "name": "ansible_host", "port_count": "1",
                    "iogrp_count": "4", "status": "offline",
                    "site_id": "", "site_name": "",
                    "host_cluster_id": "", "host_cluster_name": "",
                    "protocol": "scsi", "owner_id": "",
                    "owner_name": ""
                }
            ]
            arg_data = []
            mock_cmd.return_value = None
            v = IBMSVChost()
            data = v.host_rename(arg_data)
            self.assertEqual(data, 'Host [name] has been successfully rename to [new_name].')

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_rename_failure_for_unsupported_param(self, svc_auth_mock, mock_existing_host):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'old_name': 'ansible_host',
            'name': 'new_ansible_host',
            'state': 'present',
            'fcwwpn': True
        }):
            mock_existing_host.return_value = [
                {
                    "id": "1", "name": "ansible_host", "port_count": "1",
                    "iogrp_count": "4", "status": "offline",
                    "site_id": "", "site_name": "",
                    "host_cluster_id": "", "host_cluster_name": "",
                    "protocol": "scsi", "owner_id": "",
                    "owner_name": ""
                }
            ]
            with pytest.raises(AnsibleFailJson) as exc:
                v = IBMSVChost()
                v.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'], "Parameters ['fcwwpn'] not supported while renaming a host.")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.host_iscsiname_update')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_iscsiname_update_when_existing_absent(self, svc_authorize_mock, get_existing_host_mock, host_iscsinmae_update_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'iscsiname': 'iqn.1994-05.com.redhat:2e358e438b8a',
            'protocol': 'scsi',
            'type': 'generic'
        }):
            lshost_data = {'id': '24', 'name': 'test', 'port_count': '5', 'type': 'generic',
                           'mask': '1111111', 'iogrp_count': '4', 'status': 'offline',
                           'site_id': '', 'site_name': '', 'host_cluster_id': '', 'host_cluster_name': '',
                           'protocol': 'scsi', 'nodes': [{'iscsi_name': 'iqn.1994-05.com.redhat:2e358e438b8a', 'node_logged_in_count': '0', 'state': 'offline'},
                                                         {'iscsi_name': 'iqn.localhost.hostid.7f000001', 'node_logged_in_count': '0', 'state': 'offline'},
                                                         {'iscsi_name': 'iqn.localhost.hostid.7f000002', 'node_logged_in_count': '0', 'state': 'offline'}]}
            get_existing_host_mock.return_value = lshost_data
            host_created = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                host_created.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.host_iscsiname_update')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_iscsiname_update_when_new_added(self, svc_authorize_mock, get_existing_host_mock, host_iscsiname_update_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'iscsiname': 'iqn.1994-05.com.redhat:2e358e438b8a,iqn.localhost.hostid.7f000001,iqn.localhost.hostid.7f000002',
            'protocol': 'scsi',
            'type': 'generic'
        }):
            lshost_data = {'id': '24', 'name': 'test', 'port_count': '5', 'type': 'generic',
                           'mask': '1111111', 'iogrp_count': '4', 'status': 'offline',
                           'site_id': '', 'site_name': '', 'host_cluster_id': '', 'host_cluster_name': '',
                           'protocol': 'scsi', 'nodes': [{'iscsi_name': 'iqn.1994-05.com.redhat:2e358e438b8a', 'node_logged_in_count': '0', 'state': 'offline'},
                                                         {'iscsi_name': 'iqn.localhost.hostid.7f000001', 'node_logged_in_count': '0', 'state': 'offline'}]}
            get_existing_host_mock.return_value = lshost_data
            host_created = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                host_created.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_iscsiname_update(self, svc_authorize_mock, svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'iscsiname': 'iqn.1994-05.com.redhat:2e358e438b8a,iqn.localhost.hostid.7f000002',
            'protocol': 'scsi',
            'type': 'generic'
        }):
            obj = IBMSVChost()
            obj.existing_iscsiname = ['iqn.1994-05.com.redhat:2e358e438b8a', 'iqn.localhost.hostid.7f000001']
            obj.input_iscsiname = ['iqn.1994-05.com.redhat:2e358e438b8a', 'iqn.localhost.hostid.7f000002']
            self.assertEqual(obj.host_iscsiname_update(), None)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.host_create')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_rdmanvme_nqn_update_when_new_added(self, svc_authorize_mock, host_create_mock, get_existing_host_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'nqn': 'nqn.2014-08.com.example:nvme:nvm-example-sn-d78434,nqn.2014-08.com.example:nvme:nvm-example-sn-d78433',
            'protocol': 'rdmanvme',
            'portset': 'portset0',
            'type': 'generic'
        }):
            host = {u'message': u'Host, id [14], '
                                u'successfully created', u'id': u'14'}
            host_create_mock.return_value = host
            get_existing_host_mock.return_value = []
            host_created = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                host_created.apply()

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_nqn_update(self, svc_authorize_mock, svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'nqn': 'nqn.2014-08.com.example:nvme:nvm-example-sn-d78434,nqn.2014-08.com.example:nvme:nvm-example-sn-d78431',
            'protocol': 'rdmanvme',
            'type': 'generic'
        }):
            obj = IBMSVChost()
            obj.existing_nqn = ['nqn.2014-08.com.example:nvme:nvm-example-sn-d78434', 'nqn.2014-08.com.example:nvme:nvm-example-sn-d78433']
            obj.input_nqn = ['nqn.2014-08.com.example:nvme:nvm-example-sn-d78434', 'nqn.2014-08.com.example:nvme:nvm-example-sn-d78431']
            self.assertEqual(obj.host_nqn_update(), None)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_storage_partition_update(self, svc_authorize_mock, svc_obj_info_mock, src):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'partition': 'partition1'
        }):
            svc_obj_info_mock.return_value = {
                'id': '24', 'name': 'test', 'port_count': '5', 'type': 'generic',
                'mask': '1111111', 'iogrp_count': '4', 'status': 'offline',
                'site_id': '', 'site_name': 'site2', 'partition_name': ''
            }
            with pytest.raises(AnsibleExitJson) as exc:
                obj = IBMSVChost()
                obj.apply()
            self.assertEqual(True, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_tcpnvmehost_successfully(self, svc_authorize_mock,
                                             svc_run_command_mock,
                                             get_existing_host_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'protocol': 'tcpnvme',
            'nqn': 'nqn.2014-08.org.nvmexpress:NVMf:uuid:644f51bf-8432-4f59-bb13-5ada20c06397'
        }):
            host = {u'message': u'Host, id [0], '
                                u'successfully created', u'id': u'0'}
            svc_run_command_mock.return_value = host
            get_existing_host_mock.return_value = []
            tcpnvme_host_obj = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                tcpnvme_host_obj.apply()
            self.assertEqual(True, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_mutually_exclusive_params(self, svc_authorize_mock):
        '''
        Failure test for mutually exclusive parameteres: partition and nopartition
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'protocol': 'tcpnvme',
            'nqn': 'nqn.2014-08.org.nvmexpress:NVMf:uuid:644f51bf-8432-4f59-bb13-5ada20c06397',
            'partition': "ptn0",
            'nopartition': True
        }):
            with pytest.raises(AnsibleFailJson) as exc:
                tcpnvme_host_obj = IBMSVChost()
                tcpnvme_host_obj.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'], "Mutually exclusive parameters: partition, nopartition")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_add_existing_host_to_draftpartition(self, svc_authorize_mock, get_existing_host_mock, svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'draftpartition': "ptn0"
        }):
            svc_run_command_mock.return_value = {}
            get_existing_host_mock.return_value = {
                "draft_partition_id": "",
                "draft_partition_name": "",
                "host_cluster_id": "",
                "host_cluster_name": "",
                "id": "1",
                "name": "ansible_host",
                "partition_id": "",
                "partition_name": ""
            }
            with pytest.raises(AnsibleExitJson) as exc:
                host = IBMSVChost()
                host.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_create_host_with_draftpartition(self, svc_authorize_mock, get_existing_host_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'protocol': 'tcpnvme',
            'nqn': 'nqn.2014-08.org.nvmexpress:NVMf:uuid:644f51bf-8432-4f59-bb13-5ada20c06397',
            'draftpartition': "ptn0"
        }):
            get_existing_host_mock.return_value = {}
            with pytest.raises(AnsibleFailJson) as exc:
                host = IBMSVChost()
                host.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_modify_published_partition_host(self, svc_authorize_mock, get_existing_host_mock):
        '''
        Test add host to a partition which is already published
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'draftpartition': "ptn0"
        }):
            get_existing_host_mock.return_value = {
                "draft_partition_id": "",
                "draft_partition_name": "",
                "host_cluster_id": "",
                "host_cluster_name": "",
                "id": "1",
                "name": "ansible_host",
                "partition_id": "1",
                "partition_name": "ptn0"
            }
            with pytest.raises(AnsibleExitJson) as exc:
                host = IBMSVChost()
                host.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_modify_draft_partition_host(self, svc_authorize_mock, get_existing_host_mock):
        '''
        Test add host to a partition which is already in draft state
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'draftpartition': "ptn0"
        }):
            get_existing_host_mock.return_value = {
                "draft_partition_id": "1",
                "draft_partition_name": "ptn0",
                "host_cluster_id": "",
                "host_cluster_name": "",
                "id": "1",
                "name": "ansible_host",
                "partition_id": "",
                "partition_name": ""
            }
            with pytest.raises(AnsibleExitJson) as exc:
                host = IBMSVChost()
                host.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_draft_partition_from_host(self, svc_authorize_mock, get_existing_host_mock, svc_run_command_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'nodraftpartition': True
        }):
            svc_run_command_mock.return_value = {}
            get_existing_host_mock.return_value = {
                "draft_partition_id": "1",
                "draft_partition_name": "ptn0",
                "host_cluster_id": "",
                "host_cluster_name": "",
                "id": "1",
                "name": "ansible_host",
                "partition_id": "",
                "partition_name": ""
            }
            with pytest.raises(AnsibleExitJson) as exc:
                host = IBMSVChost()
                host.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_fcnvmehost_successfully(self, svc_authorize_mock,
                                            svc_run_command_mock,
                                            get_existing_host_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'protocol': 'fcnvme',
            'nqn': 'nqn.2014-08.org.nvmexpress:NVMf:uuid:644f51bf-8432-4f59-bb13-5ada20c06397'
        }):
            host = {u'message': u'Host, id [0], '
                                u'successfully created', u'id': u'0'}
            svc_run_command_mock.return_value = host
            get_existing_host_mock.return_value = []
            fcnvme_host_obj = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                fcnvme_host_obj.apply()
            self.assertEqual(True, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_fcnvmehost_without_protocol(self, svc_authorize_mock,
                                                get_existing_host_mock):
        '''
        Test to create fcnvme host without protocol, should fail
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'state': 'present',
            'nqn': 'nqn.2014-08.org.nvmexpress:NVMf:uuid:644f51bf-8432-4f59-bb13-5ada20c06397'
        }):
            get_existing_host_mock.return_value = {}
            with pytest.raises(AnsibleFailJson) as exc:
                nqn_host_obj = IBMSVChost()
                nqn_host_obj.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_fdmihost_successfully(self, svc_authorize_mock, svc_run_command_mock, get_existing_host_mock):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'protocol': 'fcscsi',
            'fdminame': '78F1CV1-1'
        }):
            host = {u'message': u'Host, id [0], '
                                u'successfully created', u'id': u'0'}
            svc_run_command_mock.return_value = host
            get_existing_host_mock.return_value = []
            fdmi_host_obj = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                fdmi_host_obj.apply()
            self.assertEqual(True, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_suppressofflinealert_update(self, svc_authorize_mock, svc_obj_info_mock,
                                         svc_run_command_mock):
        '''
        Test to update suppressofflinealert, should pass
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'suppressofflinealert': 'yes'
        }):
            svc_obj_info_mock.return_value = {
                'id': '24',
                'name': 'test',
                'iogrp_count': '4',
                'status': 'offline',
                'site_name': 'site2',
                'offline_alert_suppressed': 'no'
            }
            with pytest.raises(AnsibleExitJson) as exc:
                obj = IBMSVChost()
                obj.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_iscsihost(self, svc_authorize_mock,
                              svc_run_command_mock,
                              get_existing_host_mock,
                              svc_obj_info_mock):
        '''
        Test to create iscsi host, should pass
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'iscsiname': 'iqn.localhost.hostid.7f000001',
            'protocol': 'iscsi',
            'portset': 'ipportset'
        }):
            host = {u'message': u'Host, id [0], '
                                u'successfully created', u'id': u'0'}
            svc_run_command_mock.return_value = host
            get_existing_host_mock.return_value = []
            # Mock portset lookup
            svc_obj_info_mock.return_value = {'id': '1', 'name': 'ipportset', 'auto_zone_enabled': 'no'}
            iscsi_host_obj = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                iscsi_host_obj.apply()
            self.assertEqual(True, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.host_probe')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_iscsihost_idempotency(self, svc_authorize_mock,
                                          host_probe_mock,
                                          get_existing_host_mock):
        '''
        Test to create iscsi host with same config, should pass
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'iscsiname': 'iqn.localhost.hostid.7f000001',
            'protocol': 'iscsi'
        }):
            get_existing_host_mock.return_value = [{"id": "0", "name": "ansible_host", "port_count": "1",
                                                    "iogrp_count": "4", "status": "offline",
                                                    "site_id": "", "site_name": "", 'iscsi_name': 'iqn.localhost.hostid.7f000001',
                                                    "host_cluster_id": "", "host_cluster_name": "",
                                                    "protocol": "iscsi", "owner_id": "",
                                                    "owner_name": ""}]
            host_probe_mock.return_value = []
            iscsi_host_obj = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                iscsi_host_obj.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_fcscsihost(self, svc_authorize_mock,
                               svc_run_command_mock,
                               get_existing_host_mock,
                               svc_obj_info_mock):
        '''
        Test to create fcscsi host, should pass
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'fcwwpn': '5005076812113196',
            'protocol': 'fcscsi',
            'portset': 'fcportset'
        }):
            host = {u'message': u'Host, id [0], '
                                u'successfully created', u'id': u'0'}
            svc_run_command_mock.return_value = host
            get_existing_host_mock.return_value = []
            # Mock portset lookup
            svc_obj_info_mock.return_value = {'id': '1', 'name': 'fcportset', 'auto_zone_enabled': 'no'}
            iscsi_host_obj = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                iscsi_host_obj.apply()
            self.assertEqual(True, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_host_specifying_location(self, svc_authorize_mock,
                                             get_existing_host_mock,
                                             svc_run_command_mock):
        with set_module_args({
            'clustername': '{{clustername}}',
            'username': '{{username}}',
            'password': '{{password}}',
            'state': 'present',
            'name': 'host0',
            'location': 'fs9500cl-2',
            'partition': 'ha-partition-0',
            'fcwwpn': '21000024FF7D9505'
        }):
            svc_run_command_mock.return_value = {
                'message': "success"
            }
            get_existing_host_mock.return_value = {}
            with pytest.raises(AnsibleExitJson) as exc:
                host_obj = IBMSVChost()
                host_obj.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_host_specifying_location_idempotency(self, svc_authorize_mock,
                                                         get_existing_host_mock):
        with set_module_args({
            'clustername': '{{clustername}}',
            'username': '{{username}}',
            'password': '{{password}}',
            'state': 'present',
            'name': 'host0',
            'location': 'fs9500cl-2',
            'partition': 'ha-partition-0',
            'fcwwpn': '21000024FF7D9505'
        }):
            lshost_data = {'id': '24', 'name': 'test', 'port_count': '5', 'type': 'generic',
                           'mask': '1111111', 'iogrp_count': '4', 'status': 'offline',
                           'site_id': '', 'site_name': '', 'host_cluster_id': '', 'host_cluster_name': '',
                           'protocol': 'scsi', 'nodes': [{'WWPN': '21000024FF7D9505', 'node_logged_in_count': '0', 'state': 'online'}],
                           'partition_name': 'ha-partition-0', 'location_system_id': '0000020438007A94', 'location_system_name': 'fs9500cl-2'}
            get_existing_host_mock.return_value = lshost_data
            with pytest.raises(AnsibleExitJson) as exc:
                host_obj = IBMSVChost()
                host_obj.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_missing_dependent_param_1(self, svc_authorize_mock,
                                               get_existing_host_mock):
        '''
        Test for failure while missing dependent parameter partition needed with parameter location
        '''
        with set_module_args({
            'clustername': '{{clustername}}',
            'username': '{{username}}',
            'password': '{{password}}',
            'state': 'present',
            'name': 'host0',
            'location': 'fs9500cl-2',
            'fcwwpn': '21000024FF7D9505'
        }):
            get_existing_host_mock.return_value = {}
            with pytest.raises(AnsibleFailJson) as exc:
                host_obj = IBMSVChost()
                host_obj.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'], "Parameter [location] can only be entered when [partition] has been entered.")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_modify_host_specifying_location(self, svc_authorize_mock,
                                             get_existing_host_mock,
                                             svc_run_command_mock):
        with set_module_args({
            'clustername': '{{clustername}}',
            'username': '{{username}}',
            'password': '{{password}}',
            'state': 'present',
            'name': 'host0',
            'location': 'fs9500cl-2',
        }):
            get_existing_host_mock.return_value = {
                'id': '24', 'name': 'test', 'port_count': '5', 'type': 'generic',
                'mask': '1111111', 'iogrp_count': '4', 'status': 'offline',
                'site_id': '', 'site_name': 'site2', 'partition_name': 'ha-partition-0', 'location_system_id': '0000020438007A94',
                'location_system_name': 'cluster123'
            }
            svc_run_command_mock.return_value = {
                "message": "Success"
            }
            with pytest.raises(AnsibleExitJson) as exc:
                host_obj = IBMSVChost()
                host_obj.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_location_from_host(self, svc_authorize_mock,
                                       get_existing_host_mock,
                                       svc_run_command_mock):
        with set_module_args({
            'clustername': '{{clustername}}',
            'username': '{{username}}',
            'password': '{{password}}',
            'state': 'present',
            'name': 'host0',
            'location': '',
        }):
            get_existing_host_mock.return_value = {
                'id': '24', 'name': 'test', 'port_count': '5', 'type': 'generic',
                'mask': '1111111', 'iogrp_count': '4', 'status': 'offline',
                'site_id': '', 'site_name': 'site2', 'partition_name': 'ha-partition-0', 'location_system_id': '0000020438007A94',
                'location_system_name': 'cluster123'
            }
            svc_run_command_mock.return_value = {
                "message": "Success"
            }
            with pytest.raises(AnsibleExitJson) as exc:
                host_obj = IBMSVChost()
                host_obj.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_location_from_host_idempotency(self, svc_authorize_mock,
                                                   get_existing_host_mock):
        with set_module_args({
            'clustername': '{{clustername}}',
            'username': '{{username}}',
            'password': '{{password}}',
            'state': 'present',
            'name': 'host0',
            'location': '',
        }):
            get_existing_host_mock.return_value = {
                'id': '24', 'name': 'test', 'port_count': '5', 'type': 'generic',
                'mask': '1111111', 'iogrp_count': '4', 'status': 'offline',
                'site_id': '', 'site_name': 'site2', 'partition_name': 'ha-partition-0', 'location_system_id': '',
                'location_system_name': ''
            }

            with pytest.raises(AnsibleExitJson) as exc:
                host_obj = IBMSVChost()
                host_obj.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_site_from_host(self, svc_authorize_mock,
                                   get_existing_host_mock,
                                   svc_run_command_mock):
        with set_module_args({
            'clustername': '{{clustername}}',
            'username': '{{username}}',
            'password': '{{password}}',
            'state': 'present',
            'name': 'host0',
            'site': '',
        }):
            get_existing_host_mock.return_value = {
                'id': '24', 'name': 'test', 'port_count': '5', 'type': 'generic',
                'mask': '1111111', 'iogrp_count': '4', 'status': 'offline',
                'site_id': '2', 'site_name': 'site2', 'partition_name': 'ha-partition-0', 'location_system_id': '0000020438007A94',
                'location_system_name': 'cluster123'
            }
            svc_run_command_mock.return_value = {
                "message": "Success"
            }
            with pytest.raises(AnsibleExitJson) as exc:
                host_obj = IBMSVChost()
                host_obj.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_remove_site_from_host_idempotency(self, svc_authorize_mock,
                                               get_existing_host_mock):
        with set_module_args({
            'clustername': '{{clustername}}',
            'username': '{{username}}',
            'password': '{{password}}',
            'state': 'present',
            'name': 'host0',
            'site': '',
        }):
            get_existing_host_mock.return_value = {
                'id': '24', 'name': 'test', 'port_count': '5', 'type': 'generic',
                'mask': '1111111', 'iogrp_count': '4', 'status': 'offline',
                'site_id': '', 'site_name': '', 'partition_name': 'ha-partition-0', 'location_system_id': '',
                'location_system_name': ''
            }

            with pytest.raises(AnsibleExitJson) as exc:
                host_obj = IBMSVChost()
                host_obj.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_host_with_autostoragediscovery(self, svc_authorize_mock,
                                                   svc_run_command_mock,
                                                   get_existing_host_mock):
        '''
        Test creating a new host with autostoragediscovery='yes', should pass
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'state': 'present',
            'fcwwpn': '100000109B570216',
            'protocol': 'fcscsi',
            'autostoragediscovery': 'yes'
        }):
            svc_run_command_mock.return_value = {
                'message': 'Host, id [1], successfully created',
                'id': '1'
            }
            get_existing_host_mock.return_value = {}
            with pytest.raises(AnsibleExitJson) as exc:
                obj = IBMSVChost()
                obj.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_tcpnvme_host_inside_partition(self, svc_authorize_mock,
                                                  svc_run_command_mock,
                                                  get_existing_host_mock):
        with set_module_args({
            'clustername': 'clustername',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'iscsiname': 'nqn.localhost.hostid.7f000001',
            'protocol': 'tcpnvme',
            'portset': 'test_portset'
        }):
            host = {u'message': u'Host, id [0], '
                                u'successfully created', u'id': u'0'}
            svc_run_command_mock.return_value = host
            get_existing_host_mock.return_value = []
            iscsi_host_obj = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                iscsi_host_obj.apply()
            self.assertEqual(True, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_host_with_autostoragediscovery_without_port_identifier(self, svc_authorize_mock,
                                                                           get_existing_host_mock):
        '''
        Negative test: creating a host with only autostoragediscovery and no port
        identifier (fcwwpn/iscsiname/nqn/fdminame) should fail
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'state': 'present',
            'autostoragediscovery': 'yes'
        }):
            get_existing_host_mock.return_value = {}
            with pytest.raises(AnsibleFailJson) as exc:
                obj = IBMSVChost()
                obj.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertEqual(exc.value.args[0]['msg'], "One of fcwwpn, saswwpn, iscsiname, nqn or fdminame must be provided to create a new host.")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_autostoragediscovery_update(self, svc_authorize_mock, svc_obj_info_mock,
                                         svc_run_command_mock):
        '''
        Test to enable autostoragediscovery on existing host, should pass
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'autostoragediscovery': 'yes'
        }):
            svc_obj_info_mock.return_value = {
                'id': '24',
                'name': 'test',
                'iogrp_count': '4',
                'status': 'offline',
                'site_name': '',
                'auto_storage_discovery': 'no'
            }
            with pytest.raises(AnsibleExitJson) as exc:
                obj = IBMSVChost()
                obj.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_fcnvme_host_inside_partition(self, svc_authorize_mock,
                                                 svc_run_command_mock,
                                                 get_existing_host_mock):
        with set_module_args({
            'clustername': 'clustername',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'iscsiname': 'nqn.localhost.hostid.7f000001',
            'protocol': 'fcnvme',
            'portset': 'test_portset'
        }):
            host = {u'message': u'Host, id [0], '
                                u'successfully created', u'id': u'0'}
            svc_run_command_mock.return_value = host
            get_existing_host_mock.return_value = []
            iscsi_host_obj = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                iscsi_host_obj.apply()
            self.assertEqual(True, exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_sas_host_successfully(self, svc_authorize_mock,
                                          svc_run_command_mock,
                                          get_existing_host_mock):
        '''
        Test to create SAS host with saswwpn, should pass
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_sas_host',
            'saswwpn': '210100E08B251DD4',
            'protocol': 'sas'
        }):
            host = {'message': 'Host, id [0], successfully created', 'id': '0'}
            svc_run_command_mock.return_value = host
            get_existing_host_mock.return_value = []
            sas_host_obj = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                sas_host_obj.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_sas_host_missing_protocol(self, svc_authorize_mock,
                                              get_existing_host_mock):
        '''
        Test to create SAS host without protocol, should fail
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_sas_host',
            'state': 'present',
            'saswwpn': '210100E08B251DD4'
        }):
            get_existing_host_mock.return_value = []
            with pytest.raises(AnsibleFailJson) as exc:
                sas_host_obj = IBMSVChost()
                sas_host_obj.apply()
            self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_hostcluster')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failure_create_host_with_multiple_protocol_identifiers(self, svc_authorize_mock,
                                                                    get_existing_host_mock,
                                                                    svc_run_command_mock,
                                                                    get_existing_hostcluster_mock):
        '''
        Test mutual exclusivity: only one protocol identifier can be used at a time
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'state': 'present',
            'fcwwpn': '1000001AA0570260',
            'saswwpn': '210100E08B251DD4',
            'protocol': 'sas'
        }):
            get_existing_host_mock.return_value = []
            with pytest.raises(AnsibleFailJson) as exc:
                host_obj = IBMSVChost()
                host_obj.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertIn('One of fcwwpn', exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.host_saswwpn_update')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_saswwpn_update_when_existing_absent(self, svc_authorize_mock,
                                                 get_existing_host_mock,
                                                 host_saswwpn_update_mock):
        '''
        Test SAS WWPN update when some existing WWPNs are removed
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_sas',
            'state': 'present',
            'saswwpn': '210100E08B251DD4',
            'protocol': 'sas',
            'type': 'generic'
        }):
            lshost_data = {
                'id': '24', 'name': 'test_sas', 'port_count': '3', 'type': 'generic',
                'mask': '1111111', 'iogrp_count': '4', 'status': 'offline',
                'site_id': '', 'site_name': '', 'host_cluster_id': '', 'host_cluster_name': '',
                'protocol': 'sas',
                'nodes': [
                    {'SAS_WWPN': '210100E08B251DD2', 'node_logged_in_count': '0', 'state': 'online'},
                    {'SAS_WWPN': '210100E08B251DD3', 'node_logged_in_count': '0', 'state': 'online'},
                    {'SAS_WWPN': '210100E08B251DD4', 'node_logged_in_count': '0', 'state': 'online'}
                ]
            }
            get_existing_host_mock.return_value = lshost_data
            host_created = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                host_created.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.host_saswwpn_update')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_saswwpn_update_when_new_added(self, svc_authorize_mock,
                                           get_existing_host_mock,
                                           host_saswwpn_update_mock):
        '''
        Test SAS WWPN update when new WWPNs are added
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_sas',
            'state': 'present',
            'saswwpn': '210100E08B251DD2:210100E08B251DD3:210100E08B251DD4:210100F08C262DD8',
            'protocol': 'sas',
            'type': 'generic'
        }):
            lshost_data = {
                'id': '24', 'name': 'test_sas', 'port_count': '3', 'type': 'generic',
                'mask': '1111111', 'iogrp_count': '4', 'status': 'offline',
                'site_id': '', 'site_name': '', 'host_cluster_id': '', 'host_cluster_name': '',
                'protocol': 'sas',
                'nodes': [
                    {'SAS_WWPN': '210100E08B251DD2', 'node_logged_in_count': '0', 'state': 'online'},
                    {'SAS_WWPN': '210100E08B251DD3', 'node_logged_in_count': '0', 'state': 'online'},
                    {'SAS_WWPN': '210100E08B251DD4', 'node_logged_in_count': '0', 'state': 'online'}
                ]
            }
            get_existing_host_mock.return_value = lshost_data
            host_created = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                host_created.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.host_saswwpn_update')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_saswwpn_update_when_existing_removed_and_new_added(self, svc_authorize_mock,
                                                                get_existing_host_mock,
                                                                host_saswwpn_update_mock):
        '''
        Test SAS WWPN update when some existing WWPNs are removed and new ones added
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_sas',
            'state': 'present',
            'saswwpn': '210100F08C262DD8:210100F08C262DD9:210100F08C262DDA',
            'protocol': 'sas',
            'type': 'generic'
        }):
            lshost_data = {
                'id': '24', 'name': 'test_sas', 'port_count': '3', 'type': 'generic',
                'mask': '1111111', 'iogrp_count': '4', 'status': 'offline',
                'site_id': '', 'site_name': '', 'host_cluster_id': '', 'host_cluster_name': '',
                'protocol': 'sas',
                'nodes': [
                    {'SAS_WWPN': '210100E08B251DD2', 'node_logged_in_count': '0', 'state': 'online'},
                    {'SAS_WWPN': '210100E08B251DD3', 'node_logged_in_count': '0', 'state': 'online'},
                    {'SAS_WWPN': '210100E08B251DD4', 'node_logged_in_count': '0', 'state': 'online'}
                ]
            }
            get_existing_host_mock.return_value = lshost_data
            host_created = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                host_created.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_saswwpn_update(self, svc_authorize_mock,
                                 get_existing_host_mock,
                                 svc_run_command_mock):
        '''
        Test host_saswwpn_update via apply():
        existing nodes carry DD3/DD4/DD8; desired state is DD8/DD9/DDA.
        apply() runs host_probe (detects diff) -> host_update ->
        host_saswwpn_update (rmhostport DD3:DD4, addhostport DD9:DDA).
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_sas',
            'state': 'present',
            'saswwpn': '210100F08C262DD8:210100F08C262DD9:210100F08C262DDA',
            'protocol': 'sas',
            'type': 'generic'
        }):
            lshost_data = {
                'id': '24', 'name': 'test_sas', 'port_count': '3', 'type': 'generic',
                'mask': '1111111', 'iogrp_count': '4', 'status': 'offline',
                'site_id': '', 'site_name': '', 'host_cluster_id': '', 'host_cluster_name': '',
                'protocol': 'sas',
                'nodes': [
                    {'SAS_WWPN': '210100E08B251DD3', 'node_logged_in_count': '0', 'state': 'online'},
                    {'SAS_WWPN': '210100E08B251DD4', 'node_logged_in_count': '0', 'state': 'online'},
                    {'SAS_WWPN': '210100F08C262DD8', 'node_logged_in_count': '0', 'state': 'online'}
                ]
            }
            get_existing_host_mock.return_value = lshost_data
            svc_run_command_mock.return_value = None
            obj = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                obj.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_duplicate_saswwpn_detection(self, svc_authorize_mock, get_existing_host_mock):
        '''
        Test duplicate SAS WWPN detection
        '''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_sas',
            'state': 'present',
            'saswwpn': '210100E08B251DD4:210100F08C262DD8:210100E08B251DD4',
            'protocol': 'sas'
        }):
            get_existing_host_mock.return_value = []
            with pytest.raises(AnsibleFailJson) as exc:
                host_obj = IBMSVChost()
                host_obj.apply()
            self.assertTrue(exc.value.args[0]['failed'])
            self.assertIn('entered multiple times', exc.value.args[0]['msg'].lower())

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_autozone_resolve_forceautozone_for_autozone_enabled_portset(self, mock_auth, mock_run_cmd, mock_obj_info):
        """Test that -forceautozone is used when portset has auto_zone_enabled=yes"""
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'host1',
            'state': 'present',
            'fcwwpn': '100000109B570216',
            'portset': 'portset_autozone'
        }):
            mock_obj_info.side_effect = [
                {
                    'id': '1',
                    'name': 'host1',
                    'portset_name': '',
                    'nodes': [],
                    'host_cluster_name': '',
                    'type': 'generic'
                },
                {'id': '3', 'name': 'portset_autozone', 'auto_zone_enabled': 'yes'},  # Call in _resolve_force_flag_for_host
                {'id': '00000204AEA0632C', 'name': 'system0', 'code_level': '9.1.3.0 (build 193.16.2602231501000)'},
            ]
            mock_run_cmd.return_value = None

            with pytest.raises(AnsibleExitJson) as exc:
                obj = IBMSVChost()
                obj.apply()

            self.assertTrue(exc.value.args[0]['changed'])

            # Find the addhostport call
            addhostport_calls = [call for call in mock_run_cmd.call_args_list
                                 if len(call[0]) > 0 and call[0][0] == 'addhostport']
            self.assertTrue(len(addhostport_calls) > 0, "addhostport command should have been called")

            # Get the cmdopts (second positional argument)
            call_args = addhostport_calls[0][0][1]

            # Verify forceautozone flag was used (not force)
            self.assertIn('forceautozone', call_args, "forceautozone flag should be present")
            self.assertTrue(call_args['forceautozone'], "forceautozone should be True")
            self.assertNotIn('force', call_args, "force flag should not be present when using forceautozone")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_autozone_resolve_force_for_standard_portset(self, mock_auth, mock_run_cmd, mock_obj_info):
        """Test that -force is used when portset has auto_zone_enabled=no"""
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'host1',
            'state': 'present',
            'fcwwpn': '100000109B570216',
            'portset': 'portset_standard'
        }):
            mock_obj_info.side_effect = [
                {
                    'id': '1',
                    'name': 'host1',
                    'portset_name': '',
                    'nodes': [],
                    'host_cluster_name': '',
                    'type': 'generic'
                },  # lshost
                {'id': '3', 'name': 'portset_standard', 'auto_zone_enabled': 'no'},  # lsportset
                {'id': '00000204AEA0632C', 'name': 'system0', 'code_level': '9.1.3.0 (build 193.16.2602231501000)'},  # lssystem
            ]
            mock_run_cmd.return_value = None

            with pytest.raises(AnsibleExitJson) as exc:
                obj = IBMSVChost()
                obj.apply()

            self.assertTrue(exc.value.args[0]['changed'])
            # Verify force flag was used (not forceautozone)
            addhostport_call = next(call for call in mock_run_cmd.call_args_list if call[0][0] == 'addhostport')
            call_args = addhostport_call[0][1]
            self.assertIn('force', call_args)
            self.assertTrue(call_args['force'])
            self.assertNotIn('forceautozone', call_args)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_autozone_portset_not_found_fails_early(self, mock_auth, mock_obj_info):
        """Test that missing portset fails before attempting host operations"""
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'host1',
            'state': 'present',
            'fcwwpn': '100000109B570216',
            'portset': 'nonexistent_portset'
        }):
            mock_obj_info.side_effect = [
                {
                    'id': '1',
                    'name': 'host1',
                    'portset_name': '',
                    'nodes': [{'WWPN': '100000109B570216'}, {'WWPN': '100000109B570217'}],
                    'host_cluster_name': '',
                    'type': 'generic'
                },
                None,  # portset lookup returns None (not found)
                None,  # Additional call for _is_portset_autozone_enabled
            ]

            with pytest.raises(AnsibleFailJson) as exc:
                obj = IBMSVChost()
                obj.apply()

            self.assertTrue(exc.value.args[0]['failed'])
            msg = exc.value.args[0]['msg']
            self.assertIn('portset', str(msg).lower())

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_autozone_no_portset_change_skips_resolution(self, mock_auth, mock_obj_info):
        """Test that flag resolution is skipped when portset doesn't change"""
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'host1',
            'state': 'present',
            'portset': 'portset_autozone'
        }):
            # Host already has the desired portset
            mock_obj_info.return_value = {
                'id': '1',
                'name': 'host1',
                'portset_name': 'portset_autozone'
            }

            with pytest.raises(AnsibleExitJson) as exc:
                obj = IBMSVChost()
                obj.apply()

            # No change needed
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_autozone_no_portset_parameter_uses_existing_behavior(self, mock_auth, mock_run_cmd, mock_obj_info):
        """Test that operations without portset parameter don't trigger autozone logic"""
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'host1',
            'state': 'present',
            'fcwwpn': '100000109B570216'
        }):
            mock_obj_info.return_value = {
                'id': '1',
                'name': 'host1',
                'portset_name': '',
                'nodes': [],
                'host_cluster_name': '',
                'type': 'generic'
            }

            with pytest.raises(AnsibleExitJson) as exc:
                obj = IBMSVChost()
                obj.apply()

            # Should complete without querying portset
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_autozone_decouples_portset_when_fcwwpn_changes(self, mock_auth, mock_run_cmd, mock_obj_info):
        """Test that portset is updated early if both portset and fcwwpn change."""
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'host1',
            'state': 'present',
            'fcwwpn': '100000109B570216',
            'portset': 'portset_autozone'
        }):
            mock_obj_info.side_effect = [
                {
                    'id': '1',
                    'name': 'host1',
                    'portset_name': 'portset_standard',
                    'nodes': [],
                    'host_cluster_name': '',
                    'type': 'generic'
                },  # lshost
                {'id': '3', 'name': 'portset_autozone', 'auto_zone_enabled': 'yes'},  # _resolve_force_flag_for_host lsportset
                {'id': '00000204AEA0632C', 'name': 'system0', 'code_level': '9.1.3.0 (build 193.16.2602231501000)'},  # lssystem
            ]
            mock_run_cmd.return_value = None

            with pytest.raises(AnsibleExitJson) as exc:
                obj = IBMSVChost()
                obj.apply()

            self.assertTrue(exc.value.args[0]['changed'])
            # Verify the order of mock_run_cmd calls: chhost (portset), then addhostport
            call_list = [call[0][0] for call in mock_run_cmd.call_args_list if call[0][0] in ('chhost', 'addhostport')]
            self.assertEqual(call_list, ['chhost', 'addhostport'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_add_fcwwpn_omit_portset_uses_forceautozone(self, mock_auth, mock_run_cmd, mock_obj_info):
        """Edge Case 1: Add fcwwpn but omit portset. Should lookup host's existing portset and resolve force flag."""
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'edge_case_host_1',
            'state': 'present',
            'fcwwpn': '100000109B570216:100000109B570217:100000109B570218'
        }):
            mock_obj_info.side_effect = [
                {
                    'id': '1',
                    'name': 'edge_case_host_1',
                    'portset_name': 'edge_az_portset',
                    'nodes': [{'WWPN': '100000109B570216'}, {'WWPN': '100000109B570217'}],
                    'host_cluster_name': '',
                    'type': 'generic'
                },  # lshost returns existing portset
                {'id': '3', 'name': 'edge_az_portset', 'auto_zone_enabled': 'yes'},  # lsportset
                {'id': 'system0', 'name': 'system0', 'code_level': '9.1.3.0 (build 193.16.2602231501000)'},  # lssystem
            ]
            mock_run_cmd.return_value = None

            with pytest.raises(AnsibleExitJson) as exc:
                obj = IBMSVChost()
                obj.apply()

            self.assertTrue(exc.value.args[0]['changed'])
            # Verify that addhostport used forceautozone because existing portset was autozone enabled
            addhostport_call = next(call for call in mock_run_cmd.call_args_list if call[0][0] == 'addhostport')
            self.assertIn('forceautozone', addhostport_call[0][1])
            self.assertTrue(addhostport_call[0][1]['forceautozone'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_remove_fcwwpn_uses_force(self, mock_auth, mock_run_cmd, mock_obj_info):
        """Edge Case 3: Remove one fcwwpn. Should use force=True for rmhostport, never forceautozone."""
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'edge_case_host_3',
            'state': 'present',
            'fcwwpn': '100000109B570216',  # Only 1 provided, removing the second
            'portset': 'edge_az_portset'
        }):
            mock_obj_info.side_effect = [
                {
                    'id': '1',
                    'name': 'edge_case_host_3',
                    'portset_name': 'edge_az_portset',
                    'nodes': [{'WWPN': '100000109B570216'}, {'WWPN': '100000109B570217'}],
                    'host_cluster_name': '',
                    'type': 'generic'
                },  # lshost
                {'id': '3', 'name': 'edge_az_portset', 'auto_zone_enabled': 'yes'},  # lsportset
                {'id': 'system0', 'name': 'system0', 'code_level': '9.1.3.0 (build 193.16.2602231501000)'},  # lssystem
            ]
            mock_run_cmd.return_value = None

            with pytest.raises(AnsibleExitJson) as exc:
                obj = IBMSVChost()
                obj.apply()

            self.assertTrue(exc.value.args[0]['changed'])
            # rmhostport should be called with force=True
            rmhostport_call = next(call for call in mock_run_cmd.call_args_list if call[0][0] == 'rmhostport')
            self.assertIn('force', rmhostport_call[0][1])
            self.assertTrue(rmhostport_call[0][1]['force'])
            self.assertNotIn('forceautozone', rmhostport_call[0][1])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_saswwpn_with_portset_passes_to_svc(self, mock_auth, mock_run_cmd, mock_obj_info):
        """Edge Case 4: Create host with saswwpn in standard portset. Should pass portset to array, letting it fail."""
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'edge_case_host_4',
            'state': 'present',
            'protocol': 'sas',
            'saswwpn': '2100000E1EE89F77',
            'portset': 'edge_std_portset'
        }):
            mock_obj_info.side_effect = [None]  # Host doesn't exist
            mock_run_cmd.side_effect = Exception("CMMVC9777E")

            with pytest.raises(Exception) as exc:
                obj = IBMSVChost()
                obj.apply()

            # Verify mkhost gets BOTH saswwpn and portset
            mkhost_call = mock_run_cmd.call_args_list[0]
            self.assertEqual(mkhost_call[0][0], 'mkhost')
            self.assertEqual(mkhost_call[0][1]['saswwpn'], '2100000E1EE89F77')
            self.assertEqual(mkhost_call[0][1]['portset'], 'edge_std_portset')
            self.assertEqual(mkhost_call[0][1]['protocol'], 'sas')

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_create_with_autozone_portset(self,
                                               svc_authorize_mock,
                                               svc_run_command_mock,
                                               svc_obj_info_mock,
                                               get_existing_host_mock):
        """Test host creation with autozone-enabled portset uses forceautozone flag"""
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_host',
            'fcwwpn': '1000000000000001',
            'portset': 'autozone_portset',
            'state': 'present'
        }):
            get_existing_host_mock.return_value = {}
            svc_obj_info_mock.side_effect = [
                {'id': '1', 'name': 'autozone_portset', 'auto_zone_enabled': 'yes'},  # lsportset
                {'id': '00000204AEA0632C', 'name': 'system0', 'code_level': '9.1.3.0 (build 193.16.2602231501000)'}  # lssystem
            ]
            svc_run_command_mock.return_value = {'id': '1', 'message': 'Host created'}

            with pytest.raises(AnsibleExitJson) as exc:
                obj = IBMSVChost()
                obj.apply()

            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_portset_not_found_error(self,
                                          svc_authorize_mock,
                                          svc_obj_info_mock):
        """Test error when specified portset doesn't exist"""
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'test_host',
            'fcwwpn': '1000000000000001',
            'portset': 'nonexistent_portset',
            'state': 'present'
        }):
            svc_obj_info_mock.side_effect = [
                {},  # Host doesn't exist
                None  # Portset lookup returns None
            ]

            with pytest.raises(AnsibleFailJson) as exc:
                obj = IBMSVChost()
                obj.apply()

            self.assertTrue(exc.value.args[0]['failed'])
            msg = exc.value.args[0]['msg']
            # msg can be either a string or a dict
            if isinstance(msg, dict):
                msg_str = str(msg)
            else:
                msg_str = msg
            self.assertIn('portset', msg_str.lower())

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    def test_host_change_portset_autozone_to_standard(self,
                                                      svc_run_command_mock,
                                                      svc_authorize_mock,
                                                      svc_obj_info_mock):
        """Test changing host from autozone to standard portset"""
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'test_host',
            'fcwwpn': '1000000000000001',
            'portset': 'standard_portset',
            'state': 'present'
        }):
            svc_obj_info_mock.side_effect = [
                {
                    'id': '1',
                    'name': 'test_host',
                    'portset_name': 'autozone_portset',
                    'nodes': [{'WWPN': '100000109B570216'}, {'WWPN': '100000109B570217'}],
                    'host_cluster_name': '',
                    'type': 'generic'
                },
                {
                    'id': '2',
                    'name': 'standard_portset',
                    'auto_zone_enabled': 'no'
                },
                {
                    'id': '00000204AEA0632C',
                    'name': 'system0',
                    'code_level': '9.1.3.0 (build 193.16.2602231501000)'
                }
            ]
            svc_run_command_mock.return_value = None

            with pytest.raises(AnsibleExitJson) as exc:
                obj = IBMSVChost()
                obj.apply()

            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_change_portset_standard_to_autozone(self,
                                                      svc_authorize_mock,
                                                      svc_obj_info_mock,
                                                      svc_run_command_mock):
        """Test changing host from standard to autozone portset"""
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'test_host',
            'fcwwpn': '1000000000000001',
            'portset': 'autozone_portset',
            'state': 'present'
        }):
            svc_obj_info_mock.side_effect = [
                {
                    'id': '1',
                    'name': 'test_host',
                    'portset_name': 'standard_portset',
                    'nodes': [{'WWPN': '100000109B570216'}, {'WWPN': '100000109B570217'}],
                    'host_cluster_name': '',
                    'type': 'generic'
                },
                {
                    'id': '2',
                    'name': 'autozone_portset',
                    'auto_zone_enabled': 'yes'
                },
                {
                    'id': '00000204AEA0632C',
                    'name': 'system0',
                    'code_level': '9.1.3.0 (build 193.16.2602231501000)'
                }
            ]
            svc_run_command_mock.return_value = None

            with pytest.raises(AnsibleExitJson) as exc:
                obj = IBMSVChost()
                obj.apply()

            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_no_portset_change_needed(self,
                                           svc_authorize_mock,
                                           svc_obj_info_mock):
        """Test when host already has the desired portset"""
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'test_host',
            'fcwwpn': '1000000000000001',
            'portset': 'autozone_portset',
            'state': 'present'
        }):
            svc_obj_info_mock.side_effect = [
                {
                    'id': '1',
                    'name': 'test_host',
                    'portset_name': 'autozone_portset',
                    'nodes': [{'WWPN': '1000000000000001'}],
                    'host_cluster_name': '',
                    'type': 'generic'
                },
                {
                    'id': '00000204AEA0632C',
                    'name': 'system0',
                    'code_level': '9.1.3.0 (build 193.16.2602231501000)'
                }
            ]

            with pytest.raises(AnsibleExitJson) as exc:
                obj = IBMSVChost()
                obj.apply()

            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    def test_host_create_without_portset(self,
                                         svc_run_command_mock,
                                         svc_authorize_mock,
                                         svc_obj_info_mock):
        """Test creating host without portset parameter"""
        with set_module_args({
            'clustername': 'clustername',
            'username': 'username',
            'password': 'password',
            'name': 'test_host',
            'fcwwpn': '1000000000000001',
            'state': 'present'
        }):
            svc_obj_info_mock.return_value = {}
            svc_run_command_mock.return_value = {'id': '1', 'message': 'Host created'}

            with pytest.raises(AnsibleExitJson) as exc:
                obj = IBMSVChost()
                obj.apply()

            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_create_with_standard_portset(self,
                                               svc_authorize_mock,
                                               svc_run_command_mock,
                                               svc_obj_info_mock,
                                               get_existing_host_mock):
        """Test host creation with standard portset uses force flag"""
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_host',
            'state': 'present',
            'fcwwpn': '100000109B570216',
            'portset': 'standard_portset'
        }):
            get_existing_host_mock.return_value = {}
            svc_obj_info_mock.return_value = {
                'id': '1',
                'name': 'standard_portset',
                'auto_zone_enabled': 'no'
            }
            svc_run_command_mock.return_value = {'id': '1', 'message': 'Host created'}

            with pytest.raises(AnsibleExitJson) as exc:
                obj = IBMSVChost()
                obj.apply()

            self.assertTrue(exc.value.args[0]['changed'])
            # Verify mkhost was called with force flag (not forceautozone)
            call_args = svc_run_command_mock.call_args
            self.assertIn('force', call_args[0][1])
            self.assertNotIn('forceautozone', call_args[0][1])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_create_autozone_version_check_failure(self,
                                                        svc_authorize_mock,
                                                        svc_obj_info_mock,
                                                        get_existing_host_mock):
        """Test that autozone feature fails on unsupported firmware version"""
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_host',
            'state': 'present',
            'fcwwpn': '100000109B570216',
            'portset': 'autozone_portset'
        }):
            get_existing_host_mock.return_value = {}
            svc_obj_info_mock.side_effect = [
                {'id': '1', 'name': 'autozone_portset', 'auto_zone_enabled': 'yes'},
                {'id': '00000204AEA0632C', 'name': 'system0', 'code_level': '9.1.0.0 (build 193.16.2602231501000)'}
            ]

            with pytest.raises(AnsibleFailJson) as exc:
                obj = IBMSVChost()
                obj.apply()

            self.assertTrue(exc.value.args[0]['failed'])
            msg = exc.value.args[0].get('msg', '')
            if isinstance(msg, dict):
                msg = str(msg)
            self.assertIn('autozone', msg.lower())

    # UUID-based tests for host
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_host_using_UUID(self, svc_authorize_mock, svc_obj_info_mock):
        '''Test getting existing host using UUID'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'C2A27DD7-C5DA-5078-B4F8-21D7A93C6E50',
        }):
            host_ret = [{"id": "1", "name": "ansible_host", "port_count": "1",
                         "iogrp_count": "4", "status": "offline",
                         "site_id": "", "site_name": "",
                         "host_cluster_id": "", "host_cluster_name": "",
                         "protocol": "scsi", "owner_id": "",
                         "owner_name": "", "host_id": "C2A27DD7-C5DA-5078-B4F8-21D7A93C6E50"}]
            svc_obj_info_mock.return_value = host_ret
            host = IBMSVChost().get_existing_host('C2A27DD7-C5DA-5078-B4F8-21D7A93C6E50')
            self.assertEqual('ansible_host', host['name'])
            self.assertEqual('1', host['id'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.host_probe')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_idempotency_create_host_using_UUID(self, svc_authorize_mock,
                                                host_probe_mock,
                                                get_existing_host_mock):
        '''Test idempotency when creating an existing host using UUID'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': '60050768108180ED700000000000004B',
        }):
            host_ret = [{"id": "1", "name": "ansible_host", "port_count": "1",
                         "iogrp_count": "4", "status": "offline",
                         "site_id": "", "site_name": "",
                         "host_cluster_id": "", "host_cluster_name": "",
                         "protocol": "scsi", "owner_id": "",
                         "owner_name": "", "host_id": "C2A27DD7-C5DA-5078-B4F8-21D7A93C6E50"}]
            get_existing_host_mock.return_value = host_ret
            host_probe_mock.return_value = []
            host_created = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                host_created.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_delete_host_successfully_using_UUID(self, svc_authorize_mock,
                                                 svc_run_command_mock,
                                                 get_existing_host_mock):
        '''Test deleting a host successfully using UUID'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': '60050768108180ED700000000000004B',
        }):
            host_ret = [{"id": "1", "name": "ansible_host", "port_count": "1",
                         "iogrp_count": "4", "status": "offline",
                         "site_id": "", "site_name": "",
                         "host_cluster_id": "", "host_cluster_name": "",
                         "protocol": "scsi", "owner_id": "",
                         "owner_name": "", "host_id": "C2A27DD7-C5DA-5078-B4F8-21D7A93C6E50"}]
            get_existing_host_mock.return_value = host_ret
            svc_run_command_mock.return_value = None
            host_deleted = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                host_deleted.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_idempotency_delete_host_using_UUID(self, svc_authorize_mock,
                                                get_existing_host_mock):
        '''Test idempotency when deleting a non-existing host using UUID'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': '60050768108180ED700000000000004B',
        }):
            get_existing_host_mock.return_value = []
            host_deleted = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                host_deleted.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_site_update_using_UUID(self, svc_authorize_mock,
                                         svc_run_command_mock,
                                         get_existing_host_mock):
        '''Test updating host site using UUID'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': '60050768108180ED700000000000004B',
            'site': 'site2'
        }):
            host_ret = {
                "id": "1", "name": "ansible_host", "port_count": "1",
                "iogrp_count": "4", "status": "offline",
                "site_id": "1", "site_name": "site1",
                "host_cluster_id": "", "host_cluster_name": "",
                "protocol": "scsi", "owner_id": "",
                "owner_name": "", "host_id": "C2A27DD7-C5DA-5078-B4F8-21D7A93C6E50"}
            get_existing_host_mock.return_value = host_ret
            svc_run_command_mock.return_value = None
            host_updated = IBMSVChost()
            with pytest.raises(AnsibleExitJson) as exc:
                host_updated.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_rename_host_using_UUID_old_name(self, mock_svc_authorize,
                                             svc_obj_info_mock,
                                             svc_run_command_mock):
        '''Test renaming host using UUID as old_name'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'new_host_name',
            'old_name': 'C0050768108180ED70000000000000AA',
            'state': 'present',
        }):
            svc_obj_info_mock.side_effect = [
                [],  # new name doesn't exist
                {    # old UUID exists
                    "id": "14",
                    "name": "old_host_name",
                    "host_id": "C0050768108180ED70000000000000AA",
                    "port_count": "1",
                    "iogrp_count": "4",
                    "status": "offline",
                    "site_id": "",
                    "site_name": "",
                    "host_cluster_id": "",
                    "host_cluster_name": "",
                    "protocol": "scsi",
                    "partition_name": "",
                    "draft_partition_name": "",
                    "nodes": []
                }
            ]
            svc_run_command_mock.return_value = None
            with pytest.raises(AnsibleExitJson) as exc:
                h = IBMSVChost()
                h.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_hostcluster')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_host_with_UUID_hostcluster(self, svc_authorize_mock,
                                               get_existing_host_mock,
                                               svc_run_command_mock,
                                               get_existing_hostcluster_mock):
        '''Test creating host with UUID hostcluster'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_host',
            'state': 'present',
            'fcwwpn': '100000109B570216',
            'hostcluster': 'D0050768108180ED70000000000000BB'
        }):
            get_existing_host_mock.return_value = []
            get_existing_hostcluster_mock.return_value = {
                "id": "0",
                "name": "hostcluster0",
                "status": "online",
                "host_count": "1",
                "mapping_count": "0",
                "port_count": "1",
                "protocol": "scsi",
                "owner_id": "0",
                "owner_name": "group5",
                "uuid": "D0050768108180ED70000000000000BB",
            }
            svc_run_command_mock.return_value = {
                'id': '14',
                'message': 'Host, id [14], successfully created'
            }
            with pytest.raises(AnsibleExitJson) as exc:
                h = IBMSVChost()
                h.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_idempotency_update_host_hostcluster_UUID_match(self, mock_svc_authorize,
                                                            svc_obj_info_mock,
                                                            svc_run_command_mock):
        '''Test updating host when UUID hostcluster matches existing'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_host',
            'state': 'present',
            'hostcluster': 'D0050768108180ED70000000000000BB'
        }):
            svc_obj_info_mock.side_effect = [
                {    # existing host
                    "id": "14",
                    "name": "test_host",
                    "host_id": "C0050768108180ED70000000000000AA",
                    "port_count": "1",
                    "iogrp_count": "4",
                    "status": "offline",
                    "site_id": "",
                    "site_name": "",
                    "host_cluster_id": "1",
                    "host_cluster_name": "test_hostcluster",
                    "protocol": "scsi",
                    "partition_name": "",
                    "draft_partition_name": "",
                    "nodes": []
                },
                {    # hostcluster info
                    'id': '1',
                    'name': 'test_hostcluster',
                    'uuid': 'D0050768108180ED70000000000000BB'
                }
            ]
            with pytest.raises(AnsibleExitJson) as exc:
                h = IBMSVChost()
                h.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_host_with_UUID_partition(self, mock_svc_authorize,
                                             svc_obj_info_mock,
                                             svc_run_command_mock):
        '''Test creating host with UUID partition'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_host',
            'state': 'present',
            'fcwwpn': '100000109B570216',
            'partition': 'E0050768108180ED70000000000000CC'
        }):
            svc_obj_info_mock.return_value = []
            svc_run_command_mock.return_value = {
                'id': '14',
                'message': 'Host, id [14], successfully created'
            }
            with pytest.raises(AnsibleExitJson) as exc:
                h = IBMSVChost()
                h.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_idempotency_host_partition_UUID_match(self, mock_svc_authorize,
                                                   svc_obj_info_mock,
                                                   svc_run_command_mock):
        '''Test updating host when UUID partition matches existing'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_host',
            'state': 'present',
            'partition': 'E0050768108180ED70000000000000CC'
        }):
            svc_obj_info_mock.side_effect = [
                {    # existing host
                    "id": "14",
                    "name": "test_host",
                    "host_id": "C0050768108180ED70000000000000AA",
                    "port_count": "1",
                    "iogrp_count": "4",
                    "status": "offline",
                    "site_id": "",
                    "site_name": "",
                    "host_cluster_id": "",
                    "host_cluster_name": "",
                    "protocol": "scsi",
                    "partition_name": "test_partition",
                    "draft_partition_name": "",
                    "nodes": []
                },
                {    # partition info
                    'id': '1',
                    'name': 'test_partition',
                    'uuid': 'E0050768108180ED70000000000000CC'
                }
            ]
            with pytest.raises(AnsibleExitJson) as exc:
                h = IBMSVChost()
                h.apply()
            self.assertFalse(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_update_host_with_UUID_draftpartition(self, mock_svc_authorize,
                                                  svc_obj_info_mock,
                                                  svc_run_command_mock):
        '''Test updating host with UUID draftpartition'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_host',
            'state': 'present',
            'draftpartition': 'F0050768108180ED70000000000000DD'
        }):
            svc_obj_info_mock.return_value = {
                "id": "14",
                "name": "test_host",
                "host_id": "C0050768108180ED70000000000000AA",
                "port_count": "1",
                "iogrp_count": "4",
                "status": "offline",
                "site_id": "",
                "site_name": "",
                "host_cluster_id": "",
                "host_cluster_name": "",
                "protocol": "scsi",
                "partition_name": "",
                "draft_partition_name": "",
                "nodes": []
            }
            svc_run_command_mock.return_value = None
            with pytest.raises(AnsibleExitJson) as exc:
                h = IBMSVChost()
                h.apply()
            self.assertTrue(exc.value.args[0]['changed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_idempotency_host_draftpartition_UUID_match(self, mock_svc_authorize,
                                                        svc_obj_info_mock,
                                                        svc_run_command_mock):
        '''Test updating host when UUID draftpartition matches existing'''
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test_host',
            'state': 'present',
            'draftpartition': 'F0050768108180ED70000000000000DD'
        }):
            svc_obj_info_mock.side_effect = [
                {    # existing host
                    "id": "14",
                    "name": "test_host",
                    "host_id": "C0050768108180ED70000000000000AA",
                    "port_count": "1",
                    "iogrp_count": "4",
                    "status": "offline",
                    "site_id": "",
                    "site_name": "",
                    "host_cluster_id": "",
                    "host_cluster_name": "",
                    "protocol": "scsi",
                    "partition_name": "",
                    "draft_partition_name": "test_draft_partition",
                    "nodes": []
                },
                {    # draftpartition info
                    'id': '1',
                    'name': 'test_draft_partition',
                    'uuid': 'F0050768108180ED70000000000000DD',
                    'draft': 'yes'
                }
            ]
            with pytest.raises(AnsibleExitJson) as exc:
                h = IBMSVChost()
                h.apply()
            self.assertFalse(exc.value.args[0]['changed'])


if __name__ == '__main__':
    unittest.main()
