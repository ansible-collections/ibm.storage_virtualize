#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2022 IBM CORPORATION
# Author(s): Sandip Gulab Rajbanshi <sandip.rajbanshi@ibm.com>

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: ibm_sv_manage_system_certificate
short_description: This module manages system certificates and truststore for replication, high availability and
                   FlashSystem grid on IBM Storage Virtualize family systems
version_added: '3.1.0'
description:
  - Ansible interface to manage mktruststore, rmtruststore, chsystemcertstore and chsystemcert commands.
  - This module can be used to set up mutual TLS (mTLS) for inter-system communication which involves
    Policy-based Replication, Policy-based High Availability, and Flashsystem grid.
  - This module transfers the certificate between both local and remote system using SCP command.
  - This module works on SSH and uses paramiko to establish an SSH connection.
  - This module will only export root CA certificate for creating truststore.
options:
    clustername:
        description:
            - The hostname or management IP of the Storage Virtualize system.
        required: true
        type: str
    domain:
        description:
            - Domain for the Storage Virtualize storage system.
            - Valid when hostname is used for the parameter I(clustername).
        type: str
    username:
        description:
            - Username for the Storage Virtualize system.
        type: str
        required: true
    password:
        description:
            - Password for the Storage Virtualize system.
        type: str
        required: true
    log_path:
        description:
            - Path of debug log file.
        type: str
    state:
        description:
            - Creates (C(present)) or deletes (C(absent)) a truststore.
        choices: [ present, absent ]
        required: true
        type: str
    primary_truststore_name:
        description:
            - Specifies the name of the truststore on the primary system.
        required: true
        type: str
    remote_truststore_name:
        description:
            - Specifies the name of the truststore on the remote system.
        type: str
    remote_clustername:
        description:
            - Specifies the name of the partner remote cluster with which mTLS needs to be setup.
        type: str
    remote_domain:
        description:
            - Domain for the Storage Virtualize storage system.
            - Valid when hostname is used for the parameter I(remote_clustername).
        type: str
    remote_username:
        description:
            - Username for remote cluster.
        type: str
    remote_password:
        description:
            - Password for remote cluster.
        type: str
author:
    - Sandip Gulab Rajbanshi (@Sandip-Rajbanshi)
'''

EXAMPLES = '''
- name: Create truststore on both systems
  ibm.storage_virtualize.ibm_sv_manage_system_certificate:
    clustername: "{{ primary_clustername }}"
    username: "{{ primary_username }}"
    password: "{{ primary_password }}"
    remote_clustername: "{{ secondary_clustername }}"
    remote_username: "{{ secondary_username }}"
    remote_password: "{{ secondary_password }}"
    primary_truststore_name: "{{ primary_truststore_name }}"
    remote_truststore_name: "{{ secondary_truststore_name }}"
    state: present
    log_path: "{{ log_path | default('/tmp/playbook.debug') }}"

- name: Remove truststore on both systems
  ibm.storage_virtualize.ibm_sv_manage_system_certificate:
    clustername: "{{ primary_clustername }}"
    username: "{{ primary_username }}"
    password: "{{ primary_password }}"
    remote_clustername: "{{ secondary_clustername }}"
    remote_username: "{{ secondary_username }}"
    remote_password: "{{ secondary_password }}"
    primary_truststore_name: "{{ primary_truststore_name }}"
    remote_truststore_name: "{{ secondary_truststore_name }}"
    state: absent
    log_path: "{{ log_path | default('/tmp/playbook.debug') }}"

- name: Remove truststore on single system
  ibm.storage_virtualize.ibm_sv_manage_system_certificate:
    clustername: "{{ clustername }}"
    username: "{{ username }}"
    password: "{{ password }}"
    primary_truststore_name: "{{ truststore_name }}"
    state: absent
    log_path: "{{ log_path | default('/tmp/playbook.debug') }}"
'''

RETURN = '''#'''

from traceback import format_exc
import json
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils import (
    svc_ssh_argument_spec,
    get_logger,
    is_feature_supported
)
from ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_ssh import IBMSVCssh
from ansible.module_utils._text import to_native


