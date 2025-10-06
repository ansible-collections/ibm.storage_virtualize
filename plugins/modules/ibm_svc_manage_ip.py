#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2022 IBM CORPORATION
# Author(s): Sreshtant Bohidar <sreshtant.bohidar@ibm.com>
#            Rahul Pawar <rahul.p@ibm.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: ibm_svc_manage_ip
short_description: This module manages IP provisioning on IBM Storage Virtualize family systems
description:
  - Ansible interface to manage 'mkip' and 'rmip' commands.
  - This module can run on all IBM Storage Virtualize systems running on 8.4.2.0 or later.
version_added: "1.8.0"
options:
    state:
        description:
            - Creates (C(present)) or removes (C(absent)) an IP address.
        choices: [ present, absent ]
        required: true
        type: str
    clustername:
        description:
            - The hostname or management IP of the Storage Virtualize system.
        type: str
        required: true
    domain:
        description:
            - Domain for the Storage Virtualize system.
            - Valid when hostname is used for the parameter I(clustername).
        type: str
    username:
        description:
            - REST API username for the Storage Virtualize system.
            - The parameters I(username) and I(password) are required if not using I(token) to authenticate a user.
        type: str
    password:
        description:
            - REST API password for the Storage Virtualize system.
            - The parameters I(username) and I(password) are required if not using I(token) to authenticate a user.
        type: str
    token:
        description:
            - The authentication token to verify a user on the Storage Virtualize system.
            - To generate a token, use the ibm_svc_auth module.
        type: str
    node:
        description:
            - Specifies the name of the node.
        type: str
    port:
        description:
            - Specifies a port ranging from 1 - 16 to which IP shall be assigned.
        type: int
    portset:
        description:
            - Specifies the name of the portset object.
        type: str
    ip_address:
        description:
            - Specifies a valid ipv4/ipv6 address.
        type: str
        required: true
    subnet_prefix:
        description:
            - Specifies the prefix of subnet mask.
            - Required when I(state=present).
        type: int
    gateway:
        description:
            - Specifies the gateway address.
            - Applies when I(state=present).
        type: str
    vlan:
        description:
            - Specifies a vlan id ranging from 1 - 4096.
            - Applies when I(state=present).
        type: int
    resetgateway:
        description:
            - Specifies whether to reset the gateway to None.
            - Applies when I(state=present).
        type: bool
        default: false
        version_added: '3.1.0'
    resetvlan:
        description:
            - Specifies whether to reset the vlan to None.
            - Applies when I(state=present).
        type: bool
        default: false
        version_added: '3.1.0'
    old_ip_address:
        description:
            - Specifies the old IP address to be changed.
            - If not provided, the value of I(ip_address) will be used.
            - Applies when I(state=present).
        type: str
        version_added: '3.1.0'
    shareip:
        description:
            - Specifies the flag when IP is shared between multiple portsets.
            - Applies when I(state=present).
        type: bool
    validate_certs:
        description:
            - Validates certification.
        default: false
        type: bool
    log_path:
        description:
            - Path of debug log file.
        type: str
author:
    - Sreshtant Bohidar(@Sreshtant-Bohidar)
notes:
    - This module supports C(check_mode).
'''

EXAMPLES = '''
- name: Create IP provisioning
  ibm.storage_virtualize.ibm_svc_manage_ip:
   clustername: "{{ cluster }}"
   username: "{{ username }}"
   password: "{{ password }}"
   log_path: /tmp/playbook.debug
   node: node1
   port: 1
   portset: portset0
   ip_address: x.x.x.a
   subnet_prefix: 20
   gateway: x.x.x.y
   vlan: 1
   shareip: true
   state: present
- name: Change IP provisioning
  ibm.storage_virtualize.ibm_svc_manage_ip:
   clustername: "{{ cluster }}"
   username: "{{ username }}"
   password: "{{ password }}"
   log_path: /tmp/ansible.log
   portset: test_mgmt1
   old_ip_address: x.x.x.a
   ip_address: x.x.x.b
   subnet_prefix: 20
   gateway: x.x.x.y
   vlan: 1
   state: present
- name: Reset Vlan and Gateway of an IP
  ibm.storage_virtualize.ibm_svc_manage_ip:
   clustername: "{{ cluster }}"
   username: "{{ username }}"
   password: "{{ password }}"
   log_path: /tmp/ansible.log
   portset: test_mgmt1
   ip_address: x.x.x.b
   subnet_prefix: 20
   resetgateway: true
   resetvlan: true
   state: present
