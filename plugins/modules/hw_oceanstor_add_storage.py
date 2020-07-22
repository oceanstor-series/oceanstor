#!/usr/bin/python

# (c) 2020, huawei, Inc
from ansible.module_utils.basic import AnsibleModule
from oceanstor.oceanstor_add_storage import OceanStorStorage

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
                               service_type=dict(type="str", default="agent", choices=["agent", "all"]),
                               step=dict(type="str", default="check_status",
                                         choices=["get_token", "add_node", "check_status", "install_node"]))

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

    def add_node(self):
        """Add Storage node."""
        # step 1: check storage connection
        manager_servers = []
        storage_servers = []
        for server in self.module.params["servers"]:
            response = self.oceanstor.check_connection(server)
            if response['result']['code'] != '0':
                self.module.fail_json(changed=False, msg="check node {0} "
                                      "connection failed".format(server))
            if "management" in server["role"]:
                manager_servers.append(server)
            elif "storage" in server["role"]:
                storage_servers.append(server)
        # step 2: add storage node which include manager role
        self.oceanstor.add_storage_servers_with_fsm(manager_servers)
        # step 3: add storage node
        self.oceanstor.add_storage_servers(storage_servers)

        self.module.exit_json(msg="Add OceanStor storage Node complete",
                              changed=True)

    def check_status(self):
        """Check add storage node status."""
        service_type = self.module.params["service_type"]

        response = self.oceanstor.deploy_service_task(service_type)

        status = response['data']['task_status']

        self.module.warn("Deploy service task status {0}".format(status))

        self.module.exit_json(status=status, changed=True)

    def install_node(self):
        """Install OceanStor storage node."""
        response = self.oceanstor.get_server_info()
        servers = response["data"]
        server_param = []

        for server in servers:
            server_param.append(server['management_internal_ip'])
        self.oceanstor.deploy_service(server_param, service_type="all")

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

        elif step == "install_node":
            self.install_node()

        elif step == "check_status":
            self.check_status()


def main():
    settings = HuaweiOceanStorAddStorage()
    settings.update()


if __name__ == '__main__':
    main()
