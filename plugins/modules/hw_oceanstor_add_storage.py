#!/usr/bin/python

# (c) 2020, huawei, Inc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.oceanstor_series.oceanstor.plugins.module_utils.oceanstor.oceanstor_add_storage \
    import OceanStorStorage

DOCUMENTATION = """
---
module: hw_oceanstor_add_storage
short_description: Huawei OceanStor add storage node.
description:
    - Huawei OceanStor add storage node.
author: liulimin (l00557609)
options:
    param:
        api_url: float ip address
        api_port: port, default is 8088
        username:
        password:
        servers: server information to be added.
        step: check_status or add_node
    test:
        description:
            - Add OceanStor node
            - Check add OceanStor node status
        type: bool
        default: false
notes:
    - NA
"""

EXAMPLES = """
        - name: Add Huawei OceanStor Storage
        hw_oceanstor_add_storage:
            api_url: "1.1.1.1"
            api_port: "8088"
            username: "admin"
            password: "admin"
            servers: "[{"model": null, "slot_number": "", "name":"",
                        "serial_number": "",
                        "management_internal_ip": "1.1.1.1",
                        "cabinet": "1", "user_name": "root",
                        "password": "***","root_password": "***",
                        role:["management","storage"],
                        "authentication_mode": "password"}]"
            step: "add_node"
        become: yes
"""

RETURN = """
msg:
    description: Success message
    returned: on success
    type: str
    sample: The settings have been updated.
"""


