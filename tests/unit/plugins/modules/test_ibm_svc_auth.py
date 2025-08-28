# Copyright (C) 2020 IBM CORPORATION
# Author(s): Shilpi Jain <shilpi.jain1@ibm.com>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests IBM Storage Virtualize Ansible module: ibm_svc_auth """

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import unittest
import pytest
import json
from mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi
from ansible_collections.ibm.storage_virtualize.plugins.modules.ibm_svc_auth import IBMSVCauth, main
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


class TestIBMSVCauth(unittest.TestCase):
    """ a group of related Unit Tests"""
    def setUp(self):

        self.auth_patcher = patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi._svc_authorize')
        self.svc_authorize_mock = self.auth_patcher.start()
        self.addCleanup(self.auth_patcher.stop)

        # Patch svc_run_command
        self.auth_token_patcher = patch('ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils.IBMSVCRestApi.get_auth_token')
        self.auth_token_mock = self.auth_token_patcher.start()
        self.addCleanup(self.auth_token_patcher.stop)

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
                IBMSVCauth()
            print('Info: %s' % exc.value.args[0]['msg'])

    def test_module_token_returned_successfully(self):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
        }):
            self.svc_authorize_mock.return_value = None
            with pytest.raises(AnsibleExitJson) as exc:
                main()

    def test_module_token_return_failure(self):
        with set_module_args({
            'clustername': 'clustername',
            'domain': 'domain',
            'username': 'username',
            'password': 'password',
        }):
            self.svc_authorize_mock.return_value = 'a2ca1d31d663ce181b955c07f51a000c2f75835b3d87735d1f334cf4b913880c'
            with pytest.raises(AnsibleFailJson) as exc:
                main()


if __name__ == '__main__':
    unittest.main()
