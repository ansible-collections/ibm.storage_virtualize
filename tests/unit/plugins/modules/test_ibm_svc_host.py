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
        with pytest.raises(AnsibleFailJson) as exc:
            set_module_args({})
            IBMSVChost()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_existing_host(self, svc_authorize_mock, svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
        })
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'test_host',
        })
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
        })
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'fcwwpn': '100000109B570216'
        })
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
        })
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
        })
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'absent',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
        })
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'fcwwpn': '1000001AA0570262',
            'protocol': 'scsi',
            'type': 'generic'
        })
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'fcwwpn': '1000001AA0570260:1000001AA0570261:1000001AA0570262:1000001AA0570264',
            'protocol': 'scsi',
            'type': 'generic'
        })
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'fcwwpn': '1000001AA0570264:1000001AA0570265:1000001AA0570266',
            'protocol': 'scsi',
            'type': 'generic'
        })
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'iogrp': '1:2:3',
            'protocol': 'scsi',
            'type': 'generic'
        })
        svc_obj_info_mock.side_effect = [
            [
                {"id": "0", "name": "io_grp0"},
                {"id": "1", "name": "io_grp1"},
                {"id": "2", "name": "io_grp2"},
                {"id": "3", "name": "io_grp3"},
                {"id": "4", "name": "recovery_io_grp"}
            ],
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'iogrp': '0:io_grp1:io_grp2',
            'protocol': 'scsi',
            'type': 'generic'
        })
        svc_obj_info_mock.side_effect = [
            [
                {"id": "0", "name": "io_grp0"},
                {"id": "1", "name": "io_grp1"},
                {"id": "2", "name": "io_grp2"},
                {"id": "3", "name": "io_grp3"},
                {"id": "4", "name": "recovery_io_grp"}
            ],
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'fcwwpn': '1000001AA0570264:1000001AA0570265:1000001AA0570266',
            'protocol': 'scsi',
            'type': 'generic'
        })
        obj = IBMSVChost()
        obj.existing_fcwwpn = ['1000001AA0570262', '1000001AA0570263', '1000001AA0570264']
        obj.input_fcwwpn = ['1000001AA0570264', '1000001AA0570265', '1000001AA0570266']
        self.assertEqual(obj.host_fcwwpn_update(), None)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_host_site_update(self, svc_authorize_mock, svc_obj_info_mock, src):
        set_module_args({
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
        })
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
        set_module_args({
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
        })
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
        set_module_args({
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
        })
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'old_name': 'name',
            'name': 'new_name',
            'state': 'present',
        })
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'old_name': 'ansible_host',
            'name': 'new_ansible_host',
            'state': 'present',
            'fcwwpn': True
        })

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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'iscsiname': 'iqn.1994-05.com.redhat:2e358e438b8a',
            'protocol': 'scsi',
            'type': 'generic'
        })
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'iscsiname': 'iqn.1994-05.com.redhat:2e358e438b8a,iqn.localhost.hostid.7f000001,iqn.localhost.hostid.7f000002',
            'protocol': 'scsi',
            'type': 'generic'
        })
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'iscsiname': 'iqn.1994-05.com.redhat:2e358e438b8a,iqn.localhost.hostid.7f000002',
            'protocol': 'scsi',
            'type': 'generic'
        })
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
        set_module_args({
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
        })

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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'nqn': 'nqn.2014-08.com.example:nvme:nvm-example-sn-d78434,nqn.2014-08.com.example:nvme:nvm-example-sn-d78431',
            'protocol': 'rdmanvme',
            'type': 'generic'
        })
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'partition': 'partition1'
        })
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'protocol': 'tcpnvme',
            'nqn': 'nqn.2014-08.org.nvmexpress:NVMf:uuid:644f51bf-8432-4f59-bb13-5ada20c06397'
        })
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
        set_module_args({
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
        })

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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'draftpartition': "ptn0"
        })
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'protocol': 'tcpnvme',
            'nqn': 'nqn.2014-08.org.nvmexpress:NVMf:uuid:644f51bf-8432-4f59-bb13-5ada20c06397',
            'draftpartition': "ptn0"
        })
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'draftpartition': "ptn0"
        })
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'draftpartition': "ptn0"
        })
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'nodraftpartition': True
        })
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'protocol': 'fcnvme',
            'nqn': 'nqn.2014-08.org.nvmexpress:NVMf:uuid:644f51bf-8432-4f59-bb13-5ada20c06397'
        })
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'state': 'present',
            'nqn': 'nqn.2014-08.org.nvmexpress:NVMf:uuid:644f51bf-8432-4f59-bb13-5ada20c06397'
        })

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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'protocol': 'fcscsi',
            'fdminame': '78F1CV1-1'
        })
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'name': 'test',
            'state': 'present',
            'suppressofflinealert': 'yes'
        })
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

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_iscsihost(self, svc_authorize_mock,
                              svc_run_command_mock,
                              get_existing_host_mock):
        '''
        Test to create iscsi host, should pass
        '''
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'iscsiname': 'iqn.localhost.hostid.7f000001',
            'protocol': 'iscsi',
            'portset': 'ipportset'
        })
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
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'iscsiname': 'iqn.localhost.hostid.7f000001',
            'protocol': 'iscsi'
        })

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

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_host.IBMSVChost.get_existing_host')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_run_command')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_create_fcscsihost(self, svc_authorize_mock,
                               svc_run_command_mock,
                               get_existing_host_mock):
        '''
        Test to create fcscsi host, should pass
        '''
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'state': 'present',
            'username': 'username',
            'password': 'password',
            'name': 'ansible_host',
            'fcwwpn': '5005076812113196',
            'protocol': 'fcscsi',
            'portset': 'fcportset'
        })
        host = {u'message': u'Host, id [0], '
                            u'successfully created', u'id': u'0'}
        svc_run_command_mock.return_value = host
        get_existing_host_mock.return_value = []
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
        set_module_args({
            'clustername': '{{clustername}}',
            'username': '{{username}}',
            'password': '{{password}}',
            'state': 'present',
            'name': 'host0',
            'location': 'fs9500cl-2',
            'partition': 'ha-partition-0',
            'fcwwpn': '21000024FF7D9505'
        })
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
        set_module_args({
            'clustername': '{{clustername}}',
            'username': '{{username}}',
            'password': '{{password}}',
            'state': 'present',
            'name': 'host0',
            'location': 'fs9500cl-2',
            'partition': 'ha-partition-0',
            'fcwwpn': '21000024FF7D9505'
        })
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
        set_module_args({
            'clustername': '{{clustername}}',
            'username': '{{username}}',
            'password': '{{password}}',
            'state': 'present',
            'name': 'host0',
            'location': 'fs9500cl-2',
            'fcwwpn': '21000024FF7D9505'
        })
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
        set_module_args({
            'clustername': '{{clustername}}',
            'username': '{{username}}',
            'password': '{{password}}',
            'state': 'present',
            'name': 'host0',
            'location': 'fs9500cl-2',
        })
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
        set_module_args({
            'clustername': '{{clustername}}',
            'username': '{{username}}',
            'password': '{{password}}',
            'state': 'present',
            'name': 'host0',
            'location': '',
        })
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
        set_module_args({
            'clustername': '{{clustername}}',
            'username': '{{username}}',
            'password': '{{password}}',
            'state': 'present',
            'name': 'host0',
            'location': '',
        })
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
        set_module_args({
            'clustername': '{{clustername}}',
            'username': '{{username}}',
            'password': '{{password}}',
            'state': 'present',
            'name': 'host0',
            'site': '',
        })
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
        set_module_args({
            'clustername': '{{clustername}}',
            'username': '{{username}}',
            'password': '{{password}}',
            'state': 'present',
            'name': 'host0',
            'site': '',
        })
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


if __name__ == '__main__':
    unittest.main()