class HuaweiOceanStorAddStorage(object):
    def __init__(self):
        ansible_options = dict(api_url=dict(type="str", required=True),
                               api_port=dict(type="int", required=True),
                               username=dict(type="str", required=True),
                               token=dict(type="str", required=False),
                               password=dict(type="str", required=True, no_log=True),
                               servers=dict(type="list", required=True),
                               validate_certs=dict(type="bool", default=False, required=False),
                               default_root_password=dict(type="str", default='', required=False),
                               service_type=dict(type="str", default="agent", choices=["agent", "all"]),
                               step=dict(type="str", default="check_status",
                                         choices=["get_token", "add_node", "check_add_storage_status",
                                                  "check_status", "install_node"]))

        required_together = [["api_url", "api_port", "username", "password", "servers"]]

        self.module = AnsibleModule(argument_spec=ansible_options, required_together=required_together)
        self.base_url = self._format_base_url()

        username = self.module.params["username"]
        password = self.module.params["password"]
        token = self.module.params["token"]

        if token:
            self.module.warn(token)

        self.oceanstor = OceanStorStorage(self.base_url, username, password, token)

    def _format_base_url(self):
        url = self.module.params["api_url"]
        port = self.module.params["api_port"]
        return "https://{0}:{1}".format(url, port)

    def _refactoring_param_for_add_node(self, server, server_default):
        """检查添加的节点状态，重构参数
        """
        server_params = {}
        if "root_password" in server and server["root_password"]:
            server_params['password'] = server['root_password']
            server_params['root_password'] = server['root_password']
        elif self.module.params["default_root_password"]:
            server_params['password'] = self.module.params["default_root_password"]
            server_params['root_password'] = self.module.params["default_root_password"]
        else:
            self.module.fail_json(changed=False,
                                  msg=("Fail! Please add root_password or set default_root_password "
                                       "for {0}").format(server['address']))
        if 'role' in server and server["role"]:
            server_params['role'] = server['role']
        else:
            server_params['role'] = ['storage']
        server_params['management_internal_ip'] = server['address']
        server_params.update(server_default)
        response = self.oceanstor.check_connection(server_params)
        if response['result']['code'] != '0':
            self.module.fail_json(changed=False,
                                  msg="check node {0} {1} connection failed".format(server["address"], response))
        for role in server_params["role"]:
            if role not in ['management', 'storage', 'compute']:
                self.module.fail_json(changed=False, msg=("check role choice not management/storage/compute  {0} "
                                                          "connection failed").format(server["address"]))

        return server_params

    def add_node(self):
        """Add Storage node."""
        manager_servers = []
        storage_servers = []
        server_default = dict(cabinet='1', authentication_mode='password', user_name='root')
        for server in self.module.params["servers"]:
            server_params = self._refactoring_param_for_add_node(server,server_default)
            if "management" in server_params["role"]:
                manager_servers.append(server_params)
            elif "storage" in server_params["role"]:
                storage_servers.append(server_params)

        if manager_servers:
            response = self.oceanstor.add_storage_servers_with_fsm(manager_servers)
            if str(response['result']['code']) != "0":
                self.module.fail_json(msg=("Add OceanStor storage Node which include manager role failed."
                                           " Description:{0}").format(response['result']['description']),
                                      changed=True, errorCode=response['result']['code'])
        if storage_servers:
            response = self.oceanstor.add_storage_servers(storage_servers)
            if str(response['result']['code']) != "0":
                self.module.fail_json(msg=("Add OceanStor storage Node failed. "
                                           "Description:{0}").format(response['result']['description']),
                                      changed=True, errorCode=response['result']['code'])
        self.module.exit_json(msg="Add OceanStor storage Node complete", changed=True)

    def check_add_storage_status(self):
        """Check Add Storage node status."""
        param = self.module.params['servers']
        server_ip_list = []
        for server in param:
            server_ip_list.append(server['address'])
        response = self.oceanstor.get_server_info()
        if str(response['result']['code']) == '0':
            server_list = response['data']
            for server in server_list:
                if server['management_internal_ip'] in server_ip_list and server['action_phase'] != 2:
                    self.module.exit_json(msg=("Interface for {0} executing").format(server['management_internal_ip']),
                                          status='waiting', response='{0}'.format(response))
            self.module.exit_json(msg='Add OceanStor Storage node Success', status='success',
                                  response='{0}'.format(response))
        else:
            self.module.fail_json(msg=('Add OceanStor Storage node fail {0} {1}'
                                       ).format(response['result']['code'], response['result']['description']),
                                  status='fail')

    def check_status(self):
        """Check add storage node status."""
        service_type = self.module.params["service_type"]

        response = self.oceanstor.deploy_service_task(service_type)

        if str(response['result']['code']) == '0':
            status = response['data']['task_status']
            self.module.warn("Deploy service task status {0}".format(status))
            self.module.exit_json(status=status, changed=True)
        else:
            self.module.warn("Deploy service task have Error {0}".format(response['result']['description']))
            self.module.exit_json(status='error', changed=False)

    def install_node(self):
        """Install OceanStor storage node."""
        response = self.oceanstor.get_server_info()
        servers = response["data"]
        server_param = []
        service_type = self.module.params['service_type']
        if service_type == 'agent':
            for server in servers:
                if server['action_phase'] == 2:
                    server_param.append(server['management_internal_ip'])
        else:
            for server in servers:
                server_param.append(server['management_internal_ip'])
        self.module.warn('{0}'.format(server_param))

        response = self.oceanstor.deploy_service(server_param, service_type=service_type)
        self.module.warn('{0}'.format(response))

        self.module.exit_json(msg="Install OceanStor storage Node complete",
                                  changed=True)

    def get_token(self):
        """Get OceanStor storage auth token."""
        token = self.oceanstor.get_token()

        self.module.exit_json(token=token, changed=True)

    def update(self):
        step = self.module.params["step"]

        if step == "get_token":
            self.get_token()

        elif step == "add_node":
            self.add_node()

        elif step == "check_add_storage_status":
            self.check_add_storage_status()

        elif step == "install_node":
            self.install_node()

        elif step == "check_status":
            self.check_status()


def main():
    settings = HuaweiOceanStorAddStorage()
    settings.update()


if __name__ == '__main__':
    main()
