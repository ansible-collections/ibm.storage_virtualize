# Copyright (C) 2020 IBM CORPORATION
# Author(s): Peng Wang <wangpww@cn.ibm.com>
#            Sreshtant Bohidar <sreshtant.bohidar@ibm.com>
#            Lavanya C R <lavanya.c.r1@ibm.com>
#            Rahul Pawar <rahul.p@ibm.com>
#            Sandip G. Rajbanshi <sandip.rajbanshi@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Storage Virtualize Ansible module: ibm_svc_info """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from unittest.mock import patch
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

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_the_volumehostmap_result_by_gather_info(self, svc_authorize_mock,
                                                     svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'gather_subset': 'vdiskhostmap',
            'objectname': 'volume_Ansible_collections'
        })
        vol_ret = [{"id": "0", "name": "volume_Ansible_collections",
                    "SCSI_id": "0", "host_id": "0", "host_name": "ansible_host",
                    "IO_group_id": "0", "IO_group_name": "io_grp0", "vdisk_UID": "600507681295018A3000000000000000",
                    "mapping_type": "private", "host_cluster_id": "",
                    "host_cluster_name": "", "protocol": "scsi"
                    }]

        svc_obj_info_mock.return_value = vol_ret
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertFalse(exc.value.args[0]['changed'])
        self.assertDictEqual(exc.value.args[0]['VdiskHostMap'][0], vol_ret[0])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_the_volumehostmap_result_without_objectname_by_gather_info(self, svc_authorize_mock,
                                                                        svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'gather_subset': 'vdiskhostmap'
        })
        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertTrue(exc.value.args[0]['failed'])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_the_systempatchs_result_by_gather_info(self, svc_authorize_mock,
                                                    svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'gather_subset': 'systempatches'
        })
        systempatches_ret = [{"id": "1", "node_id": "1",
                              "node_name": "node1", "panel_name": "78E02ZG",
                              "patch_name": "JA_TEST_PATCH_SUCCESS_2", "patch_status": "Installed",
                              }]
        svc_obj_info_mock.return_value = systempatches_ret
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertDictEqual(exc.value.args[0]['Systempatches'][0], systempatches_ret[0])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.modules.'
           'ibm_svc_info.IBMSVCGatherInfo.get_list')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_default_gather_subset_all(self, mock_svc_authorize, mock_svc_obj_info, mock_get_list):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password'
        })
        result = {
            'Volume': [],
            'Pool': [],
            'Node': [],
            'IOGroup': [],
            'Host': [],
            'HostVdiskMap': [],
            'VdiskHostMap': [],
            'HostCluster': [],
            'FCConnectivity': [],
            'FCConsistgrp': [],
            'RCConsistgrp': [],
            'VdiskCopy': [],
            'FCPort': [],
            'TargetPortFC': [],
            'iSCSIPort': [],
            'FCMap': [],
            'RemoteCopy': [],
            'Array': [],
            'System': [],
            'CloudAccount': [],
            'CloudAccountUsage': [],
            'CloudImportCandidate': [],
            'LdapServer': [],
            'Drive': [],
            'User': [],
            'Partnership': [],
            'ReplicationPolicy': [],
            'SnapshotPolicy': [],
            'VolumeGroup': [],
            'VolumePopulation': [],
            'VolumeGroupPopulation': [],
            'SnapshotSchedule': [],
            'VolumeGroupSnapshotPolicy': [],
            'VolumeSnapshot': [],
            'DnsServer': [],
            'SystemCert': [],
            'TrustStore': [],
            'Sra': [],
            'SysLogServer': [],
            'UserGrp': [],
            'EmailServer': [],
            'EmailUser': [],
            'CloudBackup': [],
            'CloudBackupGeneration': [],
            'ProvisioningPolicy': [],
            'VolumeGroupSnapshot': [],
            'CallHome': [],
            'IP': [],
            'Ownershipgroup': [],
            'Portset': [],
            'SafeguardedPolicy': [],
            'Mdisk': [],
            'SafeguardedSchedule': [],
            'EventLog': [],
            'DriveClass': [],
            'Security': [],
            'Partition': [],
            'Plugin': [],
            'Volumegroupreplication': [],
            'Quorum': [],
            'Enclosure': [],
            'Snmpserver': [],
            'Testldapserver': []
        }
        mock_svc_obj_info.return_value = {'code_level': "10.0.0.0 ###"}
        mock_get_list.return_value = {}
        with pytest.raises(AnsibleExitJson) as exc:
            info = IBMSVCGatherInfo().apply()
        self.assertFalse(exc.value.args[0]['changed'])
        for key in result:
            self.assertEqual(exc.value.args[0][key], result[key])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failed_objectname_all_gather_subset_all(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'gather_subset': 'all',
            'objectname': 'all'
        })
        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertTrue(exc.value.args[0]['failed'])
        self.assertEqual(exc.value.args[0]['msg'], "gather_subset and objectname both cannot be specified as 'all' at the same time.")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_failed_objectname_and_no_gather_subset(self, mock_svc_authorize):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'objectname': '1'
        })
        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertTrue(exc.value.args[0]['failed'])
        self.assertEqual(exc.value.args[0]['msg'], "objectname(1) is specified while gather_subset or command_list is not specified")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_command_list(self, mock_svc_authorize, mock_svc_obj_info):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'command_list': 'lsmdisk'
        })
        mdisk_out = [{
            "id": "0",
            "UID": "",
            "capacity": "1.7TB",
            "controller_name": "",
            "ctrl_LUN_#": "",
            "dedupe": "no",
            "distributed": "yes",
            "encrypt": "no",
            "mdisk_grp_id": "0",
            "mdisk_grp_name": "Pool0",
            "mode": "array",
            "name": "mdisk0",
            "over_provisioned": "no",
            "site_id": "1",
            "site_name": "site1",
            "status": "online",
            "supports_unmap": "yes",
            "tier": "tier0_flash"
        }, {
            "id": "16",
            "UID": "",
            "capacity": "1.7TB",
            "controller_name": "",
            "ctrl_LUN_#": "",
            "dedupe": "no",
            "distributed": "yes",
            "encrypt": "no",
            "mdisk_grp_id": "1",
            "mdisk_grp_name": "Pool1",
            "mode": "array",
            "name": "mdisk1",
            "over_provisioned": "no",
            "site_id": "2",
            "site_name": "site2",
            "status": "online",
            "supports_unmap": "yes",
            "tier": "tier0_flash"
        }]
        mock_svc_obj_info.return_value = mdisk_out
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertEqual(exc.value.args[0]['Mdisk'], mdisk_out)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_command_list_with_objectname(self, mock_svc_authorize, mock_svc_obj_info):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'command_list': 'lsdriveclass',
            'objectname': "1"
        })
        lsdriveclass_op = [{
            "IO_group_id": "0",
            "IO_group_name": "io_grp0",
            "RPM": "",
            "block_size": "4096",
            "candidate_count": "2",
            "capacity": "1.7TB",
            "compressed": "no",
            "fips": "no",
            "id": "0",
            "physical_capacity": "1.7TB",
            "superior_count": "2",
            "tech_type": "tier0_flash",
            "total_count": "6",
            "transport_protocol": "nvme"
        }, {
            "IO_group_id": "1",
            "IO_group_name": "io_grp1",
            "RPM": "",
            "block_size": "4096",
            "candidate_count": "3",
            "capacity": "1.7TB",
            "compressed": "no",
            "fips": "no",
            "id": "1",
            "physical_capacity": "1.7TB",
            "superior_count": "3",
            "tech_type": "tier0_flash",
            "total_count": "6",
            "transport_protocol": "nvme"
        }]

        mock_svc_obj_info.side_effect = [lsdriveclass_op, lsdriveclass_op[1]]
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertEqual(exc.value.args[0]['Driveclass'], lsdriveclass_op[1])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_gather_subset_with_objectname_all(self, mock_svc_authorize, mock_svc_obj_info):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'gather_subset': 'mdisk',
            'objectname': "all"
        })
        mdisk_concise = [{
            "id": "0",
            "UID": "",
            "capacity": "1.7TB",
            "controller_name": "",
            "ctrl_LUN_#": "",
            "dedupe": "no",
            "distributed": "yes",
            "encrypt": "no",
            "mdisk_grp_id": "0",
            "mdisk_grp_name": "Pool0",
            "mode": "array",
            "name": "mdisk0",
            "over_provisioned": "no",
            "site_id": "1",
            "site_name": "site1",
            "status": "online",
            "supports_unmap": "yes",
            "tier": "tier0_flash"
        }, {
            "id": "16",
            "UID": "",
            "capacity": "1.7TB",
            "controller_name": "",
            "ctrl_LUN_#": "",
            "dedupe": "no",
            "distributed": "yes",
            "encrypt": "no",
            "mdisk_grp_id": "1",
            "mdisk_grp_name": "Pool1",
            "mode": "array",
            "name": "mdisk1",
            "over_provisioned": "no",
            "site_id": "2",
            "site_name": "site2",
            "status": "online",
            "supports_unmap": "yes",
            "tier": "tier0_flash"
        }]

        mdisk_detailed_op = [{
            "id": "0",
            "UID": "",
            "active_WWPN": "",
            "active_iscsi_port_id": "",
            "allocated_capacity": "81.00GB",
            "balanced": "exact",
            "block_size": "",
            "capacity": "1.7TB",
            "controller_id": "",
            "controller_name": "",
            "ctrl_LUN_#": "",
            "ctrl_WWNN": "",
            "ctrl_type": "",
            "dedupe": "no",
            "distributed": "yes",
            "drive_class_id": "0",
            "drive_count": "2",
            "easy_tier_load": "",
            "effective_used_capacity": "",
            "encrypt": "no",
            "fabric_type": "",
            "fast_write_state": "empty",
            "fips_enabled": "no",
            "max_path_count": "",
            "mdisk_grp_id": "0",
            "mdisk_grp_name": "Pool0",
            "mode": "array",
            "name": "mdisk0",
            "over_provisioned": "no",
            "path_count": "",
            "physical_capacity": "1.74TB",
            "physical_free_capacity": "1.66TB",
            "preferred_WWPN": "",
            "preferred_iscsi_port_id": "",
            "provisioning_group_id": "",
            "quorum_index": "",
            "raid_level": "raid1",
            "raid_status": "online",
            "rebuild_areas_available": "0",
            "rebuild_areas_goal": "0",
            "rebuild_areas_total": "0",
            "redundancy": "1",
            "replacement_date": "",
            "site_id": "1",
            "site_name": "site1",
            "slow_write_priority": "latency",
            "spare_goal": "",
            "spare_protection_min": "",
            "status": "online",
            "strip_size": "256",
            "stripe_width": "2",
            "supports_unmap": "yes",
            "tier": "tier0_flash",
            "write_protected": "no"
        }, {
            "id": "16",
            "UID": "",
            "active_WWPN": "",
            "active_iscsi_port_id": "",
            "allocated_capacity": "15.00GB",
            "balanced": "exact",
            "block_size": "",
            "capacity": "1.7TB",
            "controller_id": "",
            "controller_name": "",
            "ctrl_LUN_#": "",
            "ctrl_WWNN": "",
            "ctrl_type": "",
            "dedupe": "no",
            "distributed": "yes",
            "drive_class_id": "1",
            "drive_count": "2",
            "easy_tier_load": "",
            "effective_used_capacity": "",
            "encrypt": "no",
            "fabric_type": "",
            "fast_write_state": "empty",
            "fips_enabled": "no",
            "max_path_count": "",
            "mdisk_grp_id": "1",
            "mdisk_grp_name": "Pool1",
            "mode": "array",
            "name": "mdisk1",
            "over_provisioned": "no",

        }]

        mock_svc_obj_info.side_effect = [mdisk_concise, mdisk_detailed_op[0], mdisk_detailed_op[0], mdisk_detailed_op[1]]
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertEqual(exc.value.args[0]['Mdisk'][0], mdisk_detailed_op[0])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_command_list_with_objectname_all(self, mock_svc_authorize, mock_svc_obj_info):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'command_list': 'lsmdisk',
            'objectname': "all"
        })
        mdisk_concise = [{
            "id": "0",
            "UID": "",
            "capacity": "1.7TB",
            "controller_name": "",
            "ctrl_LUN_#": "",
            "dedupe": "no",
            "distributed": "yes",
            "encrypt": "no",
            "mdisk_grp_id": "0",
            "mdisk_grp_name": "Pool0",
            "mode": "array",
            "name": "mdisk0",
            "over_provisioned": "no",
            "site_id": "1",
            "site_name": "site1",
            "status": "online",
            "supports_unmap": "yes",
            "tier": "tier0_flash"
        }, {
            "id": "16",
            "UID": "",
            "capacity": "1.7TB",
            "controller_name": "",
            "ctrl_LUN_#": "",
            "dedupe": "no",
            "distributed": "yes",
            "encrypt": "no",
            "mdisk_grp_id": "1",
            "mdisk_grp_name": "Pool1",
            "mode": "array",
            "name": "mdisk1",
            "over_provisioned": "no",
            "site_id": "2",
            "site_name": "site2",
            "status": "online",
            "supports_unmap": "yes",
            "tier": "tier0_flash"
        }]

        mdisk_detailed_op = [{
            "id": "0",
            "UID": "",
            "active_WWPN": "",
            "active_iscsi_port_id": "",
            "allocated_capacity": "81.00GB",
            "balanced": "exact",
            "block_size": "",
            "capacity": "1.7TB",
            "controller_id": "",
            "controller_name": "",
            "ctrl_LUN_#": "",
            "ctrl_WWNN": "",
            "ctrl_type": "",
            "dedupe": "no",
            "distributed": "yes",
            "drive_class_id": "0",
            "drive_count": "2",
            "easy_tier_load": "",
            "effective_used_capacity": "",
            "encrypt": "no",
            "fabric_type": "",
            "fast_write_state": "empty",
            "fips_enabled": "no",
            "max_path_count": "",
            "mdisk_grp_id": "0",
            "mdisk_grp_name": "Pool0",
            "mode": "array",
            "name": "mdisk0",
            "over_provisioned": "no",
            "path_count": "",
            "physical_capacity": "1.74TB",
            "physical_free_capacity": "1.66TB",
            "preferred_WWPN": "",
            "preferred_iscsi_port_id": "",
            "provisioning_group_id": "",
            "quorum_index": "",
            "raid_level": "raid1",
            "raid_status": "online",
            "rebuild_areas_available": "0",
            "rebuild_areas_goal": "0",
            "rebuild_areas_total": "0",
            "redundancy": "1",
            "replacement_date": "",
            "site_id": "1",
            "site_name": "site1",
            "slow_write_priority": "latency",
            "spare_goal": "",
            "spare_protection_min": "",
            "status": "online",
            "strip_size": "256",
            "stripe_width": "2",
            "supports_unmap": "yes",
            "tier": "tier0_flash",
            "write_protected": "no"
        }, {
            "id": "16",
            "UID": "",
            "active_WWPN": "",
            "active_iscsi_port_id": "",
            "allocated_capacity": "15.00GB",
            "balanced": "exact",
            "block_size": "",
            "capacity": "1.7TB",
            "controller_id": "",
            "controller_name": "",
            "ctrl_LUN_#": "",
            "ctrl_WWNN": "",
            "ctrl_type": "",
            "dedupe": "no",
            "distributed": "yes",
            "drive_class_id": "1",
            "drive_count": "2",
            "easy_tier_load": "",
            "effective_used_capacity": "",
            "encrypt": "no",
            "fabric_type": "",
            "fast_write_state": "empty",
            "fips_enabled": "no",
            "max_path_count": "",
            "mdisk_grp_id": "1",
            "mdisk_grp_name": "Pool1",
            "mode": "array",
            "name": "mdisk1",
            "over_provisioned": "no",

        }]
        mock_svc_obj_info.side_effect = [mdisk_concise, mdisk_detailed_op[0], mdisk_detailed_op[0], mdisk_detailed_op[1]]
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertEqual(exc.value.args[0]['Mdisk'][0], mdisk_detailed_op[0])

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_objectname_with_same_id(self, mock_svc_authorize, mock_svc_obj_info):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'command_list': 'lsvdiskaccess',
            'objectname': "all"
        })

        lsvdiskaccess_op = [{
            "vdisk_id": "0",
            "vdisk_name": "test_vol0",
            "IO_group_id": "0",
            "IO_group_name": "io_grp0"
        }, {
            "vdisk_id": "0",
            "vdisk_name": "test_vol0",
            "IO_group_id": "1",
            "IO_group_name": "io_grp1"
        }, {
            "vdisk_id": "1",
            "vdisk_name": "test_vol1",
            "IO_group_id": "1",
            "IO_group_name": "io_grp1"
        }]

        mock_svc_obj_info.side_effect = [lsvdiskaccess_op, lsvdiskaccess_op[:1]]
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertEqual(exc.value.args[0]['Vdiskaccess'], lsvdiskaccess_op)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_objecname_all_id_not_found(self, mock_svc_authorize, mock_svc_obj_info):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'command_list': 'lscloudcallhome',
            'objectname': "all"
        })

        lscloudcallhome_op = {
            "connection": "active",
            "error_sequence_number": "",
            "last_failure": "",
            "last_success": "240510104747",
            "si_tenant_id": "",
            "status": "enabled"
        }
        mock_svc_obj_info.return_value = lscloudcallhome_op
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertEqual(exc.value.args[0]['Cloudcallhome'], lscloudcallhome_op)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_objectname_all_object_has_id_but_objectname_not_valid_parameter(self, mock_svc_authorize, mock_svc_obj_info):
        '''
        This test is about checking the commands like lssiste,
        If lssite is executed with objectname (i.e. lssite <id>) then it is invalid but with objectname all it
        should show the output of lsssite without objectname
        '''
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'command_list': 'lssite',
            'objectname': "all"
        })
        lssite = [{
            "id": "1",
            "site_name": "site1"
        }, {
            "id": "2",
            "site_name": "site2"
        }, {
            "id": "3",
            "site_name": "site3"
        }]

        mock_svc_obj_info.side_effect = [lssite, None]
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertEqual(exc.value.args[0]['Site'], lssite)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_objectname_all_concise_output_same_as_detailed(self, mock_svc_authorize, mock_svc_obj_info):
        '''
        In this test, checking those commands whose output with objectname and without objectname is same like in lsportset.
        '''
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'command_list': 'lsportset',
            'objectname': "all"
        })
        lsportset_op = [{
            "id": "0",
            "host_count": "0",
            "is_default": "yes",
            "lossless": "",
            "name": "portset0",
            "owner_id": "",
            "owner_name": "",
            "port_count": "0",
            "port_type": "ethernet",
            "type": "host"
        }, {
            "id": "1",
            "host_count": "0",
            "is_default": "no",
            "lossless": "",
            "name": "portset1",
            "owner_id": "",
            "owner_name": "",
            "port_count": "0",
            "port_type": "ethernet",
            "type": "replication"
        }]

        mock_svc_obj_info.side_effect = [lsportset_op, lsportset_op[0]]
        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertEqual(exc.value.args[0]['Portset'], lsportset_op)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi.svc_obj_info')
    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_filter(self, svc_authorize_mock, svc_obj_info_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'gather_subset': 'vol',
            'filtervalue': 'name=source_vol',
        })

        filter_value_output = {
            "FC_id": "",
            "FC_name": "",
            "IO_group_id": "0",
            "IO_group_name": "io_grp0",
            "RC_change": "no",
            "RC_id": "",
            "RC_name": "",
            "capacity": "1.00GB",
            "compressed_copy_count": "0",
            "copy_count": "1",
            "encrypt": "no",
            "fast_write_state": "empty",
            "fc_map_count": "0",
            "formatting": "no",
            "function": "",
            "id": "0",
            "is_safeguarded_snapshot": "no",
            "is_snapshot": "no",
            "mdisk_grp_id": "0",
            "mdisk_grp_name": "Pool0",
            "name": "source_vol",
            "owner_id": "",
            "owner_name": "",
            "parent_mdisk_grp_id": "0",
            "parent_mdisk_grp_name": "Pool0",
            "protocol": "",
            "replication_mode": "",
            "safeguarded_snapshot_count": "0",
            "se_copy_count": "0",
            "snapshot_count": "0",
            "status": "online",
            "type": "striped",
            "vdisk_UID": "60050768128400B12800000000000000",
            "volume_group_id": "",
            "volume_group_name": "",
            "volume_id": "0",
            "volume_name": "source_vol",
            "volume_type": ""
        }
        svc_obj_info_mock.return_value = filter_value_output

        with pytest.raises(AnsibleExitJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertEqual(exc.value.args[0]['Volume'], filter_value_output)

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_fail_filtervalue_with_gather_subset_and_command_list(self, svc_authorize_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'gather_subset': 'vol',
            'command_list': 'lsvdiskcopy',
            'filtervalue': 'name=source_vol',
        })

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertEqual(exc.value.args[0]['msg'], "filtervalue must be accompanied with a single object either in gather_subset or command_list")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_fail_filtervalue_with_gather_subset_all(self, svc_authorize_mock):
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'gather_subset': 'all',
            'filtervalue': 'name=source_vol',
        })

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertEqual(exc.value.args[0]['msg'], "filtervalue is not supported when gather_subset is specified as 'all'")

    @patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.'
           'ibm_svc_utils.IBMSVCRestApi._svc_authorize')
    def test_fail_filtervalue_with_command_list(self, svc_authorize_mock):
        # Filtervalue cannot be specified for multiple commands in command_list
        set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
            'command_list': ['lsvdiskcopy', 'lssite'],
            'filtervalue': 'name=source_vol',
        })

        with pytest.raises(AnsibleFailJson) as exc:
            IBMSVCGatherInfo().apply()
        self.assertEqual(exc.value.args[0]['msg'], "filtervalue must be accompanied with a single object either in gather_subset or command_list")


if __name__ == '__main__':
    unittest.main()
