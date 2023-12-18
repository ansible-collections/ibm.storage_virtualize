# Copyright (C) 2020 IBM CORPORATION
# Author(s): Peng Wang <wangpww@cn.ibm.com>
#            Sreshtant Bohidar <sreshtant.bohidar@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Storage Virtualize Ansible module: ibm_svc_info """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.storage_virtualize.plugins.modules.ibm_svc_info import IBMSVCGatherInfo


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


class TestIBMSVCGatherInfo(unittest.TestCase):
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
        with pytest.raises(AnsibleFailJson) as exc:
            set_module_args({})
            IBMSVCGatherInfo()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_info.IBMSVCGatherInfo.get_list')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_get_host_list_called(self, mock_svc_authorize,
                                  get_list_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'gather_subset': 'host',
        })
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertFalse(exc.value.args[0]['changed'])
        get_list_mock.assert_called_with('host', 'Host', 'lshost', False)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_the_host_result_by_gather_info(self, svc_authorize_mock,
                                            svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'gather_subset': 'host',
        })
        host_ret = [{"id": "1", "name": "ansible_host", "port_count": "1",
                     "iogrp_count": "4", "status": "offline",
                     "site_id": "", "site_name": "",
                     "host_cluster_id": "", "host_cluster_name": "",
                     "protocol": "nvme", "owner_id": "",
                     "owner_name": ""}]
        svc_obj_info_mock.return_value = host_ret
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertFalse(exc.value.args[0]['changed'])
        self.assertDictEqual(exc.value.args[0]['Host'][0], host_ret[0])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_the_host_and_vol_result_by_gather_info(self, svc_authorize_mock,
                                                    svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'gather_subset': 'host,vol',
        })
        host_ret = [{"id": "1", "name": "ansible_host", "port_count": "1",
                     "iogrp_count": "4", "status": "offline",
                     "site_id": "", "site_name": "",
                     "host_cluster_id": "", "host_cluster_name": "",
                     "protocol": "nvme", "owner_id": "",
                     "owner_name": ""}]
        vol_ret = [{"id": "0", "name": "volume_Ansible_collections",
                    "IO_group_id": "0", "IO_group_name": "io_grp0",
                    "status": "online", "mdisk_grp_id": "0",
                    "mdisk_grp_name": "Pool_Ansible_collections",
                    "capacity": "4.00GB", "type": "striped", "FC_id": "",
                    "FC_name": "", "RC_id": "", "RC_name": "",
                    "vdisk_UID": "6005076810CA0166C00000000000019F",
                    "fc_map_count": "0", "copy_count": "1",
                    "fast_write_state": "empty", "se_copy_count": "0",
                    "RC_change": "no", "compressed_copy_count": "0",
                    "parent_mdisk_grp_id": "0",
                    "parent_mdisk_grp_name": "Pool_Ansible_collections",
                    "owner_id": "", "owner_name": "", "formatting": "no",
                    "encrypt": "no", "volume_id": "0",
                    "volume_name": "volume_Ansible_collections",
                    "function": "", "protocol": "scsi"}]
        svc_obj_info_mock.side_effect = [host_ret, vol_ret]
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertFalse(exc.value.args[0]['changed'])
        self.assertDictEqual(exc.value.args[0]['Host'][0], host_ret[0])
        self.assertDictEqual(exc.value.args[0]['Volume'][0], vol_ret[0])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_vol_volgrp_population_and_volgrpsnapshot_result_by_gather_info(self, svc_authorize_mock,
                                                                            svc_obj_info_mock):
        'Test ibm_svc_info module for lsvolumepopulation, lsvolumegrouppopulation and lsvolumesgroupsnapshot'
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'gather_subset': 'volumepopulation,volumegrouppopulation,volumegroupsnapshot',
        })

        vol_population_ret = [{
            "data_to_move": "",
            "estimated_completion_time": "",
            "rate": "",
            "source_snapshot": "ssthin0",
            "source_volume_id": "2",
            "source_volume_name": "del_volume21697369620971",
            "start_time": "231127004946",
            "type": "thinclone",
            "volume_group_id": "2",
            "volume_group_name": "th_volgrp0",
            "volume_id": "11",
            "volume_name": "del_volume21697369620971-5"
        }, {
            "data_to_move": "",
            "estimated_completion_time": "",
            "rate": "",
            "source_snapshot": "ssthin0",
            "source_volume_id": "0",
            "source_volume_name": "volume0",
            "start_time": "231127004946",
            "type": "thinclone",
            "volume_group_id": "2",
            "volume_group_name": "th_volgrp0",
            "volume_id": "3",
            "volume_name": "volume0-5"
        }]

        volgrp_population_ret = [{
            "data_to_move": "",
            "estimated_completion_time": "",
            "id": "2",
            "parent_uid": "0",
            "rate": "",
            "restore_estimated_completion_time": "",
            "restore_snapshot_name": "",
            "restore_start_time": "",
            "source_snapshot": "ssthin0",
            "source_volume_group_id": "0",
            "source_volume_group_name": "volumegroup0",
            "start_time": "231127004946",
            "volume_group_name": "th_volgrp0",
            "volume_group_type": "thinclone"
        }]

        volgrp_snapshot_ret = [{
            "auto_snapshot": "no",
            "expiration_time": "",
            "id": "1",
            "matches_group": "yes",
            "name": "ssthin0",
            "operation_completion_estimate": "",
            "operation_start_time": "",
            "owner_id": "",
            "owner_name": "",
            "parent_uid": "0",
            "protection_provisioned_capacity": "33.00GB",
            "protection_written_capacity": "2.25MB",
            "safeguarded": "no",
            "state": "active",
            "time": "231127004706",
            "volume_group_id": "0",
            "volume_group_name": "volumegroup0"
        }]

        svc_obj_info_mock.side_effect = [vol_population_ret, volgrp_population_ret, volgrp_snapshot_ret]
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertFalse(exc.value.args[0]['changed'])
        self.assertDictEqual(exc.value.args[0]['VolumePopulation'][0], vol_population_ret[0])
        self.assertDictEqual(exc.value.args[0]['VolumePopulation'][1], vol_population_ret[1])
        self.assertDictEqual(exc.value.args[0]['VolumeGroupPopulation'][0], volgrp_population_ret[0])
        self.assertDictEqual(exc.value.args[0]['VolumeGroupSnapshot'][0], volgrp_snapshot_ret[0])


if __name__ == '__main__':
    unittest.main()