- name: Remove IP provisioning
  ibm.storage_virtualize.ibm_svc_manage_ip:
   clustername: "{{ cluster }}"
   username: "{{ username }}"
   password: "{{ password }}"
   log_path: /tmp/playbook.debug
   ip_address: x.x.x.x
   state: absent
- name: Create IP provisioning for management portset
  ibm.storage_virtualize.ibm_svc_manage_ip:
   clustername: "{{ cluster }}"
   username: "{{ username }}"
   password: "{{ password }}"
   log_path: /tmp/playbook.debug
   node: node1
   portset: mgmt_portset
   ip_address: x.x.x.a
   subnet_prefix: 20
   gateway: x.x.x.y
   vlan: 1
   shareip: true
   state: present
'''

RETURN = '''#'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.storage_virtualize.plugins.module_utils.ibm_svc_utils import IBMSVCRestApi, svc_argument_spec, get_logger
from ansible.module_utils._text import to_native


class IBMSVCIp(object):
    def __init__(self):
        argument_spec = svc_argument_spec()
        argument_spec.update(
            dict(
                node=dict(type='str'),
                state=dict(type='str', required=True, choices=['present', 'absent']),
                port=dict(type='int'),
                portset=dict(type='str'),
                ip_address=dict(type='str', required=True),
                subnet_prefix=dict(type='int'),
                gateway=dict(type='str'),
                vlan=dict(type='int'),
                shareip=dict(type='bool'),
                old_ip_address=dict(type='str'),
                resetgateway=dict(type='bool', default=False),
                resetvlan=dict(type='bool', default=False)
            )
        )

        mutually_exclusive = [
            ['gateway', 'resetgateway'],
            ['vlan', 'resetvlan'],
        ]
        self.module = AnsibleModule(argument_spec=argument_spec,
                                    required_if=[
                                        ('state', 'present', ['ip_address', 'subnet_prefix']),
                                        ('state', 'absent', ['ip_address'])
                                    ],
                                    mutually_exclusive=mutually_exclusive,
                                    supports_check_mode=True)

        # logging setup
        log_path = self.module.params['log_path']
        log = get_logger(self.__class__.__name__, log_path)
        self.log = log.info

        # Required
        self.state = self.module.params['state']
        self.ip_address = self.module.params.get('ip_address', False)

        # Optional
        self.portset = self.module.params.get('portset', None)
        self.subnet_prefix = self.module.params.get('subnet_prefix', None)
        self.gateway = self.module.params.get('gateway', None)
        self.vlan = self.module.params.get('vlan', None)
        self.shareip = self.module.params.get('shareip', None)
        self.port = self.module.params.get('port', None)
        self.old_ip_address = self.module.params.get('old_ip_address', None)
        self.resetgateway = self.module.params.get('resetgateway', False)
        self.resetvlan = self.module.params.get('resetvlan', False)
        self.node = self.module.params.get('node', None)

        # Initialize changed variable
        self.changed = False

        # creating an instance of IBMSVCRestApi
        self.restapi = IBMSVCRestApi(
            module=self.module,
            clustername=self.module.params['clustername'],
            domain=self.module.params['domain'],
            username=self.module.params['username'],
            password=self.module.params['password'],
            validate_certs=self.module.params['validate_certs'],
            log_path=log_path,
            token=self.module.params['token']
        )

    def basic_checks(self):
        if self.state == 'absent':
            not_required_when_absent = {
                'old_ip_address': self.old_ip_address,
                'subnet_prefix': self.subnet_prefix,
                'gateway': self.gateway,
                'vlan': self.vlan,
                'shareip': self.shareip,
                'node': self.node,
                'port': self.port
            }
            not_applicable_absent = [item for item, value in not_required_when_absent.items() if value]
            if not_applicable_absent:
                self.module.fail_json(msg="The parameter {0} are not applicable when state is absent.".format(not_applicable_absent))

    def get_ip_info(self, ip_address):
        all_data = self.restapi.svc_obj_info(cmd='lsip', cmdopts=None, cmdargs=None)
        ip_data = [item for item in all_data if item['IP_address'] == ip_address]
        ip_addr = None

        if not ip_data:
            self.log('No IP found')
            return None

        if self.portset:
            ip_addr = next((item for item in ip_data if item['portset_name'] == self.portset), None)
            if not ip_addr and not self.shareip and self.state == 'present':
                self.module.fail_json(
                    msg="IP {0} already exists. Portset cannot be changed. To create shared data IP, use shareip parameter.".format(ip_address)
                )
        else:
            if len(ip_data) > 1:
                self.module.fail_json(
                    msg="Multiple objects found with IP {0}. Please specify portset.".format(ip_address)
                )
            ip_addr = ip_data[0]

        return ip_addr

    def create_ip(self):
        if self.module.check_mode:
            self.changed = True
            return
        command = 'mkip'
        command_options = {
            'ip': self.ip_address,
            'prefix': self.subnet_prefix
        }
        if self.gateway:
            command_options['gw'] = self.gateway
        for field in ['node', 'port', 'portset', 'vlan', 'shareip']:
            value = getattr(self, field, None)
            if value:
                command_options[field] = value

        result = self.restapi.svc_run_command(command, command_options, cmdargs=None)
        self.log("create IP result %s", result)
        self.changed = True

    def ip_probe(self, data):
        props = {}

        if self.old_ip_address and self.ip_address != data['IP_address']:
            props['ip_address'] = self.ip_address
        if self.subnet_prefix != int(data['prefix']):
            props['prefix'] = self.subnet_prefix
        if self.node and (self.node != data['node_name']):
            props['node'] = self.node
        if self.port and (self.port != int(data['port_id'])):
            props['port'] = self.port

        if self.gateway and (self.gateway != data['gateway']):
            props['gateway'] = self.gateway
        if self.resetgateway and data['gateway']:
            props['gateway'] = ""
        if self.vlan and (self.vlan != data['vlan']):
            props['vlan'] = self.vlan
        if self.resetvlan and data['vlan']:
            props['vlan'] = ""

        self.log("IP probe props='%s'", props)
        return props

    def update_ip(self, old_data, modify):
        if self.module.check_mode:
            self.changed = True
            return

        unsupported_parameters = ['node', 'port']
        unsupported_exists = [param for param in unsupported_parameters if param in modify]
        if unsupported_exists:
            self.module.fail_json(msg=f"Update is not supported for parameter(s): {', '.join(unsupported_exists)}")

        command = 'chip'
        command_options = {}
        command_options['ip'] = self.ip_address
        cmdargs = [old_data['id']]

        command_options['ip'] = modify.get('ip_address', old_data['IP_address'])
        command_options['prefix'] = modify.get('prefix', old_data['prefix'])

        if 'gateway' in modify and modify['gateway'] != "":
            command_options['gw'] = modify['gateway']
        elif not self.resetgateway and old_data['gateway']:
            command_options['gw'] = old_data['gateway']

        if 'vlan' in modify and modify['vlan'] != "":
            command_options['vlan'] = modify['vlan']
        elif not self.resetvlan and old_data['vlan']:
            command_options['vlan'] = old_data['vlan']

        self.restapi.svc_run_command(command, command_options, cmdargs)
        self.log("IP parameters successfully changed.")
        self.changed = True

    def remove_ip(self, ip_address_id):
        if self.module.check_mode:
            self.changed = True
            return
        command = 'rmip'
        command_options = None
        cmdargs = [ip_address_id]
        self.restapi.svc_run_command(command, command_options, cmdargs)
        self.changed = True
        self.log("IP removed")

    def apply(self):
        msg = None
        self.basic_checks()

        ip_data = None
        if self.old_ip_address:
            if self.old_ip_address == self.ip_address:
                ip_data = self.get_ip_info(self.old_ip_address)
            else:
                old_data = self.get_ip_info(self.old_ip_address)
                new_data = self.get_ip_info(self.ip_address)
                if not old_data:
                    self.module.fail_json(msg="Ip address [{0}] does not exists.".format(self.old_ip_address))
                elif new_data:
                    self.module.fail_json(msg="Ip address [{0}] already exists.".format(self.ip_address))
                else:
                    ip_data = old_data
        else:
            ip_data = self.get_ip_info(self.ip_address)

        if self.state == 'present':
            if not ip_data:
                self.create_ip()
                msg = "IP address {0} has been created.".format(self.ip_address)
            else:
                modify = self.ip_probe(ip_data)
                if modify:
                    self.update_ip(ip_data, modify)
                    msg = "IP address {0} changed.".format(self.ip_address)
                else:
                    msg = 'No modifications done.'
        else:
            if ip_data:
                self.remove_ip(ip_data['id'])
                msg = "IP address {0} has been removed.".format(self.ip_address)
            else:
                msg = "IP address {0} does not exist.".format(self.ip_address)
                if self.portset:
                    msg = "IP address {0} with specified portset does not exist.".format(self.ip_address)

        self.module.exit_json(msg=msg, changed=self.changed)


def main():
    v = IBMSVCIp()
    try:
        v.apply()
    except Exception as e:
        v.log("Exception in apply(): \n%s", format_exc())
        v.module.fail_json(msg="Module failed. Error [%s]." % to_native(e))


if __name__ == '__main__':
    main()