class IBMSVManageSystemCert:

    def __init__(self):
        argument_spec = svc_ssh_argument_spec()
        argument_spec.update(
            dict(
                primary_truststore_name=dict(
                    type='str',
                    required=True
                ),
                remote_truststore_name=dict(
                    type='str'
                ),
                state=dict(
                    type='str',
                    choices=['present', 'absent'],
                    required=True
                ),
                remote_clustername=dict(
                    type='str'
                ),
                remote_domain=dict(
                    type='str'
                ),
                remote_username=dict(
                    type='str'
                ),
                remote_password=dict(
                    type='str',
                    no_log=True
                ),
            )
        )

        self.module = AnsibleModule(argument_spec=argument_spec,
                                    supports_check_mode=False,
                                    required_if=[('state', 'present',
                                                  ('remote_clustername',
                                                   'remote_username',
                                                   'remote_password',
                                                   'remote_truststore_name'))])

        # logging setup
        self.log_path = self.module.params['log_path']
        log = get_logger(self.__class__.__name__, self.log_path)
        self.log = log.info

        # Required parameters
        self.state = self.module.params['state']
        self.clustername = self.module.params['clustername']
        self.username = self.module.params.get('username', '')
        self.password = self.module.params.get('password', '')
        self.primary_truststore_name = self.module.params['primary_truststore_name']

        # Optional parameters
        self.domain = self.module.params.get('domain', '')
        self.remote_clustername = self.module.params.get('remote_clustername', '')
        self.remote_domain = self.module.params.get('remote_domain', '')
        self.remote_username = self.module.params.get('remote_username', '')
        self.remote_password = self.module.params.get('remote_password', '')
        self.remote_truststore_name = self.module.params['remote_truststore_name']

        # Dynamic variables
        self.changed = False
        self.msg = ''

        self.primary_ssh_client = IBMSVCssh(
            module=self.module,
            clustername=self.clustername,
            domain=self.domain,
            username=self.username,
            password=self.password,
            look_for_keys=False,
            key_filename=None,
            log_path=self.log_path
        )
        if self.remote_clustername:
            self.remote_ssh_client = IBMSVCssh(
                module=self.module,
                clustername=self.remote_clustername,
                domain=self.remote_domain,
                username=self.remote_username,
                password=self.remote_password,
                look_for_keys=False,
                key_filename=None,
                log_path=self.log_path
            )
        else:
            self.remote_ssh_client = None

        self.basic_checks()

    def basic_checks(self):
        pass

    def raise_error(self, stderr):
        message = stderr.read().decode('utf-8')
        if len(message) > 0:
            self.log("%s", message)
            self.module.fail_json(msg=message)
        else:
            message = 'Unknown error received.'
            self.module.fail_json(msg=message)

    # This function will execute the command on SVC and return the output/error
    def _execute_command(self, cmd, ssh_client):
        self.log("Executing command: %s", cmd)
        stdin, stdout, stderr = ssh_client.client.exec_command(cmd)
        result = stdout.read().decode('utf-8')
        rc = stdout.channel.recv_exit_status()

        if rc > 0:
            message = stderr.read().decode('utf-8')
            self.log("Error in executing command: %s, error detail: %s", cmd, message)
            if 'lstruststore' in cmd or 'lssystemcertstore' in cmd:
                return None
            self.raise_error(stderr)
        else:
            if not result:
                return None
            if cmd != "lssystemcertstore -json internal_communication":
                self.log("%s command output: %s", cmd, result)
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return result

    # This function will exchange the certificate between source and target system using SCP command
    def _exchange_certificate(self, cmd, ssh_client, password):
        stdin, stdout, stderr = ssh_client.client.exec_command(cmd,
                                                               get_pty=True,
                                                               timeout=60 * 1.5)
        result = ''
        while not stdout.channel.recv_ready():
            data = stdout.channel.recv(1024)
            self.log(str(data, 'utf-8'))
            if data:
                if b'Warning: Permanently added' in data:
                    while not (b'Password' in data or b'password' in data):
                        data = stdout.channel.recv(1024)
                if b'Password' in data or b'password' in data:
                    stdin.write("{0}\n".format(password))
                    stdin.flush()
                else:
                    if isinstance(data, bytes):
                        result += data.decode('utf-8')
                    else:
                        result += data.read().decode('utf-8')
                break
        if isinstance(stdout, bytes):
            # Decode the bytes object directly
            result += stdout.decode('utf-8')
        else:
            result += stdout.read().decode('utf-8')
        rc = stdout.channel.recv_exit_status()
        if rc > 0:
            if isinstance(stderr, bytes):
                message = stderr.decode('utf-8')
            else:
                message = stderr.read().decode('utf-8')
            self.log("Error in executing command: %s", cmd)
            if not len(message) > 1:
                if len(result) > 1:
                    err = result.replace('\rPassword:\r\n', '')
                    self.log("Error: %s", err)
                    if err:
                        self.module.fail_json(msg=err)
                self.module.fail_json(msg='Unknown error received')
            else:
                self.module.fail_json(msg=message)
        else:
            self.log(result)
        return None

    # This function will create truststore and internally will be exporting
    # and exchanging the certificate.
    def create_truststore(self, details):
        # =================================================================
        # An internal function to export and exchange the certificate and return name
        # of certificate file.
        def export_exchange_cert(cert_type):
            if cert_type == 'default':
                export_cmd = "chsystemcertstore -exportrootca -scope default"
                certificate_name = 'rootcacertificate.pem'
            elif cert_type == 'internal_communication':
                export_cmd = "chsystemcertstore -exportrootca -scope internal_communication"
                certificate_name = 'system_rootcacertificate_slot_3.pem'
            elif cert_type == 'root_ca':  # 8.7.3
                export_cmd = "chsystemcert -exportrootcacert"
                certificate_name = 'rootcacertificate.pem'
            else:  # legacy
                export_cmd = "chsystemcert -export"
                certificate_name = 'certificate.pem'

            self._execute_command(export_cmd, source_system_ssh_client)
            target_certificate_name = certificate_name.split('.', maxsplit=1)[0] + "_" + str(
                source_system_clustername.replace(".", "_")) + '.pem'

            scp_cmd = 'scp -O -o stricthostkeychecking=no -o UserKnownHostsFile=/dev/null '\
                '/dumps/{0} {1}@{2}:/tmp/{3}'.format(
                    certificate_name,
                    target_system_username,
                    target_system_clustername,
                    target_certificate_name)

            self.log('Command to be executed for exchanging certificate: %s', scp_cmd)
            self._exchange_certificate(scp_cmd, source_system_ssh_client,
                                       target_system_password)
            self.log('Certificate copied to %s successfully', target_system_clustername)
            return (certificate_name, target_certificate_name)
        # =================================================================

        # Local variables defined to store info of source and target system
        # because source and target can varry based on primary and remote system.
        source_system_ssh_client = details['source_system_ssh_client']
        source_system_code_level = details["source_code_level"]
        source_system_clustername = details['source_system_clustername']
        target_system_ssh_client = details['target_system_ssh_client']
        target_system_truststore_name = details['target_system_truststore_name']
        target_system_username = details['target_system_username']
        target_system_clustername = details['target_system_clustername']
        target_system_password = details['target_system_password']
        target_system_code_level = details["target_code_level"]

        certstore_cmds_supported = is_feature_supported('certstore_cmds',
                                                        source_system_code_level.split(" ")[0])
        if certstore_cmds_supported:
            icc_info_cmd = "lssystemcertstore -json internal_communication"
            icc_info = self._execute_command(icc_info_cmd, source_system_ssh_client)

            if icc_info:
                certificate_name, target_certificate_name = export_exchange_cert('internal_communication')
            else:
                certificate_name, target_certificate_name = export_exchange_cert('default')

        else:
            source_build_version = float(target_system_code_level.split(" ")[0][:3])
            source_patch = target_system_code_level.split(" ")[0][4:5]
            if float(source_build_version) == 8.7 and source_patch == "3":
                certificate_name, target_certificate_name = export_exchange_cert('root_ca')
            else:
                certificate_name, target_certificate_name = export_exchange_cert('legacy')

        if certificate_name == "certificate.pem":
            '''
            Certificate is legacy means system is below 8.7.3.0
            so system does not have support for grid.
            '''
            create_truststore_cmd = 'mktruststore -name {0} -file /tmp/{1} -restapi on -json'.format(
                target_system_truststore_name, target_certificate_name)
        else:
            target_build_version = float(target_system_code_level.split(" ")[0][:3])
            target_patch = target_system_code_level.split(" ")[0][4:5]

            if target_build_version > 8.7:
                create_truststore_cmd = 'mktruststore -name {0} -file /tmp/{1} -grid on -json'.format(
                    target_system_truststore_name, target_certificate_name)
            elif target_build_version == 8.7 and target_patch == "3":
                create_truststore_cmd = 'mktruststore -name {0} -file /tmp/{1} -flashgrid on -json'.format(
                    target_system_truststore_name, target_certificate_name)
            else:
                create_truststore_cmd = 'mktruststore -name {0} -file /tmp/{1} -restapi on -json'.format(
                    target_system_truststore_name, target_certificate_name)

        self._execute_command(create_truststore_cmd, target_system_ssh_client)
        self.log('Truststore %s created successfully on cluster %s. ',
                 target_system_truststore_name, target_system_clustername)
        return None

    def remove_truststore(self, details):
        source_system_truststore_name = details['source_system_truststore_name']
        source_system_ssh_client = details['source_system_ssh_client']
        remove_truststore_cmd = "rmtruststore {0}".format(source_system_truststore_name)
        self._execute_command(remove_truststore_cmd, source_system_ssh_client)
        self.log('Truststore %s removed successfully from cluster %s. ',
                 source_system_truststore_name, details['source_system_clustername'])
        return None

    def apply(self):
        systems_details = {
            'primary': {
                'source_system_ssh_client': self.primary_ssh_client,
                'source_system_truststore_name': self.primary_truststore_name,
                'source_system_clustername': self.clustername,
                'target_system_ssh_client': self.remote_ssh_client,
                'target_system_truststore_name': self.remote_truststore_name,
                'target_system_username': self.remote_username,
                'target_system_clustername': self.remote_clustername,
                'target_system_password': self.remote_password
            },
            'remote': {
                'source_system_ssh_client': self.remote_ssh_client,
                'source_system_truststore_name': self.remote_truststore_name,
                'source_system_clustername': self.remote_clustername,
                'target_system_ssh_client': self.primary_ssh_client,
                'target_system_truststore_name': self.primary_truststore_name,
                'target_system_username': self.username,
                'target_system_clustername': self.clustername,
                'target_system_password': self.password
            }
        }

        if self.state == 'present':
            self.primary_system_info = None
            self.remote_system_info = None

            for system, details in systems_details.items():
                truststore_info_cmd = "lstruststore -json {0}".format(
                    details['target_system_truststore_name'])
                truststore_data = self._execute_command(truststore_info_cmd,
                                                        details['target_system_ssh_client'])
                if truststore_data is None:
                    if not self.primary_system_info:
                        self.primary_system_info = self._execute_command("lssystem -json", self.primary_ssh_client)
                        systems_details['primary']['source_code_level'] = self.primary_system_info['code_level']
                        systems_details['remote']['target_code_level'] = self.primary_system_info['code_level']
                    if not self.remote_system_info:
                        self.remote_system_info = self._execute_command("lssystem -json", self.remote_ssh_client)
                        systems_details['primary']['target_code_level'] = self.remote_system_info['code_level']
                        systems_details['remote']['source_code_level'] = self.remote_system_info['code_level']

                    self.create_truststore(details)
                    self.changed = True
                    self.msg += 'Truststore {0} created successfully on cluster {1}. '.format(
                        details['target_system_truststore_name'], details['target_system_clustername'])
                else:
                    self.log('Truststore %s already exists on cluster %s. ',
                             details['target_system_truststore_name'], details['target_system_clustername'])
                    self.msg += 'Truststore {0} already exists on cluster {1}. '.format(
                        details['target_system_truststore_name'], details['target_system_clustername'])
        else:
            for system, details in systems_details.items():
                if details['source_system_ssh_client']:
                    truststore_info_cmd = "lstruststore {0}".format(
                        details['source_system_truststore_name'])
                    truststore_data = self._execute_command(truststore_info_cmd, details['source_system_ssh_client'])
                    if truststore_data:
                        self.remove_truststore(details)
                        self.changed = True
                        self.msg += 'Truststore {0} removed successfully from cluster {1}. '.format(
                            details['source_system_truststore_name'], details['source_system_clustername'])
                    else:
                        self.log("Truststore %s does not exist, or already removed from cluster %s. ",
                                 details['source_system_truststore_name'],
                                 details['source_system_clustername'])

                        self.msg += 'Truststore {0} does not exist, or already removed from cluster {1}. '.format(
                            details['source_system_truststore_name'], details['source_system_clustername'])

        self.module.exit_json(
            changed=self.changed,
            msg=self.msg
        )


def main():
    v = IBMSVManageSystemCert()
    try:
        v.apply()
    except Exception as e:
        v.log('Exception in apply(): \n%s', format_exc())
        v.module.fail_json(msg='Module failed. Error [%s].' % to_native(e))


if __name__ == '__main__':
    main()
