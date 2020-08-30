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
                               default_root_password=dict(type="str", default='', no_log=True),
                               service_type=dict(type="str", default="agent", choices=["agent", "all"]),
                               step=dict(type="str", default="check_status",
                                         choices=["get_token", "add_node", "check_add_storage_status",
                                                  "check_status", "install_node", "install_compute",
                                                  "add_compute", "remove_node", "check_node_in_cluster"]))

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

    def _refactoring_param_for_add_node(self, server, server_default, default_role="storage"):
        """check node connection，refactoring the param
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
        if server.get('user_name') and server.get('password'):
            server_params['password'] = server['password']
            server_params['user_name'] = server['user_name']
        if 'role' in server and server["role"]:
            server_params['role'] = server['role']
        else:
            server_params['role'] = [default_role]
        server_params['management_internal_ip'] = server['address']
        server_params.update(server_default)
        response = self.oceanstor.check_connection(server_params)
        status = 1
        if response['result']['code'] != '0':
            status = 0
            self.module.fail_json(msg=("check node {0} connection failed. Description: "
                                       "{1}").format(server["address"], response['result']['description']),
                                  status='fail')

        for role in server_params["role"]:
            if role not in ['management', 'storage', 'compute']:
                self.module.fail_json(changed=False, msg=("check role choice not management/storage/compute  "
                                                          "{0}").format(server["address"]))

        return status, server_params

    def _get_server_list(self):
        """get server which in cluster"""
        response = self.oceanstor.get_server_info()
        node_list = list()
        if str(response['result']['code']) == '0':
            server_list = response['data']
            for server in server_list:
                if 0 < server['action_phase'] <= 12:
                    node_list.append(server['management_internal_ip'])
            return node_list
        else:
            self.module.fail_json(msg=('Select  OceanStor Storage node list fail {0} {1}'
                                       ).format(response['result']['code'], response['result']['description']),
                                  status='fail')

    def add_node(self):
        """Add Storage node."""
        manager_servers = []
        storage_servers = []
        server_default = dict(cabinet='1', authentication_mode='password', user_name='root')
        node_servers = []
        node_list = self._get_server_list()
        for server in self.module.params["servers"]:
            if server['address'] in node_list:
                self.module.warn("Check node: {0} , have in the Cluster.".format(server["address"]))
                continue
            status, server_params = self._refactoring_param_for_add_node(server, server_default, default_role="storage")
            if status and "management" in server_params["role"]:
                manager_servers.append(server_params)
            elif status and "storage" in server_params["role"] or "compute" in server_params["role"]:
                storage_servers.append(server_params)

        if manager_servers:
            response = self.oceanstor.add_storage_servers_with_fsm(manager_servers)
            if str(response['result']['code']) != "0":
                self.module.fail_json(msg=("Add OceanStor storage Node which include manager role failed."
                                           " Description:{0}").format(response['result']['description']),
                                      changed=True, errorCode=response['result']['code'])
            for server in response['data']['server_list']:
                node_servers.append(server['ip'])

        if storage_servers:
            response = self.oceanstor.add_storage_servers(storage_servers)
            if str(response['result']['code']) != "0":
                self.module.fail_json(msg=("Add OceanStor storage Node failed. "
                                           "Description:{0}").format(response['result']['description']),
                                      changed=False, errorCode=response['result']['code'])
            for server in response['data']['server_list']:
                node_servers.append(server['ip'])

        self.module.exit_json(msg="Add OceanStor storage Node complete.Server list:{0}".format('; '.join(node_servers)),
                              changed=True, trytimes=50 * len(node_servers))

    def add_compute(self):
        """Add compute node."""
        storage_servers = []
        server_default = dict(cabinet='1', authentication_mode='password', user_name='root')
        node_servers = []
        node_list = self._get_server_list()
        for server in self.module.params["servers"]:
            if server['address'] in node_list:
                self.module.warn("Check node: {0} , have in the Cluster.".format(server["address"]))
                continue
            status, server_params = self._refactoring_param_for_add_node(server, server_default, default_role="compute")
            if status and len(server_params["role"]) == 1 and "compute" in server_params["role"]:
                storage_servers.append(server_params)

        if storage_servers:
            response = self.oceanstor.add_storage_servers(storage_servers)
            if str(response['result']['code']) != "0":
                self.module.fail_json(msg=("Add OceanStor compute Node failed. "
                                           "Description:{0}").format(response['result']['description']),
                                      changed=False, errorCode=response['result']['code'])
            for server in response['data']['server_list']:
                node_servers.append(server['ip'])
        self.module.exit_json(msg="Add OceanStor compute Node complete.Server list:{0}".format('; '.join(node_servers)),
                              changed=True, params=node_servers, trytimes=50 * len(node_servers))

    def _refactoring_server_info(self, servers, server_list):
        """refactoring server info"""
        storage_servers = []
        nodes = []
        msg = []
        for server in servers:
            node_info, storage_server, msg = self._find_server_in_list(server, server_list, msg)
            nodes.append(node_info)
            storage_servers.append(storage_server)

        if msg:
            self.module.fail_json(msg="Remove OceanStor storage Node failed. {0}.".format('. '.join(msg)),
                                  changed=False, status='fail')

        return storage_servers, nodes

    @staticmethod
    def _find_server_in_list(server, server_list, msg):
        """find server in server_list"""
        flag = 1
        node_info = dict()
        storage_server = dict
        for server_info in server_list:
            if server['address'] == server_info['management_ip']:
                flag = 0
                if server_info['usage']:
                    msg.append(server['address'] + ' Services is existent')
                else:
                    node_info = dict(userName='root', authentication_mode='password')
                    node_info['serial_number'] = server_info['serial_number']
                    node_info['root_password'] = server['root_password']
                    node_info['password'] = server['root_password']
                    node_info['role'] = server_info['role']
                    node_info['management_ip'] = server_info['management_ip']
                    node_info['management_internal_ip'] = server_info['management_ip']
                    node_info['id'] = server_info['id']
                    node_info['cabinet'] = server_info['cabinet']

                    storage_server = dict(user_name='root')
                    storage_server['management_ip'] = server['address']
                    storage_server['password'] = server['root_password']
                break
        if flag:
            msg.append(server['address'] + ' is not in cluster')

        return node_info, storage_server, msg

    def remove_node(self):
        """Remove storage node."""
        servers = self.module.params["servers"]
        if not len(servers):
            self.module.fail_json(msg="Please add servers you want to remove first.",
                                  changed=False, status='fail')
        response = self.oceanstor.get_cluster_info()
        if str(response['result']['code']) != '0':
            self.module.exit_json(msg=("Remove OceanStor storage Node fail.Query cluster node information "
                                       "fail.{0}").format(response['result']['description']),
                                  changed=False, status='fail')
        server_list = response['data']
        storage_servers, nodes = self._refactoring_server_info(servers, server_list)
        response = self.oceanstor.connection_validity(nodes)
        if str(response['result']['code']) != '0':
            self.module.fail_json(msg=("Remove OceanStor storage Node failed.Nodes authenticate fail."
                                       "{0}.").format(response['result']['description']),
                                  changed=False, status='fail')
        flag = 0
        msg = []
        for server in response['data']['successful_nodes']:
            msg.append(server['management_ip'] + ' authenticate success')
        for server in response['data']['failed_nodes']:
            flag = 1
            msg.append(server['management_ip'] + ' authenticate fail.{0}'.format(server['description']))
        if flag:
            self.module.fail_json(msg=("Remove OceanStor storage Node failed.Some nodes authenticate "
                                       "faile. {0}.").format('. '.join(msg)),
                                  changed=False, status='fail')

        response = self.oceanstor.remove_storage_servers(storage_servers)

        if str(response['result']['code']) == '0':
            for server in response['data']['successful_nodes']:
                msg.append(server['management_ip'] + ' remove success')
            for server in response['data']['failed_nodes']:
                msg.append(server['management_ip'] + ' remove fail.{0}'.format(server['description']))
            self.module.exit_json(msg="Remove OceanStor storage Node success.{0}.".format('. '.join(msg)),
                                  changed=True, status='success')
        else:
            for server in response['data']['successful_nodes']:
                msg.append(server['management_ip'] + ' remove success')
            for server in response['data']['failed_nodes']:
                msg.append(server['management_ip'] + ' remove fail.{0}'.format(server['description']))
            self.module.fail_json(msg="Remove OceanStor storage Node failed. {0}.".format('. '.join(msg)),
                                  changed=False, status='fail')

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
                if server['management_internal_ip'] in server_ip_list and server['action_phase'] < 2:
                    self.module.exit_json(msg=("Interface for {0} executing").format(server['management_internal_ip']),
                                          status='waiting')
            self.module.exit_json(msg='Add OceanStor Storage node Success', status='success')
        else:
            self.module.exit_json(msg=('Check Add OceanStor Storage node fail {0} {1}'
                                       ).format(response['result']['code'], response['result']['description']),
                                  status='fail')

    def check_node_in_cluster(self):
        """Check node whether in cluster"""
        server_list = self.module.params['servers']
        node_list = self._get_server_list()
        back_server = []
        for server in server_list:
            if server['address'] in node_list:
                self.module.warn("{0} have in cluster".format(server['address']))
            else:
                back_server.append(server)
        if back_server:
            self.module.exit_json(change=False, status='success', servers=back_server)
        else:
            self.module.exit_json(change=False, status='fail', msg='All the node are in cluster', servers=back_server)

    def check_status(self):
        """Check add storage node status."""
        service_type = self.module.params["service_type"]

        response = self.oceanstor.deploy_service_task(service_type)

        if str(response['result']['code']) == '0':
            status = response['data']['task_status']
            server_result = response['data']['server_result']
            msg = []
            msg.append("Deploy service task status {0}".format(status))
            for server in server_result:
                msg.append(server["management_internal_ip"] + " " + server["sub_task_status"] +
                           " percent:" + str(server["percent"]))
            self.module.warn("{0}".format("; ".join(msg)))
            self.module.exit_json(status=status, changed=True, msg="{0}".format("; ".join(msg)))
        else:
            self.module.warn("Deploy service task have Error {0}".format(response['result']['description']))
            self.module.exit_json(status='failure', changed=False)

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
                if server['action_phase'] != 12:
                    server_param.append(server['management_internal_ip'])

        if not len(server_param):
            self.module.fail_json(msg="Install Oceanstor storage Node fail. There are no server need install.",
                                  changed=False, status='fail')

        response = self.oceanstor.deploy_service(server_param, service_type=service_type)

        if str(response['result']['code']) == '0':
            self.module.exit_json(msg="Install OceanStor storage Node complete",
                                  changed=True, status='success', trytimes=len(server_param) * 50)
        else:
            self.module.fail_json(msg="Install OceanStor storage Node "
                                      "fail.{0}".format(response['result']['description']),
                                  changed=False, status='fail')

    def install_compute(self):
        """Install OceanStor compute node."""
        response = self.oceanstor.get_server_info()
        servers = response["data"]
        server_param = []
        service_type = self.module.params['service_type']
        param = []
        for server in self.module.params['servers']:
            param.append(server['address'])

        for server in servers:
            if server['action_phase'] == 7 and server['management_internal_ip'] in param:
                server_param.append(server['management_internal_ip'])

        self.module.warn("{0}".format(servers))
        self.module.warn("{0}".format(param))
        self.module.warn('{0}'.format(server_param))

        response = self.oceanstor.deploy_service(server_param, service_type=service_type)

        if str(response['result']['code']) == '0':
            self.module.exit_json(msg="Install OceanStor storage Node complete",
                                  changed=True)
        else:
            self.module.fail_json(msg="Install OceanStor storage Node "
                                      "fail.{0}".format(response['result']['description']),
                                  changed=False)

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

        elif step == "install_compute":
            self.install_compute()

        elif step == "add_compute":
            self.add_compute()

        elif step == "remove_node":
            self.remove_node()

        elif step == "check_node_in_cluster":
            self.check_node_in_cluster()


def main():
    settings = HuaweiOceanStorAddStorage()
    settings.update()


if __name__ == '__main__':
    main()
